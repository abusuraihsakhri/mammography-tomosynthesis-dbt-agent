"""Regression tests for security, CSV parsing, and both API entry points."""
import csv
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from agents.api import app
from agents.base import SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from cli import main as core_cli_main, parse_csv_boolean as core_parse_boolean
from dbt_sentinel.cli import main as sentinel_cli_main, parse_csv_boolean as sentinel_parse_boolean
from dbt_sentinel.engine import FrontierDomainEngine
from dbt_sentinel.server import create_app

@pytest.mark.parametrize("parser", [core_parse_boolean, sentinel_parse_boolean])
def test_csv_boolean_parsing(parser):
    for value in ["False", "false", "0", "NO", ""]:
        assert parser(value) is False
    for value in ["True", "true", "1", "YES"]:
        assert parser(value) is True
    for value in ["maybe", "2"]:
        with pytest.raises(ValueError):
            parser(value)

@pytest.mark.parametrize("entry", [core_cli_main, sentinel_cli_main])
def test_batch_false_flag_does_not_trigger_critical(entry, tmp_path):
    source = tmp_path / "data.csv"
    target = tmp_path / "output.csv"
    source.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n"
        "DEMO-1,SYNTH-1,10,2,False,NOMINAL\n"
        "DEMO-2,SYNTH-2,10,2,True,NOMINAL\n",
        encoding="utf-8",
    )
    assert entry(["batch", "-i", str(source), "-o", str(target)]) == 0
    with target.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    if entry is core_cli_main:
        assert rows[0]["overall_urgency"] == "ROUTINE"
        assert rows[1]["overall_urgency"] == "CRITICAL_STAT_PANIC"
    else:
        assert rows[0]["overall_status"] == "NOMINAL_OPTIMAL"
        assert rows[1]["overall_status"] == "CRITICAL_INTERVENTION_REQUIRED"

@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_values_rejected(invalid):
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="S1", target_identifier="SYNTH", primary_metric=invalid)
    with pytest.raises(ValueError, match="finite"):
        FrontierDomainEngine.evaluate_primary_parameter(invalid)
    with pytest.raises(ValueError, match="finite"):
        FrontierDomainEngine.evaluate_secondary_kinetics(invalid, False)

def test_phi_in_attribute_values_rejected():
    supervisor = SystemSupervisor()
    payload = SystemTaskPayload(
        task_id="S1", target_identifier="SYNTH", primary_metric=1,
        attributes={"unsafe": "MRN-123456"}
    )
    with pytest.raises(SecurityException):
        supervisor.process_task(payload)

def test_http_input_validation_and_browser_asset_routes():
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    page = client.get("/")
    assert page.status_code == 200
    assert "Not for clinical use" in page.text
    assert client.get("/app.mjs").status_code == 200
    assert client.get("/logic.mjs").status_code == 200
    data = {
        "task_id": "HTTP-TEST", "target_identifier": "SYNTH-TEST",
        "primary_metric": 26, "secondary_metric": 2, "status_descriptor": "NOMINAL"
    }
    ok = client.post("/api/audit", json=data)
    assert ok.status_code == 200
    assert ok.json()["total_alerts"] == 1
    blocked = client.post("/api/audit", json={**data, "attributes": {"unsafe": "MRN-123456"}})
    assert blocked.status_code == 422
    invalid = client.post("/api/audit", json={**data, "primary_metric": "NaN"})
    assert invalid.status_code == 422

def test_audit_metadata_protected(monkeypatch):
    client = TestClient(app)
    monkeypatch.delenv("AUDIT_READ_TOKEN", raising=False)
    assert client.get("/api/audit/logs").status_code == 503
    monkeypatch.setenv("AUDIT_READ_TOKEN", "unit-test-read-token")
    assert client.get("/api/audit/logs").status_code == 403
    response = client.get("/api/audit/logs", headers={"X-Audit-Token": "unit-test-read-token"})
    assert response.status_code == 200
    assert response.json()["verified"] is True

def test_secondary_server_still_works():
    secondary = create_app()
    assert secondary is not None
    client = TestClient(secondary)
    assert client.get("/health").status_code == 200
    result = client.post("/api/audit", json={
        "task_id": "TEST", "target_identifier": "SYNTH", "primary_metric": 10,
        "secondary_metric": 2, "status_descriptor": "NOMINAL", "is_critical_flag": False
    })
    assert result.status_code == 200
    assert result.json()["overall_status"] == "NOMINAL_OPTIMAL"
