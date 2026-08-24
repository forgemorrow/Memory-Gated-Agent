"""
效率指标 - 评估Agent的效率
"""

from typing import Optional, Dict, Any


class EfficiencyMetrics:
    """效率指标"""

    def evaluate(
        self,
        token_usage: Optional[Dict[str, int]] = None,
        response_time: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        评估效率指标

        Args:
            token_usage: Token使用情况
            response_time: 响应时间（秒）

        Returns:
            Dict[str, Any]: 各项指标
        """
        result = {
            "token_usage": 0,
            "response_time": 0.0,
            "efficiency_score": 0.0,
        }

        if token_usage:
            total_tokens = token_usage.get("total_tokens", 0)
            result["token_usage"] = total_tokens

        if response_time:
            result["response_time"] = response_time

        # 计算效率分数
        # Token效率：越少越好（假设500 token为基准）
        token_score = 1.0
        if result["token_usage"] > 0:
            token_score = max(0.0, 1.0 - (result["token_usage"] - 500) / 2000)

        # 时间效率：越快越好（假设2秒为基准）
        time_score = 1.0
        if result["response_time"] > 0:
            time_score = max(0.0, 1.0 - (result["response_time"] - 2.0) / 10.0)

        # 综合效率分数（Token 60% + 时间 40%）
        result["efficiency_score"] = token_score * 0.6 + time_score * 0.4

        return result
