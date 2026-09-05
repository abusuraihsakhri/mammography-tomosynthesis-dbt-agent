# Mammography Tomosynthesis Dbt Agent

> **Domain:** Diagnostic Radiology & Medical Imaging AI
> **Reference Guidelines & Standards:** American College of Radiology (ACR) BI-RADS & Fleischner Society

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Mammography Tomosynthesis Dbt Agent is an enterprise-grade analytical platform for Digital Breast Tomosynthesis (DBT) imaging workflows. It provides deterministic evaluation of imaging parameters, multi-tier risk classification, and cryptographic audit trail generation for clinical AI applications.

The system orchestrates multiple specialized workers (QC Invariant, Safety Escalation, Protocol Conformance) to evaluate imaging data against CAP/CLSI/ISO reference standards, generating consensus dossiers with actionable alerts.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with ACR BI-RADS reference formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization (ROUTINE, ELEVATED_RISK, CRITICAL_STAT_PANIC) with automated clinical action recommendations.
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection.
- **Zero-PHI Outbound Interceptor**: Blocks SSNs, MRNs, phone numbers, and patient identifiers from leaving the system.
- **Tamper-Evident HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs for every evaluation.
- **Domain Enrichment Suite**: 8 specialized engines covering 3D volume rendering, microcalcification analysis, lesion segmentation, bilateral comparison, view coordination, dense breast assessment, and artifact detection.

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/mammography-tomosynthesis-dbt-agent.git
cd mammography-tomosynthesis-dbt-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py audit
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 3. Batch Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. System Chat
```bash
python cli.py chat "What is the system status?"
```

### 5. Verify Audit Trail
```bash
python cli.py verify-audit
```

### 6. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
| Flag | Description | Default |
|:-----|:------------|:--------|
| `--task-id` | Unique task / case identifier | `TASK-2026-001` |
| `--target` | Target specimen or entity identifier | `KEY-TARGET-01` |
| `--primary` | Primary domain measurement (float) | `28.5` |
| `--secondary` | Secondary kinetic/confidence score (float) | `14.2` |
| `--critical` | Emergency escalation flag | `False` |
| `--status` | Status code or phenotype descriptor | `DISCORDANT` |
| `-i / --input` | Input CSV file path for batch mode | Required |
| `-o / --output` | Output CSV file path for batch mode | `results.csv` |

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique case identifier | Required |
| `target_identifier` | Specimen or entity key | Required |
| `primary_metric` | Primary measurement value | Required |
| `secondary_metric` | Secondary confidence/kinetic score | Optional (default: 0.0) |
| `is_critical_flag` | Emergency escalation trigger | Optional (default: False) |
| `status_descriptor` | Status code or phenotype | Optional (default: "NOMINAL") |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, DOB, and patient names.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Configurable Audit Secret:** Set `AUDIT_SECRET_KEY` environment variable for production deployments. Without it, an ephemeral runtime key is generated (with a warning).
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Security Configuration

```bash
# Set a persistent audit secret for production
export AUDIT_SECRET_KEY="your-secure-random-key-here"

# Or via docker-compose environment
AUDIT_SECRET_KEY=your-secure-random-key-here
```

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

Run the enrichment domain suite directly:

```bash
python -c "from enrichment import enrichment_suite; results = enrichment_suite.execute_all(1.5, 0.5); print(f'Executed {len(results)} domain engines')"
```

---

## 🐳 Container Deployment

```bash
docker build -t mammography-tomosynthesis-dbt-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secure-key mammography-tomosynthesis-dbt-agent
```

Or using Docker Compose:

```bash
docker-compose up --build
```

---

## 📁 Project Structure

```
mammography-tomosynthesis-dbt-agent/
├── agents/                    # Core agent framework
│   ├── __init__.py           # Package initialization
│   ├── api.py                # FastAPI REST endpoints
│   ├── base.py               # Security, PHI guard, audit trail
│   ├── learning.py           # Bayesian calibration engine
│   ├── llm_factory.py        # LLM provider factory
│   ├── metrics.py            # Prometheus metrics collector
│   ├── models.py             # Pydantic data models
│   ├── streamer.py           # WebSocket telemetry
│   ├── supervisor.py         # Multi-worker orchestrator
│   └── workers.py            # Specialized evaluation workers
├── dbt_sentinel/             # DBT-Sentinel sub-system
│   ├── __init__.py
│   ├── agents.py             # Specialized DBT agents
│   ├── cli.py                # DBT-Sentinel CLI
│   ├── engine.py             # Domain evaluation engine
│   ├── models.py             # DBT data models
│   └── server.py             # DBT FastAPI server
├── tests/                    # Test suite
│   ├── test_dbt_sentinel.py
│   ├── test_enrichment.py
│   └── test_mammography_tomosynthesis_dbt_agent.py
├── web/                      # Static web interface
│   └── index.html
├── cli.py                    # Main CLI entry point
├── enrichment.py             # Domain enrichment engines
├── simulator.py              # High-throughput simulator
├── pyproject.toml            # Project configuration
├── Dockerfile                # Container build
├── docker-compose.yml        # Multi-service orchestration
├── sample.csv                # Sample batch input
├── sample_payload.json       # Sample API payload
└── openapi_spec.json         # OpenAPI specification
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
