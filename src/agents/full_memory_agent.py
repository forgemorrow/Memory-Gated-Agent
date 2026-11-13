"""
Full Memory Agent - 全量记忆Agent（传统RAG）
每次都检索所有历史记忆，不进行任何过滤
"""

from typing import Optional
from .base_agent import AgentResponse, VectorMemoryAgent


class FullMemoryAgent(VectorMemoryAgent):
    """全量记忆Agent（传统RAG）"""

    def invoke(
        self,
        query: str,
        session_id: Optional[str] = None,
        top_k: int = 5,
        **kwargs,
    ) -> AgentResponse:
        """调用Agent（使用全量记忆）"""
        llm = self._get_llm()
        memories, memory_ids = self._retrieve_memories(query, top_k=top_k)

        system_prompt = self._format_memory_system_prompt(memories)
        messages = self._build_chat_messages(system_prompt, query)
        response = llm.invoke(messages)

        return AgentResponse(
            content=response.content,
            used_memory=bool(memories),
            memory_ids=memory_ids,
            token_usage=self._extract_token_usage(response),
        )
