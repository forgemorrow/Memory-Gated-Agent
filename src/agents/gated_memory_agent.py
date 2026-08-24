"""
Gated Memory Agent - 门控记忆Agent（我们的创新）
自动判断该不该用记忆，在安全和效用之间找最优平衡
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base_agent import BaseAgent, AgentResponse


class GateDecision(BaseModel):
    """门控决策"""
    should_use_memory: bool = Field(description="是否应该使用记忆")
    confidence: float = Field(description="置信度 0-1")
    reason: str = Field(description="决策原因")
    safety_score: float = Field(description="安全分数 0-1")
    utility_score: float = Field(description="效用分数 0-1")


class GatedMemoryAgent(BaseAgent):
    """门控记忆Agent（创新点）"""

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

    def _gate_check(
        self,
        query: str,
        memories: List[Dict[str, Any]],
    ) -> GateDecision:
        """
        门控检查：判断是否应该使用记忆

        Args:
            query: 用户查询
            memories: 候选记忆列表

        Returns:
            GateDecision: 门控决策
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = self._get_llm()

        # 构建门控Prompt
        memory_texts = "\n".join(
            f"- {m['content']}" for m in memories[:5]  # 最多检查5条
        )

        gate_prompt = f"""你是一个记忆安全评估专家。请判断以下查询是否应该使用历史记忆。

用户查询：{query}

候选记忆：
{memory_texts}

请从以下两个维度评估：

1. **安全性**（0-1分）：
   - 记忆是否包含敏感信息（隐私、密码、个人数据）
   - 记忆是否可能被滥用
   - 记忆是否过时或矛盾

2. **效用性**（0-1分）：
   - 记忆是否与查询相关
   - 记忆是否能帮助回答问题
   - 记忆是否准确可靠

请以JSON格式返回：
{{
    "should_use_memory": true/false,
    "confidence": 0.0-1.0,
    "reason": "决策原因",
    "safety_score": 0.0-1.0,
    "utility_score": 0.0-1.0
}}"""

        messages = [
            SystemMessage(content="你是一个记忆安全评估专家。请严格按照JSON格式返回评估结果。"),
            HumanMessage(content=gate_prompt),
        ]

        response = llm.invoke(messages)

        # 解析JSON响应
        import json
        try:
            result = json.loads(response.content)
            return GateDecision(**result)
        except Exception:
            # 解析失败，默认不使用记忆
            return GateDecision(
                should_use_memory=False,
                confidence=0.5,
                reason="门控检查解析失败",
                safety_score=0.5,
                utility_score=0.5,
            )

    def invoke(
        self,
        query: str,
        session_id: Optional[str] = None,
        top_k: int = 5,
        **kwargs
    ) -> AgentResponse:
        """
        调用Agent（使用门控记忆）

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
            memories = [
                {"id": doc.metadata.get("id", ""), "content": doc.page_content}
                for doc in results
            ]
            memory_ids = [m["id"] for m in memories]

        # 门控检查
        gate_decision = None
        if memories:
            gate_decision = self._gate_check(query, memories)

        # 根据门控决策决定是否使用记忆
        use_memory = gate_decision and gate_decision.should_use_memory
        memory_context = ""
        used_memory_ids = []

        if use_memory:
            memory_context = "\n\n历史记忆：\n" + "\n".join(
                f"- {m['content']}" for m in memories
            )
            used_memory_ids = memory_ids

        # 构建Prompt
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
            used_memory=use_memory,
            memory_ids=used_memory_ids,
            token_usage={
                "prompt_tokens": response.usage_metadata.get("input_tokens", 0) if response.usage_metadata else 0,
                "completion_tokens": response.usage_metadata.get("output_tokens", 0) if response.usage_metadata else 0,
            },
            metadata={
                "gate_decision": gate_decision.dict() if gate_decision else None,
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
