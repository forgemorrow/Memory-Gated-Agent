"""
Base Agent - Agent基类与向量记忆公共基类
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
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
        self._llm = None

    def _get_llm(self):
        """获取或懒加载 LLM 实例"""
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

    @staticmethod
    def _build_chat_messages(system_prompt: str, query: str) -> List[Any]:
        """构建 LangChain 对话消息列表"""
        from langchain_core.messages import HumanMessage, SystemMessage

        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query),
        ]

    @staticmethod
    def _extract_token_usage(response: Any) -> Dict[str, int]:
        """从 LangChain 响应对象安全提取 Token 统计"""
        usage = getattr(response, "usage_metadata", None) or {}
        return {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
        }

    @abstractmethod
    def invoke(
        self,
        query: str,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> AgentResponse:
        """调用Agent"""

    @abstractmethod
    def add_memory(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """添加记忆"""

    @abstractmethod
    def clear_memory(self, session_id: Optional[str] = None) -> None:
        """清除记忆"""

    def get_memory_count(self) -> int:
        """获取记忆数量"""
        return 0


class VectorMemoryAgent(BaseAgent, ABC):
    """带 ChromaDB 向量记忆存储的公共基类"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._vectorstore = None
        self._memories: List[Dict[str, Any]] = []

    def _get_vectorstore(self):
        """获取向量存储"""
        if self._vectorstore is None:
            import chromadb
            from langchain_chroma import Chroma
            from langchain_community.embeddings import HuggingFaceEmbeddings

            client = chromadb.Client()
            client.get_or_create_collection("memories")
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
            )
            self._vectorstore = Chroma(
                client=client,
                collection_name="memories",
                embedding_function=embeddings,
            )
        return self._vectorstore

    def _retrieve_memories(
        self, query: str, top_k: int = 5
    ) -> Tuple[List[Dict[str, str]], List[str]]:
        """检索最相关的候选记忆及其 ID 列表"""
        if not self._memories:
            return [], []
        vectorstore = self._get_vectorstore()
        results = vectorstore.similarity_search(query, k=top_k)
        memories = [
            {"id": doc.metadata.get("id", ""), "content": doc.page_content}
            for doc in results
        ]
        memory_ids = [m["id"] for m in memories]
        return memories, memory_ids

    def add_memory(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """添加记忆并写入向量索引"""
        import uuid

        memory_id = str(uuid.uuid4())
        memory_metadata = dict(metadata or {})
        memory_metadata["id"] = memory_id

        self._memories.append({
            "id": memory_id,
            "content": content,
            "metadata": memory_metadata,
        })

        vectorstore = self._get_vectorstore()
        vectorstore.add_texts(
            texts=[content],
            metadatas=[memory_metadata],
            ids=[memory_id],
        )
        return memory_id

    def clear_memory(self, session_id: Optional[str] = None) -> None:
        """清除本地及向量记忆"""
        self._memories.clear()
        self._vectorstore = None

    def get_memory_count(self) -> int:
        """获取记忆数量"""
        return len(self._memories)

    @staticmethod
    def _format_memory_system_prompt(memories: List[Dict[str, str]]) -> str:
        """将通过检索/门控的记忆拼装为系统提示词"""
        memory_context = ""
        if memories:
            memory_context = "\n\n历史记忆：\n" + "\n".join(
                f"- {m['content']}" for m in memories
            )
        return f"""你是一个有帮助的AI助手。请根据以下信息回答用户的问题。

{memory_context}

如果历史记忆中有相关信息，请基于记忆回答。如果没有，请直接回答。"""
