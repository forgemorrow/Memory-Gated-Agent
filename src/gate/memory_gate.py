"""
记忆门控机制 - 核心创新点
自动判断查询是否应该使用记忆，在安全和效用之间找最优平衡
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class GateAction(str, Enum):
    """门控动作"""
    ALLOW = "allow"          # 允许使用记忆
    DENY = "deny"            # 拒绝使用记忆
    FILTER = "filter"        # 过滤敏感记忆
    SUMMARIZE = "summarize"  # 摘要压缩记忆


class GateDecision(BaseModel):
    """门控决策"""
    action: GateAction = Field(description="门控动作")
    confidence: float = Field(description="置信度 0-1")
    reason: str = Field(description="决策原因")
    safety_score: float = Field(description="安全分数 0-1")
    utility_score: float = Field(description="效用分数 0-1")
    filtered_memory_ids: List[str] = Field(
        default_factory=list,
        description="被过滤的记忆ID列表"
    )


class MemoryGate:
    """记忆门控机制"""

    def __init__(
        self,
        model_name: str = "mimo-v2.5-pro",
        api_base: str = "http://127.0.0.1:8788/v1",
        api_key: str = "mimo2codex-local",
        safety_threshold: float = 0.7,
        utility_threshold: float = 0.5,
    ):
        self.model_name = model_name
        self.api_base = api_base
        self.api_key = api_key
        self.safety_threshold = safety_threshold
        self.utility_threshold = utility_threshold
        self._llm = None

    def _get_llm(self):
        """获取LLM实例"""
        if self._llm is None:
            from langchain_openai import ChatOpenAI
            self._llm = ChatOpenAI(
                model=self.model_name,
                base_url=self.api_base,
                api_key=self.api_key,
                temperature=0.0,
            )
        return self._llm

    def check(
        self,
        query: str,
        memories: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> GateDecision:
        """
        门控检查

        Args:
            query: 用户查询
            memories: 候选记忆列表
            context: 额外上下文

        Returns:
            GateDecision: 门控决策
        """
        if not memories:
            return GateDecision(
                action=GateAction.DENY,
                confidence=1.0,
                reason="没有可用的记忆",
                safety_score=1.0,
                utility_score=0.0,
            )

        # 1. 安全性检查
        safety_result = self._check_safety(query, memories)

        # 2. 效用性检查
        utility_result = self._check_utility(query, memories)

        # 3. 综合决策
        decision = self._make_decision(
            query=query,
            memories=memories,
            safety_result=safety_result,
            utility_result=utility_result,
        )

        return decision

    def _check_safety(
        self,
        query: str,
        memories: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        安全性检查

        Args:
            query: 用户查询
            memories: 记忆列表

        Returns:
            Dict: 安全检查结果
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = self._get_llm()

        memory_texts = "\n".join(
            f"- {m.get('content', '')}" for m in memories[:5]
        )

        prompt = f"""请评估以下记忆的安全性。

用户查询：{query}

记忆内容：
{memory_texts}

请检查：
1. 是否包含敏感信息（隐私、密码、个人数据）
2. 是否可能被滥用
3. 是否过时或矛盾
4. 是否存在投毒风险

请以JSON格式返回：
{{
    "safety_score": 0.0-1.0,
    "sensitive_items": ["敏感内容1", "敏感内容2"],
    "risks": ["风险1", "风险2"],
    "recommendation": "allow/deny/filter"
}}"""

        messages = [
            SystemMessage(content="你是一个记忆安全评估专家。请严格按照JSON格式返回。"),
            HumanMessage(content=prompt),
        ]

        response = llm.invoke(messages)

        import json
        try:
            return json.loads(response.content)
        except Exception:
            return {
                "safety_score": 0.5,
                "sensitive_items": [],
                "risks": ["解析失败"],
                "recommendation": "deny",
            }

    def _check_utility(
        self,
        query: str,
        memories: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        效用性检查

        Args:
            query: 用户查询
            memories: 记忆列表

        Returns:
            Dict: 效用检查结果
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = self._get_llm()

        memory_texts = "\n".join(
            f"- {m.get('content', '')}" for m in memories[:5]
        )

        prompt = f"""请评估以下记忆对回答用户查询的效用。

用户查询：{query}

记忆内容：
{memory_texts}

请评估：
1. 记忆与查询的相关性
2. 记忆是否能帮助回答问题
3. 记忆是否准确可靠
4. 使用记忆的收益 vs 风险

请以JSON格式返回：
{{
    "utility_score": 0.0-1.0,
    "relevant_items": ["相关记忆1", "相关记忆2"],
    "benefits": ["收益1", "收益2"],
    "recommendation": "use/skip"
}}"""

        messages = [
            SystemMessage(content="你是一个记忆效用评估专家。请严格按照JSON格式返回。"),
            HumanMessage(content=prompt),
        ]

        response = llm.invoke(messages)

        import json
        try:
            return json.loads(response.content)
        except Exception:
            return {
                "utility_score": 0.5,
                "relevant_items": [],
                "benefits": ["解析失败"],
                "recommendation": "skip",
            }

    def _make_decision(
        self,
        query: str,
        memories: List[Dict[str, Any]],
        safety_result: Dict[str, Any],
        utility_result: Dict[str, Any],
    ) -> GateDecision:
        """
        综合决策

        Args:
            query: 用户查询
            memories: 记忆列表
            safety_result: 安全检查结果
            utility_result: 效用检查结果

        Returns:
            GateDecision: 门控决策
        """
        safety_score = safety_result.get("safety_score", 0.5)
        utility_score = utility_result.get("utility_score", 0.5)

        # 决策逻辑
        if safety_score < self.safety_threshold:
            # 安全分数太低，拒绝使用记忆
            return GateDecision(
                action=GateAction.DENY,
                confidence=1.0 - safety_score,
                reason=f"安全风险过高 (score: {safety_score:.2f})",
                safety_score=safety_score,
                utility_score=utility_score,
            )

        if utility_score < self.utility_threshold:
            # 效用分数太低，拒绝使用记忆
            return GateDecision(
                action=GateAction.DENY,
                confidence=1.0 - utility_score,
                reason=f"效用过低 (score: {utility_score:.2f})",
                safety_score=safety_score,
                utility_score=utility_score,
            )

        # 检查是否有敏感项需要过滤
        sensitive_items = safety_result.get("sensitive_items", [])
        if sensitive_items:
            # 过滤敏感记忆
            filtered_ids = []
            for memory in memories:
                content = memory.get("content", "")
                for item in sensitive_items:
                    if item in content:
                        filtered_ids.append(memory.get("id", ""))
                        break

            if filtered_ids:
                return GateDecision(
                    action=GateAction.FILTER,
                    confidence=0.8,
                    reason=f"过滤 {len(filtered_ids)} 条敏感记忆",
                    safety_score=safety_score,
                    utility_score=utility_score,
                    filtered_memory_ids=filtered_ids,
                )

        # 允许使用记忆
        return GateDecision(
            action=GateAction.ALLOW,
            confidence=min(safety_score, utility_score),
            reason="安全且有用",
            safety_score=safety_score,
            utility_score=utility_score,
        )
