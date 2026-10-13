"""
FastAPI REST API Server for Mammography Tomosynthesis Dbt Agent.
"""
from typing import Dict, Any, List
from pathlib import Path
from fastapi.responses import FileResponse
from .base import SecurityException
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Mammography Tomosynthesis Dbt Agent API",
    description="Synthetic-input demonstration of deterministic threshold checks; not a medical device.",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "mammography-tomosynthesis-dbt-agent", "domain": "Clinical & Biomedical AI", "standard": "Unvalidated demonstration thresholds", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
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
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(Path(__file__).resolve().parent.parent / "web" / "index.html")
