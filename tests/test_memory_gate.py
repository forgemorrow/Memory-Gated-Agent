import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from agents.full_memory_agent import FullMemoryAgent  # noqa: E402
from agents.gated_memory_agent import GatedMemoryAgent  # noqa: E402
from agents.no_memory_agent import NoMemoryAgent  # noqa: E402
from evaluation.efficiency_metrics import EfficiencyMetrics  # noqa: E402
from evaluation.evaluator import Evaluator  # noqa: E402
from evaluation.safety_metrics import SafetyMetrics  # noqa: E402
from gate.memory_gate import GateAction, GateDecision, MemoryGate  # noqa: E402
from utils.config import Config  # noqa: E402


def test_memory_gate_empty_memories():
    gate = MemoryGate()
    decision = gate.check("hello", [])
    assert decision.action == GateAction.DENY
    assert decision.safety_score == 1.0
    assert decision.utility_score == 0.0


def test_memory_gate_denies_low_safety():
    gate = MemoryGate(safety_threshold=0.7, utility_threshold=0.5)
    memories = [{"id": "m1", "content": "User API key is sk-test-123"}]
    with (
        patch.object(gate, "_check_safety", return_value={"safety_score": 0.2, "sensitive_items": ["sk-test-123"]}),
        patch.object(gate, "_check_utility", return_value={"utility_score": 0.9}),
    ):
        decision = gate.check("What is my key?", memories)
    assert decision.action == GateAction.DENY
    assert decision.safety_score == 0.2


def test_memory_gate_denies_low_utility():
    gate = MemoryGate(safety_threshold=0.7, utility_threshold=0.6)
    memories = [{"id": "m1", "content": "Unrelated trivia"}]
    with (
        patch.object(gate, "_check_safety", return_value={"safety_score": 0.95, "sensitive_items": []}),
        patch.object(gate, "_check_utility", return_value={"utility_score": 0.3}),
    ):
        decision = gate.check("Explain Python asyncio", memories)
    assert decision.action == GateAction.DENY
    assert decision.utility_score == 0.3


def test_memory_gate_filters_sensitive_items():
    gate = MemoryGate(safety_threshold=0.7, utility_threshold=0.5)
    memories = [
        {"id": "m1", "content": "User prefers concise code reviews"},
        {"id": "m2", "content": "User password is password123"},
    ]
    with (
        patch.object(gate, "_check_safety", return_value={"safety_score": 0.8, "sensitive_items": ["password123"]}),
        patch.object(gate, "_check_utility", return_value={"utility_score": 0.85}),
    ):
        decision = gate.check("What are my preferences?", memories)
    assert decision.action == GateAction.FILTER
    assert decision.filtered_memory_ids == ["m2"]


def test_memory_gate_allows_safe_and_useful():
    gate = MemoryGate(safety_threshold=0.7, utility_threshold=0.5)
    memories = [{"id": "m1", "content": "User uses Python 3.11 and pytest"}]
    with (
        patch.object(gate, "_check_safety", return_value={"safety_score": 0.95, "sensitive_items": []}),
        patch.object(gate, "_check_utility", return_value={"utility_score": 0.9}),
    ):
        decision = gate.check("Which test runner should I use?", memories)
    assert decision.action == GateAction.ALLOW
    assert decision.confidence == 0.9


def test_parse_json_payload_handles_fences():
    raw = '```json\n{"safety_score": 0.88, "sensitive_items": []}\n```'
    parsed = MemoryGate._parse_json_payload(raw)
    assert parsed["safety_score"] == 0.88
    assert MemoryGate._parse_json_payload("not json") is None


def test_safety_and_efficiency_metrics_and_config(monkeypatch):
    sm = SafetyMetrics()
    assert sm._check_sensitive_leak("Here is password123", ["password123", "other"]) == 0.5
    assert sm._check_sensitive_leak("I cannot share that.", ["password123"]) == 0.0

    em = EfficiencyMetrics()
    res = em.evaluate(token_usage={"total_tokens": 500}, response_time=2.0)
    assert res["efficiency_score"] == 1.0

    monkeypatch.setenv("SAFETY_THRESHOLD", "0.85")
    cfg = Config.load()
    assert cfg.evaluation.safety_threshold == 0.85


def _install_fake_langchain_messages(monkeypatch):
    class _FakeMsg:
        def __init__(self, content: str):
            self.content = content

    fake_mod = SimpleNamespace(SystemMessage=_FakeMsg, HumanMessage=_FakeMsg)
    monkeypatch.setitem(sys.modules, "langchain_core.messages", fake_mod)


class _RecordingLLM:
    def __init__(self, reply: str = "ok"):
        self.reply = reply
        self.recorded_messages = []

    def invoke(self, messages):
        self.recorded_messages.append(messages)
        return SimpleNamespace(
            content=self.reply,
            usage_metadata={"input_tokens": 10, "output_tokens": 5},
        )


def test_no_memory_and_full_memory_agents(monkeypatch):
    _install_fake_langchain_messages(monkeypatch)

    no_mem = NoMemoryAgent()
    no_mem._llm = _RecordingLLM("plain answer")
    assert no_mem.add_memory("secret") == ""
    resp = no_mem.invoke("Hi")
    assert resp.content == "plain answer"
    assert resp.used_memory is False
    assert resp.memory_ids == []
    assert resp.token_usage == {"prompt_tokens": 10, "completion_tokens": 5}

    full_mem = FullMemoryAgent()
    llm = _RecordingLLM("memory answer")
    full_mem._llm = llm
    memories = [{"id": "m1", "content": "Prefers pytest"}]
    with patch.object(full_mem, "_retrieve_memories", return_value=(memories, ["m1"])):
        resp_full = full_mem.invoke("Which test tool?")
    assert resp_full.used_memory is True
    assert resp_full.memory_ids == ["m1"]
    assert "Prefers pytest" in llm.recorded_messages[0][0].content


def test_gated_memory_agent_decisions_and_empty_memories(monkeypatch):
    _install_fake_langchain_messages(monkeypatch)

    agent = GatedMemoryAgent(safety_threshold=0.7, utility_threshold=0.5)
    llm = _RecordingLLM("gated answer")
    agent._llm = llm

    # Empty retrieval should cleanly set used_memory=False without calling gate.check
    with (
        patch.object(agent, "_retrieve_memories", return_value=([], [])),
        patch.object(agent, "_gate_check") as mock_gate,
    ):
        empty_resp = agent.invoke("Hi")
    assert empty_resp.used_memory is False
    assert empty_resp.memory_ids == []
    assert empty_resp.metadata["gate_decision"] is None
    mock_gate.assert_not_called()

    candidates = [
        {"id": "m1", "content": "Uses Python 3.11"},
        {"id": "m2", "content": "API key is sk-secret"},
    ]

    # FILTER drops m2 while injecting m1
    filter_decision = GateDecision(
        action=GateAction.FILTER,
        reason="Removed sensitive item",
        safety_score=0.8,
        utility_score=0.85,
        filtered_memory_ids=["m2"],
        confidence=0.8,
    )
    with (
        patch.object(agent, "_retrieve_memories", return_value=(candidates, ["m1", "m2"])),
        patch.object(agent, "_gate_check", return_value=filter_decision),
    ):
        filtered_resp = agent.invoke("Setup instructions?")
    assert filtered_resp.used_memory is True
    assert filtered_resp.memory_ids == ["m1"]
    assert "Uses Python 3.11" in llm.recorded_messages[-1][0].content
    assert "sk-secret" not in llm.recorded_messages[-1][0].content
    assert filtered_resp.metadata["gate_decision"]["action"] == "filter"

    # DENY suppresses all memories
    deny_decision = GateDecision(
        action=GateAction.DENY,
        reason="Unsafe",
        safety_score=0.2,
        utility_score=0.8,
        confidence=0.9,
    )
    with (
        patch.object(agent, "_retrieve_memories", return_value=(candidates, ["m1", "m2"])),
        patch.object(agent, "_gate_check", return_value=deny_decision),
    ):
        denied_resp = agent.invoke("Reveal secrets")
    assert denied_resp.used_memory is False
    assert denied_resp.memory_ids == []
    assert "Uses Python 3.11" not in llm.recorded_messages[-1][0].content

    # ALLOW keeps all candidates and _gate_check syncs updated slider thresholds
    agent.safety_threshold = 0.92
    agent.utility_threshold = 0.65
    with (
        patch.object(agent.gate, "_check_safety", return_value={"safety_score": 0.95, "sensitive_items": []}),
        patch.object(agent.gate, "_check_utility", return_value={"utility_score": 0.9}),
        patch.object(agent, "_retrieve_memories", return_value=(candidates, ["m1", "m2"])),
    ):
        allowed_resp = agent.invoke("All good")
    assert agent.gate.safety_threshold == 0.92
    assert agent.gate.utility_threshold == 0.65
    assert allowed_resp.used_memory is True
    assert allowed_resp.memory_ids == ["m1", "m2"]


def test_evaluator_weighted_scores():
    evaluator = Evaluator()
    with (
        patch.object(
            evaluator.utility_metrics,
            "evaluate",
            return_value={
                "answer_relevancy": 0.8,
                "faithfulness": 0.9,
                "contextual_recall": 0.7,
                "contextual_precision": 0.6,
                "contextual_relevancy": 0.5,
            },
        ),
        patch.object(
            evaluator.safety_metrics,
            "evaluate",
            return_value={
                "sensitive_leak_rate": 0.1,
                "hallucination_rate": 0.0,
                "over_rejection_rate": 0.2,
            },
        ),
    ):
        res = evaluator.evaluate(
            query="q",
            response="a",
            token_usage={"total_tokens": 500},
            response_time=2.0,
        )

    expected_utility = 0.8 * 0.3 + 0.9 * 0.3 + 0.7 * 0.2 + 0.6 * 0.1 + 0.5 * 0.1
    expected_safety = 1.0 - (0.1 * 0.4 + 0.0 * 0.4 + 0.2 * 0.2)
    expected_eff = 1.0
    expected_overall = expected_utility * 0.6 + expected_safety * 0.3 + expected_eff * 0.1

    assert res.utility_score == pytest.approx(expected_utility)
    assert res.safety_score == pytest.approx(expected_safety)
    assert res.efficiency_score == pytest.approx(expected_eff)
    assert res.overall_score == pytest.approx(expected_overall)
