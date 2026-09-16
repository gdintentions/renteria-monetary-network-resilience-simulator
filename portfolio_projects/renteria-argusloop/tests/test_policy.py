from argusloop.models import Action, Risk
from argusloop.policy import authorize


def action(**overrides):
    data = {"reasoning": "test", "action": "wait", "confidence": 0.9}
    data.update(overrides)
    return Action(**data)


def test_dry_run_blocks_mutation():
    result = authorize(action(action="click", x=50, y=50), "medium", "dry-run")
    assert not result.allowed


def test_sensitive_typing_blocked():
    result = authorize(
        action(action="type", text="enter password here", risk=Risk.medium), "medium", "live"
    )
    assert not result.allowed


def test_critical_never_allowed():
    assert not authorize(action(risk=Risk.critical), "critical", "live").allowed


def test_low_risk_wait_allowed_live():
    assert authorize(action(), "low", "live").allowed
