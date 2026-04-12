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

import os
import sqlite3
from uuid import uuid4
from tasks import get_random_task, get_task_by_difficulty, Task
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import SqlAction, SqlObservation
except ImportError:
    from models import SqlAction, SqlObservation


DB_PATH = os.environ.get(
    "SQL_ENV_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sql_env.db")
)

# Set TASK_DIFFICULTY=easy/medium/hard in .env, or leave unset for random
TASK_DIFFICULTY = os.environ.get("TASK_DIFFICULTY", None)


class SqlEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count = 0
        self._conn: sqlite3.Connection | None = None
        self._task: Task | None = None
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
        self._conn.row_factory = sqlite3.Row

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
                columns = [desc[0] for desc in cursor.description]
                rows = [list(row) for row in cursor.fetchall()]
                return {
                    "columns": columns,
                    "rows": rows,
                    "rowcount": len(rows),
                    "error": None,
                }
            else:
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

    def _reward(self, result: dict, query: str) -> float:
        if result["error"]:
            return 0.0

        score = 0.0
        q = query.lower()

        score += 0.3

        if result["rowcount"] > 0:
            score += 0.2

        if "join" in q:
            score += 0.2

        if any(fn in q for fn in ["count(", "sum(", "avg(", "max(", "min("]):
            score += 0.2

        if "where" in q:
            score += 0.1

        if self._task and result["columns"]:
            matched = sum(
                1 for c in self._task.expected_columns
                if any(c in col.lower() or col.lower() in c
                    for col in result["columns"])
            )
            score += 0.2 * (matched / len(self._task.expected_columns))

        # ← run grader if available
        if self._task and self._task.grader and result["rows"]:
            grader_score = self._task.grader(result["rows"])
            score = min(score + (grader_score * 0.2), 1.0)

        return min(score, 1.0)

    # ------------------------------------------------------------------
    # Environment interface
    # ------------------------------------------------------------------

    def reset(self) -> SqlObservation:
        self._task = self._pick_task()
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count += 1
        self._connect()

        print(f"[ENV] Task: {self._task.id} | Difficulty: {self._task.difficulty}", flush=True)

        return SqlObservation(
            echoed_message=f"Task: {self._task.description}",
            message_length=0,
            metadata={
                "db_path": DB_PATH,
                "task_id": self._task.id,
                "task_difficulty": self._task.difficulty,
            },
        )

    def step(self, action: SqlAction) -> SqlObservation:
        self._state.step_count += 1

        query = action.query.strip()
        result = self._execute(query)

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
                "reward": self._reward(result, query),
            },
        )

    @property
    def state(self) -> State:
        return self._state