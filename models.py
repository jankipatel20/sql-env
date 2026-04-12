# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the Sql Env Environment.

The sql_env environment is a simple test environment that echoes back messages.
"""


from typing import Dict, Any
from openenv.core.env_server import Action, Observation, State


class SqlAction(Action):
    query: str


class SqlObservation(Observation):
    echoed_message: str
    message_length: int
    metadata: Dict[str, Any] = {}