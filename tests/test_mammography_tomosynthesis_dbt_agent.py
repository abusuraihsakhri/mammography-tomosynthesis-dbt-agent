"""
Automated Pytest Test Suite for Mammography Tomosynthesis Dbt Agent.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import os
import sys
import warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, AuditTrail, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_phi_guard_redaction():
    """Test that PHI is properly redacted from text."""
    dirty = "Contact patient at 555-123-4567 or MRN-12345"
    redacted = PHIGuard.redact_phi(dirty)
    assert "555-123-4567" not in redacted
    assert "MRN-12345" not in redacted
    assert "[REDACTED_IDENTIFIER]" in redacted


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_audit_trail_ephemeral_key_warning():
    """Test that AuditTrail warns when AUDIT_SECRET_KEY is not set."""
    # Ensure the env var is not set for this test
    original_key = os.environ.pop("AUDIT_SECRET_KEY", None)
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            trail = AuditTrail()
            # Check that a RuntimeWarning was raised about the ephemeral key
            runtime_warnings = [x for x in w if issubclass(x.category, RuntimeWarning)]
            assert len(runtime_warnings) >= 1
            assert "AUDIT_SECRET_KEY" in str(runtime_warnings[0].message)
            # Verify the key starts with "ephemeral-"
            assert trail.secret_key.startswith(b"ephemeral-")
    finally:
        # Restore original env var if it existed
        if original_key is not None:
            os.environ["AUDIT_SECRET_KEY"] = original_key


def test_audit_trail_with_explicit_key():
    """Test that AuditTrail uses explicit key without warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        trail = AuditTrail(secret_key="my-test-key-12345")
        runtime_warnings = [x for x in w if issubclass(x.category, RuntimeWarning)]
        assert len(runtime_warnings) == 0
        assert trail.secret_key == b"my-test-key-12345"


def test_audit_trail_integrity_tampering():
    """Test that AuditTrail detects tampering with the chain."""
    trail = AuditTrail(secret_key="tamper-test-key")
    trail.log("test", "test_tier", "TEST_EVENT", {"data": "value1"})
    trail.log("test", "test_tier", "TEST_EVENT", {"data": "value2"})

    # Integrity should hold initially
    assert trail.verify_integrity() is True

    # Tamper with a log entry
    if trail.logs:
        trail.logs[0]["payload_hash"] = "tampered_hash"

    # Integrity check should fail after tampering
    assert trail.verify_integrity() is False
