# SMART H2S ARKL — PROJECT STATUS

> Source of truth: repository code, migrations, tests, settings, URL registration, and committed `schema.yml`.
> Updated: 2026-08-20. This document records the current audit; it does not alter application logic, database records, migrations, or environment values.

## 1. Project Identity

- **Purpose:** Django backend for MQTT H2S monitoring, exposure management, Smart ARKL, deterministic alerts, and research reporting.
- **Stack:** Django 5.2, Django REST Framework, drf-spectacular, paho-mqtt, pytest, Ruff.
- **Database:** SQLite (`db.sqlite3`).
- **Architecture:** modular Django monolith: View → Serializer → Service → Model/ORM → SQLite.
- **IoT:** MQTT subscriber via `python manage.py run_mqtt`.
- **Automation boundary:** MQTT ingestion does not automatically calculate ARKL or create an Alert; callers invoke ARKL and Alert evaluation APIs explicitly.

## 2. Current Overall Status

| Layer | Name | Status | Notes |
| --- | --- | --- | --- |
| 1 | IoT Environmental Monitoring | DONE | MQTT validation, persistence, provenance, reading APIs, and Device→H2SReading relation exist. |
| 2 | Data & Exposure Management | DONE | Worker and one-to-one ExposureProfile with validation and limited CRUD exist. |
| 3 | Smart ARKL | DONE — ENGINEERING / SCIENTIFIC REVIEW PENDING | Runtime is intake-based `2.0.0-MVP`; its scientific reference/unit methodology is not established as final by engineering tests. |
| 4 | Alert & Risk Management | DONE — CORE LOGIC LOCKED | Matrix, recommendation, persistence, dedupe, escalation, lifecycle, and APIs consume ARKL interpretation only. |
| 5 | Research & Reporting | DONE — ENGINEERING | All seven specified endpoints are registered, schema-listed, and implemented as persisted-data readers. Runtime quality verification remains pending. |
| 6 | Authentication & Authorization | NOT STARTED | Django auth is installed, but API permissions, roles, Worker ownership, and lifecycle actors are absent. |

## 3. Current Development Position

Project berada pada transisi dari completed engineering Layers 1–5 menuju Layer 6, dengan scientific verification ARKL dan runtime quality verification sebagai parallel gates.

```text
Completed engineering: Layers 1–5
    ↓
Current: ARKL scientific reference/unit review + quality gate in compatible runtime
    ↓
Next: Layer 6 authentication, authorization, ownership, actor audit
    ↓
Later: physical IoT hardening and production operations
```

## 4. Layer 1 — IoT Environmental Monitoring

### Implemented

- `Device`: unique `device_code`, name, location, active state, timestamps.
- `H2SReading`: device, `ppm`, `adc`, `filtered_adc`, `level`, `status`, `uptime_ms`, `simulated`, backend `received_at`.
- MQTT requires `device_id`, `ppm`, `adc`, `filtered_adc`, `level`, `status`, `uptime_ms`, and boolean `simulated`.
- Invalid JSON/telemetry is rejected; valid telemetry atomically reuses/creates Device then persists H2SReading.
- Simulated provenance is retained through ARKLResult and Alert.
- Read APIs include filtered readings and a deterministic latest reading ordered by `received_at DESC, id DESC`.

### Remaining physical IoT work

- Sensor calibration and quality-control method.
- Device provisioning and allowed topic/device policy.
- Source/sensor timestamp and message identity/idempotency contract.
- Production MQTT supervision/reconnect strategy.

### Known debt

Payload has no source timestamp or idempotency key; repeated delivery may create duplicate readings. The repository does not demonstrate production physical-sensor calibration.

## 5. Layer 2 — Data & Exposure Management

- `Worker` is a domain exposure subject (`code`, `is_active`, timestamps), not an authentication user.
- `ExposureProfile` is one-to-one with Worker and stores `body_weight`, `exposure_time`, `exposure_frequency`, `exposure_duration`, and `inhalation_rate`.
- Validation prevents invalid numeric/negative values; ARKL applies further domain/range validation.
- APIs: Workers `GET, POST /api/v1/workers/`, `GET /api/v1/workers/{id}/`; profiles `GET, POST /api/v1/exposure-profiles/`, `GET, PATCH /api/v1/exposure-profiles/{id}/`.

Future authentication must link Django User optionally to Worker; it must not convert Worker into an auth model.

## 6. Layer 3 — Smart ARKL

### Runtime formula and version

Current runtime version is `2.0.0-MVP`.

```text
C_mg/m³ = ppm × 1.40
tavg = Dt × 365
I = (C × R × tE × fE × Dt) / (Wb × tavg)
RQ = I / configured reference value
RQ <= 1 → WITHIN_REFERENCE_LEVEL
RQ > 1  → ABOVE_REFERENCE_LEVEL
```

The configured runtime reference constant is `H2S_RFC = 0.002`; new results persist it in `ARKLResult.rfc`.

### Runtime behavior

- Realtime uses the deterministic latest reading and persists it in `ARKLResult.reading`.
- Historical uses arithmetic mean ppm in the selected inclusive period, sets `reading = NULL`, and stores period/count metadata.
- v2 persists concentration, all exposure snapshots, averaging time, intake, RfC, RQ, interpretation, version, and source provenance.
- `exposure_concentration_mg_m3` is set to `NULL` for v2 and is not in the primary v2 pipeline.
- Existing versioned v1.1 records remain representable; no migration was needed because the existing nullable schema supports both representations.

### Scientific guardrail

**Engineering implemented/testable; scientific reference and unit verification pending.** The repository does not by itself establish that `tavg`, reference value/RfC, intake units, or the ppm conversion source are scientifically final. RQ is risk characterization, not a disease diagnosis or probability.

### Files/layers affected by a future approved methodology revision

- `arkl/services/{constants,validation,intake,rq,calculator}.py`, ARKL tests, API/schema documentation.
- A new versioned migration only if the approved result contract requires schema changes.
- Alert regression tests, Research version filters/exports, and frontend contract. Historical records must not be overwritten or relabeled.

## 7. Layer 4 — Alert & Risk Management

**Status: DONE — CORE LOGIC LOCKED. Rule version: `1.0.0-MVP`.**

- Environmental strings normalize to `NORMAL`, `CAUTION`, `WARNING`, `DANGER`, or `CRITICAL`.
- The fixed matrix combines environmental severity with `ARKLResult.interpretation` to produce `NONE`, `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.
- Risk statuses map deterministically to no action, monitoring, risk management, or immediate action.
- Recommendation codes are derived from the selected Alert level.
- Persistence stores source snapshots plus ARKL calculation version and alert-rule version.
- `OPEN` and `ACKNOWLEDGED` are active for deduplication; same level is duplicate, higher level escalates with a new Alert, lower level does not create a new Alert.
- Lifecycle supports `OPEN → ACKNOWLEDGED → RESOLVED`; acknowledge and resolve are idempotent; resolved alerts permit new alerts.
- Historical ARKLResult is rejected for realtime Alert persistence.
- Alert does not calculate Intake, RQ, reference value, or ARKL interpretation.

If ARKL changes in a future version, Layer 4 requires regression, not an automatic decision-rule rewrite.

## 8. Layer 5 — Research & Reporting

### Implemented and registered

| Capability | Endpoint | Evidence |
| --- | --- | --- |
| H2S summary | `GET /api/v1/research/h2s-summary/` | summary service/view/test source |
| H2S trends: raw/hour/day | `GET /api/v1/research/h2s-trends/` | trend service/view/test source |
| Version-aware ARKL recap | `GET /api/v1/research/arkl-results/` | filters by exactly one `calculation_version` |
| Risk distribution | `GET /api/v1/research/risk-distribution/` | version-aware persisted ARKL aggregation |
| Exposure summary | `GET /api/v1/research/exposure-summary/` | persisted ExposureProfile aggregation |
| Alert summary | `GET /api/v1/research/alert-summary/` | persisted Alert aggregation |
| ARKL CSV export | `GET /api/v1/research/export/arkl.csv` | uses research-result service; no recalculation |

- `config/urls.py` includes `research.urls` at `/api/v1/research/`.
- The seven routes are present in committed `schema.yml`.
- H2S filters retain tri-state provenance: omitted = all, `true` = simulated, `false` = physical.
- ARKL recap/risk distribution default to the active runtime calculation version and require one explicit version context, preventing silent v1.1/v2 mixing.
- Research reads persisted data and does not reimplement ARKL, interpretation, or Alert rules.

## 9. End-to-End Current Flow

```text
MQTT telemetry
  ↓
validated Device + H2SReading
  ↓ explicit caller POST
realtime/historical ARKL API
  ↓
versioned ARKLResult
  ↓ explicit caller POST
Alert evaluate API
  ↓
Alert + persisted snapshots/recommendations
  ↓
read-only Research APIs / CSV export
```

## 10. REST API Inventory

### Active

- Devices: `GET /api/v1/devices/`, `GET /api/v1/devices/{id}/`, `GET /api/v1/readings/`, `GET /api/v1/readings/{id}/`, `GET /api/v1/readings/latest/`.
- Exposure: Worker/Profile endpoints in Layer 2 above.
- ARKL: `POST /api/v1/arkl/realtime/`, `POST /api/v1/arkl/historical/`, `GET /api/v1/arkl/results/`, `GET /api/v1/arkl/results/{id}/`.
- Alerts: `GET /api/v1/alerts/`, `GET /api/v1/alerts/{id}/`, `POST /api/v1/alerts/evaluate/`, `PATCH /api/v1/alerts/{id}/acknowledge/`, `PATCH /api/v1/alerts/{id}/resolve/`.
- Research: all seven endpoints listed in Layer 5.
- Documentation: `GET /api/schema/`, `GET /api/docs/`.

### Missing REST capabilities

- Authentication/login/token endpoints.
- Role/permission and object-ownership enforcement.
- Actor identity in acknowledge/resolve responses/history.

## 11. Database Relationship

```text
Device 1 ───< H2SReading
Worker 1 ─── 1 ExposureProfile
Worker 1 ───< ARKLResult >── 0..1 H2SReading
Worker 1 ───< Alert >──────── 1 Device
                         └──── 1 H2SReading
                         └──── 1 ARKLResult
```

`PROTECT` is used for historical H2SReading/Worker/ARKLResult references; Worker→ExposureProfile uses `CASCADE`.

## 12. Testing and Quality Status

Static inventory identifies **192 test functions**: devices 15, exposure 13, ARKL 55, alerts 50, research 46, core 13. This is not equivalent to a pytest collected-item count because parametrization can create additional items.

| Check | Status | Exact result/evidence |
| --- | --- | --- |
| `pytest -v` | NOT RUN | `/bin/bash: pytest: command not found` |
| `ruff check .` | NOT RUN | `/bin/bash: ruff: command not found` |
| `ruff format --check .` | NOT RUN | `/bin/bash: ruff: command not found` |
| `python manage.py check` | NOT RUN | `/bin/bash: python: command not found` |
| `python manage.py spectacular --file schema.yml` | NOT RUN | `/bin/bash: python: command not found` |
| `pip-audit` | NOT RUN | `/bin/bash: pip-audit: command not found` |
| `python manage.py makemigrations --check --dry-run` | NOT RUN | `/bin/bash: python: command not found` |
| URL/schema inspection | VERIFIED | Root includes Research; all seven Research routes are in `schema.yml` (26 API paths total). |

The repository contains a Windows virtualenv (`.venv/Scripts/*.exe`), but it cannot run through this WSL environment due interop socket failure. The prior `206 passed` baseline is not treated as a current verified result.

## 13. Engineering Verdict

**PASS WITH KNOWN GAPS.**

- Static repository evidence supports complete engineering paths for Layers 1–5, including ARKL v2 and version-aware Research endpoints.
- The current environment cannot execute the requested runtime quality gate, so test/lint/schema/migration PASS is not independently verified here.
- No source evidence supports production-ready physical IoT, authentication/authorization, or final scientific ARKL methodology.
- It is reasonable to plan Layer 6 after restoring verification capability; implementation should begin only after the quality gate is executed and recorded.

## 14. Locked Components

- MQTT required payload contract and simulated provenance.
- Existing historical ARKLResult and Alert records, including version values.
- Alert decision matrix, lifecycle, dedupe/escalation semantics, and `1.0.0-MVP` rule version.
- Alert boundary: consume persisted ARKL interpretation only.
- Core request ID, request/error/performance/security middleware and rotating-log configuration.
- `/api/v1/` prefix.

## 15. Current Blockers and Gaps

### Compatible quality runtime

- **Why:** Linux shell lacks project Python tooling; Windows virtualenv cannot execute under current WSL interop.
- **Blocks:** verified pytest, Ruff, Django check, schema generation, migration check, and dependency audit.

### Scientific methodology verification

- **Why:** source/unit compatibility for intake, `tavg`, reference value, and ppm conversion requires approved scientific evidence, not code inference.
- **Blocks:** scientific-final claims and research publication methodology approval; it does not negate the implemented engineering version.

### Security / Layer 6

- **Why:** no permission classes/default permissions, User↔Worker link, ownership filters, or lifecycle actor fields were found.
- **Blocks:** safe exposure of mutating APIs to real users.

## 16. Technical Debt

### CRITICAL

- Mutating API endpoints are not protected by authentication/authorization.

### HIGH

- MQTT idempotency and source timestamp are absent.
- Alert dedupe is query-based without a database uniqueness/locking guarantee across concurrent evaluations.

### MEDIUM

- `H2SReading.level` is stored while alert decision uses `status`; no consistency rule is enforced.
- Raw H2S trends return all matching readings without a pagination/limit strategy.
- `redact_mapping` exists but is not referenced by inspected logging paths.
- MQTT uses `smart_h2s.mqtt`; no dedicated logger declaration/handler is present in settings, so runtime routing should be verified.
- Research URL/view source has non-canonical import/layout formatting that may fail Ruff/format checks; this is unverified until the runtime gate is available.

### LOW

- Legacy ARKL v1.1 helpers remain for compatibility and must remain clearly version-labeled.
- SQLite is appropriate for MVP but has limited high-concurrency/production-ingestion characteristics.

## 17. Authentication and Role Plan

Use Django built-in User with optional Worker linkage:

```text
Django User
  ↓ optional one-to-one link
Worker
  ↓
ExposureProfile
```

- **ADMIN:** user/role/device/worker administration and audit access.
- **OPERATOR:** telemetry, operational ARKL, and Alert lifecycle actions.
- **RESEARCHER:** constrained read-only research and export access.
- **WORKER:** only own profile and relevant risk/alert data.

Layer 6 must add endpoint permissions, object ownership filtering, and acknowledged/resolved actor audit without changing Alert decision rules.

## 18. Recommended Next Tasks

1. Restore a compatible Python environment and run the seven documented quality commands; record exact outputs.
2. Resolve any actual lint/format/check/migration failures found by that gate.
3. Obtain approved scientific references/units for ARKL v2 (`tavg`, reference value, conversion) and version the decision record.
4. Begin Layer 6 with Django User, role groups, endpoint permissions, and optional User↔Worker relation.
5. Add ownership filtering and Alert lifecycle actor audit fields without altering alert rules.
6. Add MQTT idempotency, source timestamp, and provisioning policy.
7. Define physical sensor calibration/quality metadata and deployment operating procedures.
8. Plan production database/concurrency strategy when ingestion scale requires it.

## 19. Do Not Do Yet

- Do not overwrite/relabel v1.1 ARKL data as v2.
- Do not change ARKL constants, tavg, or formula without approved science.
- Do not rewrite Alert rules merely because ARKL v2 exists.
- Do not use RQ as diagnosis or probability of disease.
- Do not convert Worker into the auth model.
- Do not claim production readiness from static inspection or unverified historical test claims.

## 20. Handoff Summary

```text
Current engineering stage: Layers 1–5 are implemented in source; Layer 6 is next.
Layer 3 runtime: ARKL 2.0.0-MVP, intake-based; science/source/unit verification remains pending.
Layer 4: DONE — CORE LOGIC LOCKED; Alert consumes ARKL interpretation and does not recalculate risk.
Layer 5: seven Research endpoints are registered and schema-listed; ARKL reports are version-aware.
No automatic MQTT → ARKL → Alert pipeline exists; callers trigger ARKL and Alert APIs.
Quality gate was NOT RUN in this audit: Python/pytest/Ruff/pip-audit absent in Linux shell; Windows venv is not executable here.
Static test inventory: 192 test functions; do not treat it as pytest collected/pass count.
Main immediate task: restore compatible runtime and run the complete quality gate.
Main security gap: APIs have no auth, roles, ownership, or lifecycle actor audit.
Main IoT gap: no source timestamp/idempotency/calibration contract.
Do not alter historical ARKL versions, Alert rules, or scientific constants without approval.
```
