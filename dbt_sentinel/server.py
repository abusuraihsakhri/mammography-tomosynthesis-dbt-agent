"""
FastAPI REST API Server for DBT-Sentinel: Digital Breast Tomosynthesis Slice Reconstruction Agent.
"""
from typing import Dict, Any
from .models import FrontierPayload
from .agents import DBTSentinelCoordinator
from agents.base import SecurityException

coordinator = DBTSentinelCoordinator()


def create_app():
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel, Field

        app = FastAPI(
            title="DBT-Sentinel: Digital Breast Tomosynthesis Slice Reconstruction Agent",
            description="Demonstration numeric-threshold checks. No DBT reconstruction or lesion detection.",
            version="2.0.0-FRONTIER",
        )

        class TaskRequest(BaseModel):
            task_id: str = "TASK-2026-001"
            target_identifier: str = "TARGET-BIO-KEY"
            primary_metric: float = Field(default=28.5, allow_inf_nan=False)
            secondary_metric: float = Field(default=14.2, allow_inf_nan=False)
            status_descriptor: str = "DISCORDANT_ANOMALY"
            is_critical_flag: bool = True
            attributes: Dict[str, Any] = Field(default_factory=dict)

        class ChatRequest(BaseModel):
            query: str

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "mammography-tomosynthesis-dbt-agent", "domain": "Breast Imaging AI", "version": "2.0.0-FRONTIER"}

        @app.post("/api/audit")
        def api_audit(req: TaskRequest):
            payload = FrontierPayload(
                task_id=req.task_id,
                target_identifier=req.target_identifier,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_descriptor=req.status_descriptor,
                is_critical_flag=req.is_critical_flag,
                attributes=req.attributes,
            )
            try:
                return coordinator.process(payload)
            except SecurityException:
                raise HTTPException(status_code=422, detail="Use synthetic data only.") from None

        @app.post("/api/chat")
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_supervisory_chat(req.query)}

        return app
    except ImportError:
        return None
