"""
FastAPI REST API Server for Mammography Tomosynthesis Dbt Agent.
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import os
import hmac
from fastapi.responses import FileResponse
from .base import SecurityException
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Mammography Tomosynthesis Dbt Agent API",
    description="Synthetic-input demonstration of deterministic threshold checks; not a medical device.",
    version="2.1.0",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "mammography-tomosynthesis-dbt-agent", "domain": "Clinical & Biomedical AI", "standard": "Unvalidated demonstration thresholds", "version": "2.1.0"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "DEMONSTRATION_RUNNING"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=422, detail="Input includes a prohibited identifier; use synthetic data.") from None
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=422, detail="Input includes a prohibited identifier; use synthetic data.") from None


@app.get("/api/audit/logs")
def api_audit_logs(x_audit_token: Optional[str] = Header(default=None, alias="X-Audit-Token")):
    """Audit metadata access requires a distinct read token, disabled by default."""
    read_token = os.getenv("AUDIT_READ_TOKEN")
    if not read_token:
        raise HTTPException(status_code=503, detail="Audit log access is not configured.")
    if not x_audit_token or not hmac.compare_digest(x_audit_token, read_token):
        raise HTTPException(status_code=403, detail="Not authorized to read audit logs.")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(Path(__file__).resolve().parent.parent / "web" / "index.html")


@app.get("/app.mjs", include_in_schema=False)
def browser_app_module():
    return FileResponse(Path(__file__).resolve().parent.parent / "web" / "app.mjs", media_type="text/javascript")


@app.get("/logic.mjs", include_in_schema=False)
def browser_rules_module():
    return FileResponse(Path(__file__).resolve().parent.parent / "web" / "logic.mjs", media_type="text/javascript")
