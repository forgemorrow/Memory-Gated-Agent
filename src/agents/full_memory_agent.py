"""
Full Memory Agent - 全量记忆Agent（传统RAG）
每次都检索所有历史记忆，不进行任何过滤
"""

from typing import Optional, List, Dict, Any
from .base_agent import BaseAgent, AgentResponse


class FullMemoryAgent(BaseAgent):
    """全量记忆Agent（传统RAG）"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._llm = None
        self._vectorstore = None
        self._memories: List[Dict[str, Any]] = []

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

    def _get_vectorstore(self):
        """获取向量存储"""
        if self._vectorstore is None:
            import chromadb
            from langchain_chroma import Chroma
            from langchain_community.embeddings import HuggingFaceEmbeddings

            client = chromadb.Client()
            collection = client.get_or_create_collection("memories")
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

    def invoke(
        self,
        query: str,
        session_id: Optional[str] = None,
        top_k: int = 5,
        **kwargs
    ) -> AgentResponse:
        """
        调用Agent（使用全量记忆）

        Args:
            query: 用户查询
            session_id: 会话ID
            top_k: 检索的记忆数量

        Returns:
            AgentResponse: Agent响应
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = self._get_llm()
        vectorstore = self._get_vectorstore()

        # 检索相关记忆
        memories = []
        memory_ids = []
        if self._memories:
            results = vectorstore.similarity_search(query, k=top_k)
            memories = [doc.page_content for doc in results]
            memory_ids = [doc.metadata.get("id", "") for doc in results]

        # 构建Prompt
        memory_context = ""
        if memories:
            memory_context = "\n\n历史记忆：\n" + "\n".join(
                f"- {m}" for m in memories
            )

        system_prompt = f"""你是一个有帮助的AI助手。请根据以下信息回答用户的问题。

{memory_context}

如果历史记忆中有相关信息，请基于记忆回答。如果没有，请直接回答。"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query),
        ]

        response = llm.invoke(messages)

        return AgentResponse(
            content=response.content,
            used_memory=len(memories) > 0,
            memory_ids=memory_ids,
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
        """
        添加记忆

        Args:
            content: 记忆内容
            metadata: 元数据

        Returns:
            str: 记忆ID
        """
        import uuid

        memory_id = str(uuid.uuid4())
        memory_metadata = metadata or {}
        memory_metadata["id"] = memory_id

        self._memories.append({
            "id": memory_id,
            "content": content,
            "metadata": memory_metadata,
        })

        # 添加到向量存储
        vectorstore = self._get_vectorstore()
        vectorstore.add_texts(
            texts=[content],
            metadatas=[memory_metadata],
            ids=[memory_id],
        )

        return memory_id

    def clear_memory(self, session_id: Optional[str] = None) -> None:
        """
        清除记忆

        Args:
            session_id: 会话ID（None表示清除所有）
        """
        self._memories.clear()
        self._vectorstore = None

    def get_memory_count(self) -> int:
        """获取记忆数量"""
        return len(self._memories)
