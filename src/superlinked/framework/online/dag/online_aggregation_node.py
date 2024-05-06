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

from __future__ import annotations

from typing import cast

from beartype.typing import Sequence
from typing_extensions import override

from superlinked.framework.common.dag.aggregation_node import AggregationNode
from superlinked.framework.common.dag.context import ExecutionContext
from superlinked.framework.common.dag.exception import ParentCountException
from superlinked.framework.common.dag.node import Node
from superlinked.framework.common.data_types import Vector
from superlinked.framework.common.exception import (
    MismatchingDimensionException,
    ValidationException,
)
from superlinked.framework.common.interface.has_aggregation import HasAggregation
from superlinked.framework.common.interface.has_length import HasLength
from superlinked.framework.common.space.aggregation import Aggregation
from superlinked.framework.online.dag.default_online_node import DefaultOnlineNode
from superlinked.framework.online.dag.evaluation_result import SingleEvaluationResult
from superlinked.framework.online.dag.online_node import OnlineNode
from superlinked.framework.online.dag.parent_validator import ParentValidationType
from superlinked.framework.online.store_manager.evaluation_result_store_manager import (
    EvaluationResultStoreManager,
)


class OnlineAggregationNode(DefaultOnlineNode[AggregationNode, Vector], HasLength):
    def __init__(
        self,
        node: AggregationNode,
        parents: list[OnlineNode],
        evaluation_result_store_manager: EvaluationResultStoreManager,
    ) -> None:
        super().__init__(
            node,
            parents,
            evaluation_result_store_manager,
            ParentValidationType.AT_LEAST_ONE_PARENT,
        )
        OnlineAggregationNode.__validate_parents(parents)

    @property
    def length(self) -> int:
        return self.node.length

    @classmethod
    def __validate_parents(cls, parents: list[OnlineNode]) -> None:
        length = cast(HasLength, parents[0]).length
        if any(
            parent for parent in parents if cast(HasLength, parent).length != length
        ):
            raise ValidationException(
                f"{cls.__name__} must have parents with the same length."
            )

    @override
    def _evaluate_singles(
        self,
        parent_results: list[dict[OnlineNode, SingleEvaluationResult]],
        context: ExecutionContext,
    ) -> Sequence[Vector | None]:
        return [
            self._evaluate_single(parent_result, context)
            for parent_result in parent_results
        ]

    def _evaluate_single(
        self,
        parent_results: dict[OnlineNode, SingleEvaluationResult],
        context: ExecutionContext,
    ) -> Vector:
        self._check_evaluation_inputs(parent_results)
        weighted_vectors = self._get_weighted_vectors(parent_results)
        return self.__get_aggregation(parent_results).aggregate(
            weighted_vectors, context
        )

    def __get_aggregation(
        self, parent_results: dict[OnlineNode, SingleEvaluationResult]
    ) -> Aggregation:
        aggregations: list[Aggregation] = [
            online_node.node.aggregation
            for online_node in parent_results.keys()
            if isinstance(online_node.node, HasAggregation)
        ]
        if not aggregations:
            raise ValidationException("No Aggregation set.")
        if not all(
            aggregation.normalization == aggregations[0].normalization
            for aggregation in aggregations
        ):
            aggregation_class_names = [
                str(aggregation.__class__) for aggregation in aggregations
            ]
            raise ValidationException(
                f"Cannot aggregate with different Aggregations: {str(aggregation_class_names)}."
            )
        return aggregations[0]

    def _check_evaluation_inputs(
        self,
        parent_results: dict[OnlineNode, SingleEvaluationResult],
    ) -> None:
        invalid_type_result_types = [
            result.__class__.__name__
            for _, result in parent_results.items()
            if not isinstance(result.value, Vector)
        ]
        if any(invalid_type_result_types):
            raise ValidationException(
                f"{self.class_name} can only process `Vector` inputs"
                + f", got {invalid_type_result_types}"
            )
        filtered_parent_results: dict[OnlineNode, SingleEvaluationResult[Vector]] = {
            parent: result
            for parent, result in parent_results.items()
            if not cast(Vector, result.value).is_empty
        }
        if not any(filtered_parent_results.items()):
            raise ParentCountException(
                f"{self.class_name} must have at least 1 parent with valid input."
            )
        invalid_length_results = [
            result
            for _, result in filtered_parent_results.items()
            if result.value.dimension != self.length
        ]
        if any(invalid_length_results):
            raise MismatchingDimensionException(
                f"{self.class_name} can only process inputs having same length"
                + f", got {invalid_length_results[0].value.dimension}"
            )

    def _get_weighted_vectors(
        self, parent_results: dict[OnlineNode, SingleEvaluationResult]
    ) -> list[Vector]:
        node_id_weight_map = {
            weighted_parent.item.node_id: weighted_parent.weight
            for weighted_parent in self.node.weighted_parents
        }
        return [
            result.value * node_id_weight_map[cast(Node, parent.node).node_id]
            for parent, result in cast(
                dict[OnlineNode, SingleEvaluationResult[Vector]], parent_results
            ).items()
            if not cast(Vector, result.value).is_empty
        ]
