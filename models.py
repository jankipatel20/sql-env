# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the Sql Env Environment.

The sql_env environment is a simple test environment that echoes back messages.
"""


from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from openenv.core.env_server import Action, Observation, State

@dataclass
class SQLAction(Action):
    query: str                    # The SQL query the agent submits
    action_type: str = "execute"  # "execute" | "submit"

@dataclass
class SQLObservation(Observation):
    output: str                          # Human-readable result or error
    rows: List[Dict[str, Any]] = field(default_factory=list)  # Query result rows
    error: Optional[str] = None          # SQL error message if any
    execution_time_ms: float = 0.0       # Query execution time
    task_description: str = ""           # What the agent needs to solve
    schema_info: str = ""                # Available tables and columns
    success: bool = True
    done: bool = False
    reward: float = 0.0

@dataclass
class SQLState(State):
    episode_id: str = ""
    task_id: str = ""
    task_difficulty: str = "easy"
    step_count: int = 0
    max_steps: int = 15
    current_score: float = 0.0
    submitted: bool = False
    last_query: str = ""
    query_history: List[str] = field(default_factory=list)
