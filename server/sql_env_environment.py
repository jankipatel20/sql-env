# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Sql Env Environment Implementation.

A simple test environment that echoes back messages sent to it.
Perfect for testing HTTP server infrastructure.
"""

from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import SqlAction, SqlObservation
except ImportError:
    from models import SqlAction, SqlObservation

class SqlEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count = 0

    def reset(self) -> SqlObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count += 1

        return SqlObservation(
            echoed_message="Sql Env environment ready!",
            message_length=0,
            metadata={}
        )

    def step(self, action: SqlAction) -> SqlObservation:
        self._state.step_count += 1

        message = action.query
        length = len(message)

        return SqlObservation(
            echoed_message=message,
            message_length=length,
            metadata={}
        )

    @property
    def state(self) -> State:
        return self._state