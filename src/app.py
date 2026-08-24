"""
Streamlit Demo - 展示三种Agent的对比
"""

import streamlit as st
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import NoMemoryAgent, FullMemoryAgent, GatedMemoryAgent
from utils import Config


# 页面配置
st.set_page_config(
    page_title="Memory Gate Agent Demo",
    page_icon="🧠",
    layout="wide",
)

# 标题
st.title("🧠 Memory Gate Agent Demo")
st.markdown("**面向安全与效用平衡的LLM Agent长期记忆门控机制研究**")

# 侧边栏
with st.sidebar:
    st.header("配置")

    # 加载配置
    config = Config.load()

    # 模型选择
    model = st.selectbox(
        "选择模型",
        ["mimo-v2.5-pro", "mimo-v2-pro", "mimo-v2-flash"],
        index=0,
    )

    # 温度
    temperature = st.slider("温度", 0.0, 1.0, 0.0)

    # 记忆数量
    max_memories = st.slider("最大记忆数", 1, 10, 5)

    # 安全阈值
    safety_threshold = st.slider("安全阈值", 0.0, 1.0, 0.7)

    # 效用阈值
    utility_threshold = st.slider("效用阈值", 0.0, 1.0, 0.5)

# 初始化Session State
if "agents" not in st.session_state:
    st.session_state.agents = {
        "无记忆 (基线)": NoMemoryAgent(
            model_name=model,
            api_base=config.mimo.api_base,
            api_key=config.mimo.api_key,
            temperature=temperature,
        ),
        "全量记忆 (传统RAG)": FullMemoryAgent(
            model_name=model,
            api_base=config.mimo.api_base,
            api_key=config.mimo.api_key,
            temperature=temperature,
        ),
        "门控记忆 (创新)": GatedMemoryAgent(
            model_name=model,
            api_base=config.mimo.api_base,
            api_key=config.mimo.api_key,
            temperature=temperature,
        ),
    }

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "memories" not in st.session_state:
    st.session_state.memories = []

# 添加记忆
st.header("📝 添加记忆")
col1, col2 = st.columns(2)

with col1:
    new_memory = st.text_area("输入记忆内容", height=100)

with col2:
    memory_type = st.selectbox("记忆类型", ["episodic", "semantic", "procedural"])
    if st.button("添加记忆"):
        if new_memory:
            for agent in st.session_state.agents.values():
                agent.add_memory(new_memory, {"type": memory_type})
            st.session_state.memories.append(new_memory)
            st.success("记忆已添加！")

# 显示记忆
if st.session_state.memories:
    st.header("📚 已有记忆")
    for i, memory in enumerate(st.session_state.memories):
        st.text(f"{i+1}. {memory}")

# 聊天界面
st.header("💬 对话")

# 显示聊天历史
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("请输入您的问题"):
    # 显示用户消息
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 获取三个Agent的回答
    st.header("🤖 Agent回答对比")

    for agent_name, agent in st.session_state.agents.items():
        with st.expander(agent_name, expanded=True):
            with st.spinner("思考中..."):
                response = agent.invoke(
                    prompt,
                    top_k=max_memories,
                )

            # 显示回答
            st.markdown(response.content)

            # 显示元数据
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("使用记忆", "是" if response.used_memory else "否")
            with col2:
                st.metric("记忆数量", len(response.memory_ids))
            with col3:
                if response.token_usage:
                    total = response.token_usage.get("total_tokens", 0)
                    st.metric("Token使用", total)

            # 显示门控决策（如果是门控Agent）
            if "门控" in agent_name and response.metadata.get("gate_decision"):
                gate = response.metadata["gate_decision"]
                st.json(gate)

    # 添加到聊天历史
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": "已获取三个Agent的回答",
    })

# 底部说明
st.markdown("---")
st.markdown("""
**项目说明：**
- **无记忆Agent (基线)**：每次查询都从头开始，不使用任何历史记忆
- **全量记忆Agent (传统RAG)**：每次都检索所有历史记忆，不进行任何过滤
- **门控记忆Agent (创新)**：自动判断该不该用记忆，在安全和效用之间找最优平衡
""")
