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

from typing import cast

from superlinked.framework.common.dag.exception import ParentCountException
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.dag.persistence_params import PersistenceParams
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.storage.persistence_type import PersistenceType


class IndexNode(Node[Vector], HasLength):
    def __init__(
        self,
        parents: set[Node[Vector]],
    ) -> None:
        super().__init__(
            list(self.__validate_parents(parents)),
            persistence_params=PersistenceParams(
                persist_evaluation_result=True, persistence_type=PersistenceType.VECTOR
            ),
        )
        self.__length = cast(HasLength, self.parents[0]).length

    def __validate_parents(self, parents: set[Node[Vector]]) -> set[Node[Vector]]:
        if len(parents) == 0:
            raise ParentCountException(
                f"{self.class_name} must have at least 1 parent."
            )
        return parents

    @property
    def length(self) -> int:
        return self.__length
