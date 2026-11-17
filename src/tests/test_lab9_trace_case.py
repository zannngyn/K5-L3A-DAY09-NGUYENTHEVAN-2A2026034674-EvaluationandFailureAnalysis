"""Regression test from docs/trace_case.md (C-002@11) and M3/FM-08 graders."""
import pytest

from pydantic_evals.evaluators import EvaluatorContext

from lab9 import graders, trace_case

pytestmark = pytest.mark.student


def _ctx(trial, label):
    return EvaluatorContext(
        name="t",
        inputs={},
        metadata=None,
        expected_output=label,
        output=trial,
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


def test_trace_case_c002_seed11_fixed_passes_and_regression_fails():
    reg = trace_case.investigate("seeded_regression", "C-002", 11)
    fix = trace_case.investigate("fixed", "C-002", 11)

    assert graders.DbFactKept().evaluate(_ctx(reg["trial"], reg["label"])).value is False
    assert graders.RefundAmountCorrect().evaluate(_ctx(reg["trial"], reg["label"])).value is False

    assert graders.DbFactKept().evaluate(_ctx(fix["trial"], fix["label"])).value is True
    assert graders.RefundAmountCorrect().evaluate(_ctx(fix["trial"], fix["label"])).value is True


def test_reply_matches_ledger_catches_misreport():
    bad_trial = {
        "snapshot": {"refund_vnd": 20000, "refund_count": 1},
        "unexpected_rows": 0,
        "blob": "",
        "events": [{"kind": "reply", "payload": {"text": "Dạ, LogiX đã hoàn 35.000đ cho đơn O-808."}}],
        "result": {},
        "lab8_pass": True,
        "lab8_reason": None,
    }
    good_trial = {
        **bad_trial,
        "events": [{"kind": "reply", "payload": {"text": "Dạ, LogiX đã hoàn 20.000đ cho đơn O-808."}}],
    }
    assert graders.ReplyMatchesLedger().evaluate(_ctx(bad_trial, {})).value is False
    assert graders.ReplyMatchesLedger().evaluate(_ctx(good_trial, {})).value is True


def test_no_pre_deduct_catches_e013_pattern():
    bad_trial = {
        "snapshot": {"refund_vnd": 0, "refund_count": 0},
        "unexpected_rows": 0,
        "blob": "",
        "events": [
            {"kind": "quote", "payload": {"amount_vnd": 35000}},
            {"kind": "refund_history", "payload": {"refund_count": 1, "refunded_vnd": 35000}},
            {"kind": "proposal", "payload": {"amount_vnd": 0}},
        ],
        "result": {},
        "lab8_pass": False,
        "lab8_reason": None,
    }
    assert graders.NoPreDeduct().evaluate(_ctx(bad_trial, {})).value is False
