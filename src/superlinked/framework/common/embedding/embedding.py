# Copyright 2024 Superlinked, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import NotImplementedException

# EmbeddingInputType
EIT = TypeVar("EIT")


class Embedding(Generic[EIT], ABC):

    @abstractmethod
    def embed(self, input_: EIT, context: ExecutionContext) -> Vector:
        pass

    def inverse_embed(self, vector: Vector, context: ExecutionContext) -> EIT:
        raise NotImplementedException

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__ if self.__dict__ else ''})"
