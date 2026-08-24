"""
效用指标 - 评估Agent输出的质量
使用DeepEval框架
"""

from typing import Optional, List, Dict, Any


class UtilityMetrics:
    """效用指标"""

    def __init__(
        self,
        model_name: str = "mimo-v2.5-pro",
        api_base: str = "http://127.0.0.1:8788/v1",
        api_key: str = "mimo2codex-local",
    ):
        self.model_name = model_name
        self.api_base = api_base
        self.api_key = api_key

    def evaluate(
        self,
        query: str,
        response: str,
        expected_output: Optional[str] = None,
        retrieval_context: Optional[List[str]] = None,
    ) -> Dict[str, float]:
        """
        评估效用指标

        Args:
            query: 用户查询
            response: Agent响应
            expected_output: 期望输出
            retrieval_context: 检索上下文

        Returns:
            Dict[str, float]: 各项指标分数
        """
        scores = {
            "answer_relevancy": 0.0,
            "faithfulness": 0.0,
            "contextual_recall": 0.0,
            "contextual_precision": 0.0,
            "contextual_relevancy": 0.0,
        }

        try:
            from deepeval.metrics import (
                AnswerRelevancyMetric,
                FaithfulnessMetric,
                ContextualRecallMetric,
                ContextualPrecisionMetric,
                ContextualRelevancyMetric,
            )
            from deepeval.test_case import LLMTestCase

            # 创建测试用例
            test_case = LLMTestCase(
                input=query,
                actual_output=response,
                expected_output=expected_output or response,
                retrieval_context=retrieval_context or [],
            )

            # 评估答案相关性
            relevancy_metric = AnswerRelevancyMetric(
                threshold=0.5,
                model=self.model_name,
            )
            relevancy_metric.measure(test_case)
            scores["answer_relevancy"] = relevancy_metric.score

            # 评估忠实度
            if retrieval_context:
                faithfulness_metric = FaithfulnessMetric(
                    threshold=0.5,
                    model=self.model_name,
                )
                faithfulness_metric.measure(test_case)
                scores["faithfulness"] = faithfulness_metric.score

                # 评估上下文召回率
                recall_metric = ContextualRecallMetric(
                    threshold=0.5,
                    model=self.model_name,
                )
                recall_metric.measure(test_case)
                scores["contextual_recall"] = recall_metric.score

                # 评估上下文精确率
                precision_metric = ContextualPrecisionMetric(
                    threshold=0.5,
                    model=self.model_name,
                )
                precision_metric.measure(test_case)
                scores["contextual_precision"] = precision_metric.score

                # 评估上下文相关性
                relevancy_metric = ContextualRelevancyMetric(
                    threshold=0.5,
                    model=self.model_name,
                )
                relevancy_metric.measure(test_case)
                scores["contextual_relevancy"] = relevancy_metric.score

        except Exception as e:
            print(f"效用指标评估失败: {e}")

        return scores
