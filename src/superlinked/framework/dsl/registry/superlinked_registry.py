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

from superlinked.framework.dsl.data_loader.data_loader import DataLoader
from superlinked.framework.dsl.executor.executor import Executor
from superlinked.framework.dsl.registry.exception import DuplicateElementException


class SuperlinkedRegistry:
    __executors: set[Executor] = set()
    __data_loaders: set[DataLoader] = set()

    @staticmethod
    def register(*items: Executor | DataLoader) -> None:
        for item in items:
            SuperlinkedRegistry.__check_for_duplicates(item)
            match item:
                case Executor():
                    SuperlinkedRegistry.__executors.add(item)
                case DataLoader():
                    SuperlinkedRegistry.__data_loaders.add(item)
                case _:
                    raise ValueError(
                        f"Invalid type {type(item)}! Only Executor and DataLoader allowed."
                    )

    @staticmethod
    def __check_for_duplicates(item: Executor | DataLoader) -> None:
        if item in SuperlinkedRegistry.__executors | SuperlinkedRegistry.__data_loaders:
            raise DuplicateElementException(f"{item} already registered!")

    @staticmethod
    def get_executors() -> frozenset[Executor]:
        return frozenset(SuperlinkedRegistry.__executors)

    @staticmethod
    def get_data_loaders() -> frozenset[DataLoader]:
        return frozenset(SuperlinkedRegistry.__data_loaders)
