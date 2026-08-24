# Memory Gate Agent

**面向安全与效用平衡的LLM Agent长期记忆门控机制研究**

## 项目目标

研究如何设计记忆门控机制，在安全和效用之间找到最优平衡。

## 技术栈

- **Agent框架**: LangChain + LangGraph
- **向量数据库**: ChromaDB
- **评估**: DeepEval (5个指标) + 自定义安全指标
- **LLM**: MiMo API (mimo-v2.5-pro)
- **前端**: Streamlit (Demo演示)

## 实验设计

三个Agent对比：
- **Agent A**: 无记忆（每次从头开始，基线）
- **Agent B**: 全量记忆（每次都检索所有历史，传统RAG）
- **Agent C**: 门控记忆（我们的创新 — 自动判断该不该用记忆）

## 评估指标

- **效用指标**: 准确率、忠实度、相关性（DeepEval）
- **安全指标**: 敏感信息泄露率、幻觉率、过度拒绝率
- **效率指标**: token消耗、响应时间

## 数据集

- LongMemEval-S (500题，最常用，结果可对比)
- LoCoMo (4955测试行，长对话记忆)
- 中文版：翻译或自建

## 项目结构

```
memory-gate-agent/
├── src/
│   ├── agents/          # Agent实现
│   ├── memory/          # 记忆管理
│   ├── evaluation/      # 评估模块
│   ├── gate/            # 门控机制
│   └── utils/           # 工具函数
├── configs/             # 配置文件
├── data/                # 数据集
├── notebooks/           # Jupyter notebooks
├── tests/               # 测试
└── docs/                # 文档
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行实验
python src/main.py

# 启动Demo
streamlit run src/app.py
```

## 论文结构

1. 引言 — Agent发展、记忆重要性、安全与效用矛盾
2. 相关工作 — 记忆架构/记忆安全/记忆评估
3. 方法 — 问题定义/记忆门控设计/安全-效用权衡算法
4. 实验 — 设置/主实验/消融实验/案例分析
5. 讨论
6. 结论

## 目标发表

EI会议（IJCNN / ICONIP / PRICAI / NLPCC）

## 作者

[Your Name]

## 日期

2026年6月
