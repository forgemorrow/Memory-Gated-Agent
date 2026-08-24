"""
No Memory Agent - 无记忆Agent（基线）
每次查询都从头开始，不使用任何历史记忆
"""

from typing import Optional, List, Dict, Any
from .base_agent import BaseAgent, AgentResponse


class NoMemoryAgent(BaseAgent):
    """无记忆Agent（基线）"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._llm = None

    def _get_llm(self):
        """获取LLM实例"""
        if self._llm is None:
            from langchain_openai import ChatOpenAI
            self._llm = ChatOpenAI(
                model=self.model_name,
                base_url=self.api_base,
                api_key=self.api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        return self._llm

    def invoke(
        self,
        query: str,
        session_id: Optional[str] = None,
        **kwargs
    ) -> AgentResponse:
        """
        调用Agent（不使用记忆）

        Args:
            query: 用户查询
            session_id: 会话ID（忽略）

        Returns:
            AgentResponse: Agent响应
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = self._get_llm()

        messages = [
            SystemMessage(content="你是一个有帮助的AI助手。请直接回答用户的问题。"),
            HumanMessage(content=query),
        ]

        response = llm.invoke(messages)

        return AgentResponse(
            content=response.content,
            used_memory=False,
            memory_ids=[],
            token_usage={
                "prompt_tokens": response.usage_metadata.get("input_tokens", 0) if response.usage_metadata else 0,
                "completion_tokens": response.usage_metadata.get("output_tokens", 0) if response.usage_metadata else 0,
            },
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

    def get_memory_count(self) -> int:
        """无记忆Agent没有记忆"""
        return 0
