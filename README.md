# DBT Sentinel — Synthetic Rules Demonstration

A browser and Python toolkit for deterministic threshold checks on **synthetic numeric inputs**. The primary workflow evaluates a task against three fixed rules, produces a JSON dossier, and optionally records an in-memory HMAC audit chain when using Python.

**Important limitation:** Despite the original name and worker class names, the project **does not** load DICOM data, reconstruct digital breast tomosynthesis images, detect microcalcifications or masses, assign BI-RADS categories, or implement validated clinical thresholds. It must not be used for diagnosis, triage, clinical quality assurance, or medical decisions.

## Browser demonstration

The static interface is in [web/index.html](web/index.html). It needs no Python runtime or server-side API; evaluation uses JavaScript rules tested in CI. Features include synthetic-input validation, session counters, readable JSON output, and JSON download. Browser results have `audit_hash: null` because no cryptographic signature is created.

To preview locally:

~~~bash
python -m http.server 8080 --directory web
~~~

Open **http://localhost:8080/**. An HTTP server is needed because ES modules may not load from `file://`.

An optional checkbox sends tasks to a **same-origin FastAPI server** instead. That mode does not run on static GitHub Pages. Unavailable APIs produce visible errors rather than substitute results.

## Python installation

Python 3.9+ is supported. From the cloned repository:

~~~bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[api,dev]"
python -m pytest -q
~~~

On Windows, activate the environment through its `Scripts` directory.

## Commands

The primary implementation is in `agents/`, with entry point `cli.py`.

~~~bash
mammography-tomosynthesis-dbt-agent audit --task-id DEMO-001 --target SYNTH-01 --primary 29.4 --secondary 14.8 --status DISCORDANT
mammography-tomosynthesis-dbt-agent batch -i sample.csv -o results.csv
mammography-tomosynthesis-dbt-agent chat "status"
mammography-tomosynthesis-dbt-agent verify-audit
mammography-tomosynthesis-dbt-agent serve --host 127.0.0.1 --port 8000
~~~

The legacy `dbt_sentinel/` subsystem is retained and callable through the original installed `mammography-tomosynthesis-dbt-engine` command or `python dbt_sentinel_app.py`. These implementations differ: the primary secondary-metric cutoff is **12**, whereas the legacy cutoff is **10**. Both primary cutoffs are **25**. Neither threshold is clinically validated.

CSV `is_critical_flag` accepts `true`/`false`, `1`/`0` or `yes`/`no`. Ambiguous entries are rejected.

## API and security

With the primary server running, open **http://127.0.0.1:8000/** for the interface and **http://127.0.0.1:8000/docs** for generated API documentation. Key endpoints: `POST /api/audit`, `POST /api/chat`, `GET /health`, `GET /metrics` and `GET /api/audit/logs`.

- Regex-based guards reject some common identifiers in task text and metadata. This is **not comprehensive PHI detection, de-identification, HIPAA compliance, or authorization to handle clinical records**. Only use synthetic data.
- The HMAC audit ledger is **in memory** and does not survive a process restart. Integrity verification checks recorded fields in that process, provided the signing key stays secret.
- Configure a strong unique `AUDIT_SECRET_KEY` to make the key stable across restarts. Without one, the runtime warns and generates an ephemeral key.
- The audit-log read endpoint is disabled until `AUDIT_READ_TOKEN` is configured; then it requires the `X-Audit-Token` request header. Other demo endpoints are unauthenticated and should not be exposed to untrusted clients without further controls.
- Chat responses are deterministic mock text; external model providers are not implemented. The `enrichment.py` classes are generic numeric rule wrappers, **not** working rendering or segmentation engines.
- Browser-only mode processes data locally. Explicit API mode sends JSON to the same-origin server. No external fonts or tracking scripts are loaded.

See [.env.example](.env.example) for configuration variables. Never commit a populated `.env`.

## Docker

~~~bash
cp .env.example .env
# Set AUDIT_SECRET_KEY in .env to a newly generated, strong random value.
docker compose up --build
~~~

Compose refuses to start if `AUDIT_SECRET_KEY` is missing or empty. The container exposes FastAPI on port 8000.

## Testing and technology

~~~bash
python -m pytest -q
node --test web/logic.test.mjs
node --check web/app.mjs
python simulator.py 100
~~~

CI checks Python 3.9–3.12, installed console scripts, API routes, and JavaScript rules. Stack: Python, Pydantic, FastAPI, Uvicorn, vanilla JavaScript ES modules, and GitHub Actions. The browser interface targets current Chrome, Firefox, Safari and Edge versions supporting ES modules; a cross-browser matrix has not yet been run.

## License

MIT — see [LICENSE](LICENSE).
