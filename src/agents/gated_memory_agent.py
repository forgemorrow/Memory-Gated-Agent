"""
Gated Memory Agent - 门控记忆Agent
在检索与上下文注入之间引入 MemoryGate 安全-效用联合决策
"""

from typing import List, Dict, Any, Optional
from gate.memory_gate import GateAction, GateDecision, MemoryGate
from .base_agent import AgentResponse, VectorMemoryAgent


class GatedMemoryAgent(VectorMemoryAgent):
    """门控记忆Agent"""

    def __init__(
        self,
        safety_threshold: float = 0.7,
        utility_threshold: float = 0.5,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.safety_threshold = safety_threshold
        self.utility_threshold = utility_threshold
        self.gate = MemoryGate(
            model_name=self.model_name,
            api_base=self.api_base,
            api_key=self.api_key,
            safety_threshold=safety_threshold,
            utility_threshold=utility_threshold,
        )

    def _gate_check(
        self,
        query: str,
        memories: List[Dict[str, Any]],
    ) -> GateDecision:
        """使用 MemoryGate 对候选记忆执行安全与效用联合评估"""
        self.gate.safety_threshold = self.safety_threshold
        self.gate.utility_threshold = self.utility_threshold
        return self.gate.check(query, memories)

    def invoke(
        self,
        query: str,
        session_id: Optional[str] = None,
        top_k: int = 5,
        **kwargs,
    ) -> AgentResponse:
        """调用Agent（仅注入通过门控检查的非敏感记忆）"""
        llm = self._get_llm()
        memories, _ = self._retrieve_memories(query, top_k=top_k)

        gate_decision: Optional[GateDecision] = None
        approved_memories: List[Dict[str, str]] = []

        if memories:
            gate_decision = self._gate_check(query, memories)
            if gate_decision.action == GateAction.ALLOW:
                approved_memories = memories
            elif gate_decision.action == GateAction.FILTER:
                blocked = set(gate_decision.filtered_memory_ids)
                approved_memories = [m for m in memories if m["id"] not in blocked]

        use_memory = bool(approved_memories)
        used_memory_ids = [m["id"] for m in approved_memories] if use_memory else []

        system_prompt = self._format_memory_system_prompt(approved_memories)
        messages = self._build_chat_messages(system_prompt, query)
        response = llm.invoke(messages)

        return AgentResponse(
            content=response.content,
            used_memory=use_memory,
            memory_ids=used_memory_ids,
            token_usage=self._extract_token_usage(response),
            metadata={
                "gate_decision": gate_decision.model_dump() if gate_decision else None,
            },
        )
