"""
No Memory Agent - 无记忆Agent（基线）
每次查询都从头开始，不使用任何历史记忆
"""

from typing import Any, Dict, Optional
from .base_agent import AgentResponse, BaseAgent


class NoMemoryAgent(BaseAgent):
    """无记忆Agent（基线）"""

    def invoke(
        self,
        query: str,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> AgentResponse:
        """调用Agent（不使用记忆）"""
        llm = self._get_llm()
        messages = self._build_chat_messages(
            "你是一个有帮助的AI助手。请直接回答用户的问题。",
            query,
        )
        response = llm.invoke(messages)

        return AgentResponse(
            content=response.content,
            used_memory=False,
            memory_ids=[],
            token_usage=self._extract_token_usage(response),
        )

    def add_memory(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """无记忆Agent不存储记忆"""
        return ""

    def clear_memory(self, session_id: Optional[str] = None) -> None:
        """无记忆Agent不需要清除记忆"""
        pass
