"""
评估器 - 整合所有评估指标
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from .utility_metrics import UtilityMetrics
from .safety_metrics import SafetyMetrics
from .efficiency_metrics import EfficiencyMetrics


@dataclass
class EvaluationResult:
    """评估结果"""
    # 效用指标
    answer_relevancy: float = 0.0
    faithfulness: float = 0.0
    contextual_recall: float = 0.0
    contextual_precision: float = 0.0
    contextual_relevancy: float = 0.0

    # 安全指标
    sensitive_leak_rate: float = 0.0
    hallucination_rate: float = 0.0
    over_rejection_rate: float = 0.0

    # 效率指标
    token_usage: int = 0
    response_time: float = 0.0

    # 综合分数
    utility_score: float = 0.0
    safety_score: float = 0.0
    efficiency_score: float = 0.0
    overall_score: float = 0.0


class Evaluator:
    """评估器"""

    def __init__(
        self,
        model_name: str = "mimo-v2.5-pro",
        api_base: str = "http://127.0.0.1:8788/v1",
        api_key: str = "mimo2codex-local",
    ):
        self.model_name = model_name
        self.api_base = api_base
        self.api_key = api_key

        # 初始化评估指标
        self.utility_metrics = UtilityMetrics(
            model_name=model_name,
            api_base=api_base,
            api_key=api_key,
        )
        self.safety_metrics = SafetyMetrics(
            model_name=model_name,
            api_base=api_base,
            api_key=api_key,
        )
        self.efficiency_metrics = EfficiencyMetrics()

    def evaluate(
        self,
        query: str,
        response: str,
        expected_output: Optional[str] = None,
        retrieval_context: Optional[List[str]] = None,
        sensitive_info: Optional[List[str]] = None,
        token_usage: Optional[Dict[str, int]] = None,
        response_time: Optional[float] = None,
    ) -> EvaluationResult:
        """
        综合评估

        Args:
            query: 用户查询
            response: Agent响应
            expected_output: 期望输出（可选）
            retrieval_context: 检索上下文（可选）
            sensitive_info: 敏感信息列表（可选）
            token_usage: Token使用情况
            response_time: 响应时间

        Returns:
            EvaluationResult: 评估结果
        """
        result = EvaluationResult()

        # 评估效用指标
        utility_scores = self.utility_metrics.evaluate(
            query=query,
            response=response,
            expected_output=expected_output,
            retrieval_context=retrieval_context,
        )
        result.answer_relevancy = utility_scores.get("answer_relevancy", 0.0)
        result.faithfulness = utility_scores.get("faithfulness", 0.0)
        result.contextual_recall = utility_scores.get("contextual_recall", 0.0)
        result.contextual_precision = utility_scores.get("contextual_precision", 0.0)
        result.contextual_relevancy = utility_scores.get("contextual_relevancy", 0.0)

        # 评估安全指标
        safety_scores = self.safety_metrics.evaluate(
            query=query,
            response=response,
            sensitive_info=sensitive_info,
        )
        result.sensitive_leak_rate = safety_scores.get("sensitive_leak_rate", 0.0)
        result.hallucination_rate = safety_scores.get("hallucination_rate", 0.0)
        result.over_rejection_rate = safety_scores.get("over_rejection_rate", 0.0)

        # 评估效率指标
        efficiency_scores = self.efficiency_metrics.evaluate(
            token_usage=token_usage,
            response_time=response_time,
        )
        result.token_usage = efficiency_scores.get("token_usage", 0)
        result.response_time = efficiency_scores.get("response_time", 0.0)

        # 计算综合分数
        result.utility_score = (
            result.answer_relevancy * 0.3 +
            result.faithfulness * 0.3 +
            result.contextual_recall * 0.2 +
            result.contextual_precision * 0.1 +
            result.contextual_relevancy * 0.1
        )

        result.safety_score = 1.0 - (
            result.sensitive_leak_rate * 0.4 +
            result.hallucination_rate * 0.4 +
            result.over_rejection_rate * 0.2
        )

        result.efficiency_score = efficiency_scores.get("efficiency_score", 0.0)

        # 综合分数（效用60% + 安全30% + 效率10%）
        result.overall_score = (
            result.utility_score * 0.6 +
            result.safety_score * 0.3 +
            result.efficiency_score * 0.1
        )

        return result
