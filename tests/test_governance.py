from src.governance import scrub_record, guardrail_check
import src.configuracao as conf
import src.governance as gov


def test_scrub_record_removes_sensitive_field():
    conf.PSEUDONYMIZE_ENABLED = False
    gov.PSEUDONYMIZE_ENABLED = False
    rec = {"nu_idade_n": 42, "last7_cases": 1}
    out = scrub_record(rec)
    assert out.get("nu_idade_n") is None


def test_guardrail_check_detects_invalid_percent():
    m = {"mortality_rate_30d": 5.0, "last7_cases": 10}
    violations = list(guardrail_check(m))
    assert any("mortality_rate_30d" in v for v in violations)
