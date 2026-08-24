"""
记忆管理器 - 管理记忆的存储、检索、更新、删除
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class Memory:
    """记忆单元"""

    def __init__(
        self,
        content: str,
        memory_type: str = "episodic",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = str(uuid.uuid4())
        self.content = content
        self.memory_type = memory_type  # episodic, semantic, procedural
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.access_count = 0
        self.importance_score = 0.5

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "access_count": self.access_count,
            "importance_score": self.importance_score,
        }


class MemoryManager:
    """记忆管理器"""

    def __init__(
        self,
        model_name: str = "mimo-v2.5-pro",
        api_base: str = "http://127.0.0.1:8788/v1",
        api_key: str = "mimo2codex-local",
    ):
        self.model_name = model_name
        self.api_base = api_base
        self.api_key = api_key
        self._memories: Dict[str, Memory] = {}
        self._vectorstore = None

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

    def add(
        self,
        content: str,
        memory_type: str = "episodic",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        添加记忆

        Args:
            content: 记忆内容
            memory_type: 记忆类型 (episodic, semantic, procedural)
            metadata: 元数据

        Returns:
            str: 记忆ID
        """
        memory = Memory(
            content=content,
            memory_type=memory_type,
            metadata=metadata,
        )

        self._memories[memory.id] = memory

        # 添加到向量存储
        vectorstore = self._get_vectorstore()
        vectorstore.add_texts(
            texts=[content],
            metadatas=[{
                "id": memory.id,
                "memory_type": memory_type,
                **(metadata or {}),
            }],
            ids=[memory.id],
        )

        return memory.id

    def search(
        self,
        query: str,
        top_k: int = 5,
        memory_type: Optional[str] = None,
    ) -> List[Memory]:
        """
        搜索记忆

        Args:
            query: 查询
            top_k: 返回数量
            memory_type: 记忆类型过滤

        Returns:
            List[Memory]: 记忆列表
        """
        vectorstore = self._get_vectorstore()

        # 构建过滤条件
        filter_dict = {}
        if memory_type:
            filter_dict["memory_type"] = memory_type

        # 搜索
        results = vectorstore.similarity_search(
            query,
            k=top_k,
            filter=filter_dict if filter_dict else None,
        )

        # 转换为Memory对象
        memories = []
        for doc in results:
            memory_id = doc.metadata.get("id", "")
            if memory_id in self._memories:
                memory = self._memories[memory_id]
                memory.access_count += 1
                memories.append(memory)

        return memories

    def get(self, memory_id: str) -> Optional[Memory]:
        """
        获取记忆

        Args:
            memory_id: 记忆ID

        Returns:
            Optional[Memory]: 记忆对象
        """
        return self._memories.get(memory_id)

    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        更新记忆

        Args:
            memory_id: 记忆ID
            content: 新内容
            metadata: 新元数据

        Returns:
            bool: 是否成功
        """
        if memory_id not in self._memories:
            return False

        memory = self._memories[memory_id]

        if content:
            memory.content = content
        if metadata:
            memory.metadata.update(metadata)

        memory.updated_at = datetime.now()

        return True

    def delete(self, memory_id: str) -> bool:
        """
        删除记忆

        Args:
            memory_id: 记忆ID

        Returns:
            bool: 是否成功
        """
        if memory_id not in self._memories:
            return False

        del self._memories[memory_id]
        return True

    def clear(self) -> None:
        """清除所有记忆"""
        self._memories.clear()
        self._vectorstore = None

    def count(self) -> int:
        """获取记忆数量"""
        return len(self._memories)

    def list_all(self) -> List[Memory]:
        """列出所有记忆"""
        return list(self._memories.values())
