import sys
from pathlib import Path
from unittest.mock import patch

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from evaluation.efficiency_metrics import EfficiencyMetrics  # noqa: E402
from evaluation.safety_metrics import SafetyMetrics  # noqa: E402
from gate.memory_gate import GateAction, MemoryGate  # noqa: E402
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
