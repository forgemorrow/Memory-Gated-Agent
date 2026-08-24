"""
配置管理
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv


class MiMoConfig(BaseModel):
    """MiMo API配置"""
    api_base: str = Field(default="http://127.0.0.1:8788/v1")
    api_key: str = Field(default="mimo2codex-local")
    model: str = Field(default="mimo-v2.5-pro")
    temperature: float = Field(default=0.0)
    max_tokens: int = Field(default=2000)


class ChromaDBConfig(BaseModel):
    """ChromaDB配置"""
    host: str = Field(default="localhost")
    port: int = Field(default=8000)
    persist_directory: str = Field(default="./data/chroma")


class EvaluationConfig(BaseModel):
    """评估配置"""
    safety_threshold: float = Field(default=0.7)
    utility_threshold: float = Field(default=0.5)
    max_memories: int = Field(default=5)


class Config(BaseModel):
    """主配置"""
    mimo: MiMoConfig = Field(default_factory=MiMoConfig)
    chroma: ChromaDBConfig = Field(default_factory=ChromaDBConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)

    @classmethod
    def load(cls, env_file: Optional[str] = None) -> "Config":
        """
        从环境变量加载配置

        Args:
            env_file: .env文件路径

        Returns:
            Config: 配置对象
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        return cls(
            mimo=MiMoConfig(
                api_base=os.getenv("MIMO_API_BASE", "http://127.0.0.1:8788/v1"),
                api_key=os.getenv("MIMO_API_KEY", "mimo2codex-local"),
                model=os.getenv("MIMO_MODEL", "mimo-v2.5-pro"),
                temperature=float(os.getenv("MIMO_TEMPERATURE", "0.0")),
                max_tokens=int(os.getenv("MIMO_MAX_TOKENS", "2000")),
            ),
            chroma=ChromaDBConfig(
                host=os.getenv("CHROMA_HOST", "localhost"),
                port=int(os.getenv("CHROMA_PORT", "8000")),
                persist_directory=os.getenv("CHROMA_PERSIST_DIR", "./data/chroma"),
            ),
            evaluation=EvaluationConfig(
                safety_threshold=float(os.getenv("SAFETY_THRESHOLD", "0.7")),
                utility_threshold=float(os.getenv("UTILITY_THRESHOLD", "0.5")),
                max_memories=int(os.getenv("MAX_MEMORIES", "5")),
            ),
        )
