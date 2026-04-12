# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Sql Env Environment Implementation.

Executes SQL queries against a SQLite database and returns results
as structured observations.
"""

import json
import os
import sqlite3
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import SqlAction, SqlObservation
except ImportError:
    from models import SqlAction, SqlObservation


# Path to the SQLite database file.
# Place your .db file here, or it will be created automatically.
DB_PATH = os.environ.get("SQL_ENV_DB_PATH", "sql_env.db")


class SqlEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count = 0
        self._conn: sqlite3.Connection | None = None
        self._connect()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _connect(self):
        """Open (or reopen) a connection to the SQLite database."""
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
        self._conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row  # enables column-name access

    def _execute(self, query: str) -> dict:
        """
        Execute a SQL query and return a result dict with keys:
          - columns : list[str]
          - rows    : list[list]
          - rowcount: int  (affected rows for INSERT/UPDATE/DELETE)
          - error   : str | None
        """
        try:
            cursor = self._conn.cursor()
            cursor.execute(query)
            self._conn.commit()

            if cursor.description:
                # SELECT (or any query that returns rows)
                columns = [desc[0] for desc in cursor.description]
                rows = [list(row) for row in cursor.fetchall()]
                return {
                    "columns": columns,
                    "rows": rows,
                    "rowcount": len(rows),
                    "error": None,
                }
            else:
                # INSERT / UPDATE / DELETE / CREATE / DROP …
                return {
                    "columns": [],
                    "rows": [],
                    "rowcount": cursor.rowcount,
                    "error": None,
                }
        except sqlite3.Error as e:
            return {
                "columns": [],
                "rows": [],
                "rowcount": 0,
                "error": str(e),
            }

    @staticmethod
    def _reward(result: dict) -> float:
        """Simple reward signal: +1 for success, -1 for error."""
        return -1.0 if result["error"] else 1.0

    # ------------------------------------------------------------------
    # Environment interface
    # ------------------------------------------------------------------

    def reset(self) -> SqlObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count += 1
        self._connect()  # fresh connection each episode

        return SqlObservation(
            echoed_message="Sql Env environment ready!",
            message_length=0,
            metadata={"db_path": DB_PATH},
        )

    def step(self, action: SqlAction) -> SqlObservation:
        self._state.step_count += 1

        query = action.query.strip()
        result = self._execute(query)

        # Build a human-readable summary for echoed_message
        if result["error"]:
            summary = f"ERROR: {result['error']}"
        elif result["columns"]:
            summary = (
                f"{result['rowcount']} row(s) returned. "
                f"Columns: {result['columns']}"
            )
        else:
            summary = f"Query OK. {result['rowcount']} row(s) affected."

        return SqlObservation(
            echoed_message=summary,
            message_length=len(query),
            metadata={
                "query": query,
                "columns": result["columns"],
                "rows": result["rows"],
                "rowcount": result["rowcount"],
                "error": result["error"],
                "reward": self._reward(result),
            },
        )

    @property
    def state(self) -> State:
        return self._state