"""
Base Agent - Agent基类
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """Agent响应"""
    content: str = Field(description="回答内容")
    used_memory: bool = Field(description="是否使用了记忆")
    memory_ids: List[str] = Field(default_factory=list, description="使用的记忆ID列表")
    token_usage: Dict[str, int] = Field(default_factory=dict, description="Token使用情况")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")


class BaseAgent(ABC):
    """Agent基类"""

    def __init__(
        self,
        model_name: str = "mimo-v2.5-pro",
        api_base: str = "http://127.0.0.1:8788/v1",
        api_key: str = "mimo2codex-local",
        temperature: float = 0.0,
        max_tokens: int = 2000,
    ):
        self.model_name = model_name
        self.api_base = api_base
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def invoke(
        self,
        query: str,
        session_id: Optional[str] = None,
        **kwargs
    ) -> AgentResponse:
        """
        调用Agent

        Args:
            query: 用户查询
            session_id: 会话ID（用于记忆检索）

        Returns:
            AgentResponse: Agent响应
        """
        pass

    @abstractmethod
    def add_memory(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        添加记忆

        Args:
            content: 记忆内容
            metadata: 元数据

        Returns:
            str: 记忆ID
        """
        pass

    @abstractmethod
    def clear_memory(self, session_id: Optional[str] = None) -> None:
        """
        清除记忆

        Args:
            session_id: 会话ID（None表示清除所有）
        """
        pass

    def get_memory_count(self) -> int:
        """获取记忆数量"""
        return 0
