# SOP Pengembangan Backend Smart H₂S v2.0

> **Tujuan dokumen:** menjadi panduan kerja aktif dan source of truth engineering agar pengembangan backend Smart H₂S tetap terarah, sederhana, reproducible, dan tidak melompat-lompat antar-layer.
>
> **Stack:** Django + Django REST Framework + SQLite + Paho MQTT + React Frontend
>
> **Prinsip:** SOLID, KISS, YAGNI, deterministic calculation, explicit scientific assumptions
>
> **Status:** Active Development / Living SOP
>
> **Version:** 2.0
>
> **Scientific calculation source of truth:** `ARKL_CALCULATION_SPEC.md`
>
> **ARKL specification version:** `1.0.0-MVP`
>
> **ARKL specification status:** `MVP SCIENTIFIC LOCK`

---

# 1. Prinsip Kerja Utama

Selama pengembangan backend, gunakan aturan berikut.

1. Kerjakan satu tahap sampai acceptance criteria terpenuhi sebelum berpindah ke tahap berikutnya.
2. Jangan membuat fitur yang belum dibutuhkan. Terapkan YAGNI.
3. Jangan membuat abstraksi berlebihan. Terapkan KISS.
4. Pisahkan tanggung jawab kode. Terapkan SOLID.
5. Views harus tipis.
6. Serializer menangani request/response validation dan representation API.
7. Service menangani business logic, orchestration, MQTT processing, scientific calculation, alert rule, dan aggregation.
8. Model menangani struktur data, relasi, dan persistence.
9. Middleware/observability mengawasi HTTP request, error, performance, dan security.
10. MQTT/background process menggunakan logger `smart_h2s.*`.
11. Core observability yang sudah tersedia tidak boleh diimplementasikan ulang di masing-masing app.
12. Scientific calculation harus deterministic.
13. Semua konstanta ilmiah wajib memiliki sumber dan calculation version.
14. Semua satuan calculation harus eksplisit.
15. Tidak boleh ada hidden default untuk data responden.
16. Tidak boleh melakukan rounding pada intermediate scientific calculation.
17. AI/LLM tidak boleh menghitung Intake, RfC, atau RQ.
18. Wokwi/IoT tidak dikontrol backend.
19. Backend hanya menjadi consumer telemetry MQTT dan penyedia API.
20. Jangan mengubah Layer 1 yang sudah bekerja tanpa kebutuhan teknis yang jelas.
21. Data simulasi dan data sensor fisik harus dapat dibedakan.
22. Hasil ARKL adalah risk characterization, bukan diagnosis medis.
23. Testing adalah quality gate setiap phase, bukan pekerjaan yang ditunda sampai akhir.

---

# 2. Arsitektur Backend

Gunakan arsitektur sederhana:

```text
Presentation / API
views.py + serializers.py
        ↓
Application / Business Logic
services/
        ↓
Persistence
models.py + Django ORM
        ↓
SQLite
```

Alur HTTP:

```text
React
  ↓
Django View
  ↓
Serializer
  ↓
Service
  ↓
Model / ORM
  ↓
SQLite
```

Alur MQTT:

```text
Wokwi / ESP32
      ↓
MQTT Broker
      ↓
Django MQTT Subscriber
      ↓
Telemetry Validation
      ↓
MQTT Ingestion Service
      ↓
Device + H2SReading
      ↓
SQLite
```

Scientific calculation:

```text
H2SReading
    +
ExposureProfile
    ↓
Validation
    ↓
Conversion
    ↓
Aggregation bila diperlukan
    ↓
Intake
    ↓
RfC
    ↓
RQ
    ↓
Interpretation
    ↓
ARKLResult
```

---

# 3. Observability / CCTV Backend

Observability adalah infrastructure lintas-layer.

```text
                    BACKEND
                       │
      ┌────────────────┼────────────────┐
      │                │                │
     HTTP           Services          MQTT
      │                │                │
      └────────────────┼────────────────┘
                       ↓
                 OBSERVABILITY
```

## 3.1 Existing Observability

Infrastructure berikut sudah tersedia dan tidak boleh dibuat ulang:

```text
[x] Request ID / Trace ID
[x] Request logging
[x] Error logging
[x] Performance monitoring
[x] Security audit logging
[x] Sensitive data redaction
[x] Rotating file logs
[x] Unit tests
[x] Feature tests
```

HTTP menggunakan middleware global yang sudah terdaftar di `settings.py`.

Background process menggunakan logger:

```text
smart_h2s.*
```

Contoh:

```text
smart_h2s.mqtt
smart_h2s.arkl
smart_h2s.alerts
smart_h2s.research
```

## 3.2 Jangan Dicatat

Jangan menulis ke log:

- password;
- access token;
- Authorization header;
- sensitive cookie;
- full body berisi data pribadi;
- data kesehatan mentah yang tidak diperlukan;
- secret `.env`.

---

# 4. Roadmap Utama v2

```text
Phase 0 — Backend Foundation
        ↓
Phase 1 — Devices + MQTT Ingestion
        ↓
Phase 2 — Layer 2 Data Models
        ↓
Phase 3 — Layer 2 REST API
        ↓
Phase 4 — Smart ARKL
        ↓
Phase 5 — Alert & Risk Management
        ↓
Phase 6 — Research & Reporting
```

Testing dilakukan di dalam setiap phase.

---

# 5. Phase 0 — Backend Foundation

## Tujuan

Membangun fondasi Django yang bersih sebelum domain feature dikembangkan.

## Pekerjaan

- Membuat virtual environment Python.
- Membuat Django project.
- Mengaktifkan Django REST Framework.
- Menggunakan SQLite sebagai database MVP.
- Menambahkan CORS untuk React.
- Menambahkan `.env`.
- Menambahkan `.env.example`.
- Menambahkan `.gitignore`.
- Menambahkan drf-spectacular/OpenAPI.
- Menambahkan pytest.
- Menambahkan pytest-django.
- Menambahkan Ruff.
- Menambahkan pip-audit.
- Menyiapkan logging.
- Menyiapkan Request ID.
- Menyiapkan request logging.
- Menyiapkan error logging.
- Menyiapkan performance monitoring.
- Menyiapkan security audit logging.
- Menyiapkan redaction.
- Menyiapkan rotating logs.
- Menyiapkan unit + feature tests observability.

## Struktur

```text
backend/
├── config/
├── core/
│   ├── middleware/
│   ├── observability/
│   └── tests/
├── devices/
├── exposure/
├── arkl/
├── alerts/
├── research/
├── requirements/
├── .env
├── .env.example
├── .gitignore
├── pyproject.toml
├── pytest.ini
├── db.sqlite3
└── manage.py
```

## Definition of Done

```text
[x] Django berjalan.
[x] Migration dasar berhasil.
[x] DRF tersedia.
[x] React diperbolehkan mengakses API development.
[x] Request logging bekerja.
[x] Error logging bekerja.
[x] Request ID bekerja.
[x] Performance monitoring bekerja.
[x] Security audit bekerja.
[x] Redaction bekerja.
[x] pytest berjalan.
[x] Ruff berjalan.
[x] pip-audit tersedia.
```

Status:

```text
PHASE 0 = DONE
```

---

# 6. Phase 1 — Devices + MQTT Ingestion

## Tujuan

Backend menerima telemetry dari Layer 1 melalui MQTT tanpa mengontrol perangkat.

## Alur

```text
Wokwi / ESP32
      ↓
MQTT Publish
      ↓
MQTT Broker
      ↓
Django MQTT Subscriber
      ↓
Payload Validation
      ↓
Persistence
```

## Model

```text
Device
├── id
├── device_code
├── name
├── location
├── is_active
├── created_at
└── updated_at
```

```text
H2SReading
├── id
├── device
├── ppm
├── adc
├── filtered_adc
├── level
├── status
├── uptime_ms
├── simulated
└── received_at
```

`sensor_timestamp` belum menjadi baseline karena payload sensor saat ini belum menyediakan timestamp sensor terpercaya.

## Pekerjaan

```text
[x] Device model
[x] H2SReading model
[x] telemetry validator
[x] mqtt_ingestion.py
[x] run_mqtt management command
[x] Subscribe telemetry topic
[x] Parse JSON
[x] Required-field validation
[x] Reject invalid payload
[x] Store valid payload
[x] Device get_or_create
[x] received_at
[x] simulated provenance
[x] MQTT logging
[x] reconnect handling
[x] invalid message tidak mematikan subscriber
```

## MQTT Scope

Backend tidak boleh:

- mengontrol Wokwi;
- mengubah ADC;
- mengubah firmware;
- mengubah nilai ppm;
- melakukan ARKL calculation;
- membawa data pribadi melalui public MQTT.

## Deterministic Latest Reading

Definisi latest reading:

```text
ORDER BY received_at DESC, id DESC
```

Rule ini harus digunakan konsisten oleh:

```text
GET /api/v1/readings/latest/
```

dan:

```text
calculate_realtime_risk()
```

## Definition of Done

```text
[x] Wokwi publish telemetry
[x] React tetap menerima telemetry
[x] Backend menerima telemetry
[x] Valid reading tersimpan
[x] Invalid JSON ditolak
[x] Invalid payload ditolak
[x] Subscriber tetap hidup
[x] reconnect bekerja
[x] MQTT events logged
[x] no Layer 3 dependency
```

Status:

```text
PHASE 1 = DONE
```

---

# 7. Phase 2 — Layer 2 Data Models

## Tujuan

Membangun struktur data responden dan parameter pajanan.

## Model

```text
Worker
├── id
├── code
├── is_active
├── created_at
└── updated_at
```

```text
ExposureProfile
├── id
├── worker
├── body_weight
├── exposure_time
├── exposure_frequency
├── exposure_duration
├── inhalation_rate
├── created_at
└── updated_at
```

Baseline:

```text
1 Worker
   ↓
1 ExposureProfile aktif
```

Belum ada relasi langsung:

```text
H2SReading → Worker
```

karena asosiasi ini dilakukan oleh ARKL calculation request.

## Pekerjaan

```text
[x] Worker model
[x] ExposureProfile model
[x] OneToOne relationship
[x] basic constraints
[x] domain validation
[x] migrations
[x] migrate
[x] admin registration
[x] model tests
[x] validation tests
[x] dummy create/read
```

## Data Privacy

Gunakan:

```text
PML-001
PML-002
PML-003
```

sebagai respondent code.

Jangan menyimpan NIK/alamat/telepon jika tidak dibutuhkan penelitian.

Status:

```text
PHASE 2 = DONE
```

---

# 8. Phase 3 — Layer 2 REST API

## Tujuan

Menyediakan REST API untuk React dan penggunaan internal penelitian.

## Endpoint

```text
GET    /api/v1/devices/
GET    /api/v1/devices/{id}/

GET    /api/v1/readings/
GET    /api/v1/readings/{id}/
GET    /api/v1/readings/latest/

POST   /api/v1/workers/
GET    /api/v1/workers/
GET    /api/v1/workers/{id}/

POST   /api/v1/exposure-profiles/
GET    /api/v1/exposure-profiles/
GET    /api/v1/exposure-profiles/{id}/
PATCH  /api/v1/exposure-profiles/{id}/
```

## Rules

`H2SReading` bersifat read-only melalui REST.

Telemetry masuk melalui MQTT, bukan melalui React.

Reading list menggunakan pagination.

Filtering dasar dapat menggunakan query parameter seperti:

```text
device_code
status
```

## Definition of Done

```text
[x] serializers
[x] viewsets/views
[x] /api/v1 versioning
[x] request validation
[x] reading pagination
[x] filtering
[x] POST Worker
[x] POST ExposureProfile
[x] PATCH ExposureProfile
[x] latest reading
[x] invalid request → 4xx
[x] OpenAPI
[x] Swagger
[x] no ARKL formula in views
```

Status:

```text
PHASE 3 = DONE
```

---

# 9. Phase 4 — Layer 3 Smart ARKL

## Tujuan

Membangun deterministic scientific calculation engine untuk H₂S inhalation risk assessment.

Scientific source of truth:

```text
ARKL_CALCULATION_SPEC.md
Version: 1.0.0-MVP
Status: MVP SCIENTIFIC LOCK
```

## 9.1 Phase 4A — Scientific Specification

Locked MVP contract:

```text
Pollutant               = H₂S
Route                   = inhalation
Sensor unit             = ppm
ARKL concentration      = mg/m³
Conversion              = 1 ppm = 1.40 mg/m³
RfC                     = 0.002 mg/m³

Body weight             = kg
Inhalation rate         = m³/hour
Exposure time           = hour/day
Exposure frequency      = day/year
Exposure duration       = year

Averaging time:
tavg = Dt × 365 days
```

Intake:

```text
             C × R × tE × fE × Dt
Intake = ───────────────────────────
                  Wb × tavg
```

RQ:

```text
RQ = Intake / RfC
```

Interpretation:

```text
RQ <= 1
→ WITHIN_REFERENCE_LEVEL

RQ > 1
→ ABOVE_REFERENCE_LEVEL
```

Realtime source:

```text
latest valid reading
```

Historical source:

```text
arithmetic mean readings
between start_time and end_time
```

Backend MVP menggunakan istilah:

```text
HISTORICAL
```

bukan actual lifetime monitoring.

Status:

```text
Phase 4A = DONE
```

---

# 10. Phase 4B — Core Calculation Engine

## Struktur

```text
arkl/services/
├── constants.py
├── conversion.py
├── validation.py
├── aggregation.py
├── intake.py
├── rq.py
├── interpretation.py
└── calculator.py
```

## Responsibilities

### constants.py

```text
H2S_PPM_TO_MG_M3
H2S_RFC_MG_M3
DAYS_PER_YEAR
ARKL_CALCULATION_VERSION
interpretation constants
```

### conversion.py

```text
ppm_to_mg_m3()
```

### validation.py

Validasi:

```text
concentration_ppm >= 0
body_weight > 0
0 <= exposure_time <= 24
0 <= exposure_frequency <= 365
exposure_duration > 0
inhalation_rate >= 0
```

### aggregation.py

```text
calculate_mean_concentration()
```

### intake.py

```text
calculate_averaging_time()
calculate_intake()
```

### rq.py

```text
calculate_rq()
```

### interpretation.py

```text
interpret_rq()
```

### calculator.py

Application orchestration:

```text
calculate_realtime_risk()
calculate_historical_risk()
```

## Numeric Strategy

Scientific calculation menggunakan:

```text
Decimal
```

Gunakan:

```python
Decimal(str(value))
```

Jangan:

```python
Decimal(value)
```

untuk input float.

Rule:

```text
DO NOT ROUND INTERMEDIATE VALUES
```

Status:

```text
Phase 4B = DONE
```

---

# 11. Phase 4C — ARKLResult Persistence

## Tujuan

Menyimpan immutable calculation snapshot secara konseptual agar hasil dapat direproduksi.

## Model

```text
ARKLResult
├── id
├── worker
├── reading nullable
├── calculation_type
├── concentration_ppm
├── concentration_mg_m3
├── body_weight
├── exposure_time
├── exposure_frequency
├── exposure_duration
├── inhalation_rate
├── averaging_time
├── intake
├── rfc
├── rq
├── interpretation
├── calculation_version
├── source_simulated
├── period_start
├── period_end
├── reading_count
└── created_at
```

Calculation types:

```text
REALTIME
HISTORICAL
```

Realtime:

```text
reading != null
```

Historical:

```text
reading = null
period_start != null
period_end != null
reading_count != null
```

Exposure values disimpan sebagai snapshot.

Jika ExposureProfile berubah setelah calculation:

```text
ARKLResult lama tidak berubah.
```

Status:

```text
Phase 4C = DONE
```

---

# 12. Phase 4D — Calculator Orchestration

## Realtime

```text
Worker
 +
Device
 ↓
ExposureProfile
 +
Latest deterministic H2SReading
 ↓
validate
 ↓
ppm → mg/m³
 ↓
Intake
 ↓
RQ
 ↓
Interpretation
 ↓
ARKLResult
```

## Historical

```text
Worker
 +
Device
 +
start_time/end_time
 ↓
readings in period
 ↓
mean ppm
 ↓
ppm → mg/m³
 ↓
Intake
 ↓
RQ
 ↓
Interpretation
 ↓
ARKLResult
```

Errors harus eksplisit:

```text
worker without ExposureProfile
device without reading
inactive device
invalid time range
empty historical readings
invalid exposure parameters
```

Status:

```text
Phase 4D = DONE
```

---

# 13. Phase 4E — ARKL REST API + OpenAPI

## Endpoint MVP

```text
POST /api/v1/arkl/realtime/
POST /api/v1/arkl/historical/

GET  /api/v1/arkl/results/
GET  /api/v1/arkl/results/{id}/
```

Realtime request:

```json
{
  "worker": 1,
  "device": 1
}
```

Historical request:

```json
{
  "worker": 1,
  "device": 1,
  "start_time": "2026-08-20T00:00:00+07:00",
  "end_time": "2026-08-20T08:00:00+07:00"
}
```

React tidak mengirim:

```text
Intake
RfC
RQ
interpretation
```

Backend menghitung semuanya.

## API Rules

```text
View
 ↓
Serializer
 ↓
calculator.py
 ↓
services
 ↓
ARKLResult
```

Tidak boleh ada formula dalam View.

## Current Checklist

```text
[x] serializers
[x] views
[x] urls
[x] calculator integration
[x] OpenAPI annotations

[ ] API tests final
[ ] Swagger final verification
```

Status:

```text
Phase 4E = IN PROGRESS
```

---

# 14. Phase 4F — Regression + End-to-End Validation

## Unit Tests

```text
conversion
validation
aggregation
intake
RQ
interpretation
```

## Persistence Tests

```text
ARKLResult snapshot
calculation version
simulated provenance
historical metadata
```

## Integration Tests

```text
realtime calculator
historical calculator
latest reading selection
invalid profile
invalid device
invalid period
```

## API Tests

```text
POST realtime
POST historical
GET result list
GET result detail
invalid input
filters
```

## End-to-End

```text
Wokwi
 ↓
MQTT
 ↓
Django ingestion
 ↓
H2SReading
 ↓
ARKL realtime endpoint
 ↓
Intake
 ↓
RQ
 ↓
ARKLResult
 ↓
Swagger / React
```

Definition of Done Phase 4:

```text
[ ] Realtime API works
[ ] Historical API works
[ ] Result list/detail works
[ ] Invalid input → clear 4xx
[ ] OpenAPI schema valid
[ ] Swagger works
[ ] Ruff clean
[ ] Django check clean
[ ] ARKL test suite green
[ ] full regression green
[ ] E2E verified
```

Jika semuanya terpenuhi:

```text
PHASE 4 = DONE
```




---




# 15. Phase 5 — Layer 4 Alert & Risk Management

## Tujuan

Layer 4 bertanggung jawab menggabungkan:

```text
Environmental Condition
        +
ARKLResult
        ↓
Deterministic Alert Engine
        ↓
Alert
        +
Risk Management Recommendation
```

Tujuan utama Phase 5 adalah menghasilkan:

- status alert yang deterministic;
- severity yang terdokumentasi;
- rekomendasi pengendalian risiko;
- lifecycle alert;
- mekanisme pencegahan duplicate/spam alert;
- output yang dapat digunakan langsung oleh React.

Layer ini tidak melakukan perhitungan ulang ARKL.

---

## 15.1 Scientific Separation

Layer 4 menerima dua dimensi yang berbeda.

### Environmental Dimension

Source:

```text
H2SReading
```

Informasi utama:

```text
ppm
level
status
simulated
received_at
device
```

Dimensi ini menjawab:

```text
"Bagaimana kondisi H₂S lingkungan saat ini?"
```

---

### Risk Dimension

Source:

```text
ARKLResult
```

Informasi utama:

```text
rq
interpretation
calculation_type
calculation_version
source_simulated
```

Dimensi ini menjawab:

```text
"Bagaimana skenario pajanan dibandingkan
dengan reference concentration?"
```

---

Kedua dimensi tidak boleh dianggap identik.

Contoh yang valid:

```text
Environmental status:
NORMAL

ARKL:
ABOVE_REFERENCE_LEVEL
```

Hal tersebut dimungkinkan karena Layer 3 memperhitungkan:

```text
concentration
+
exposure time
+
exposure frequency
```

dan tidak hanya melihat konsentrasi sesaat.

---

## 15.2 Input

Conceptual input:

```text
H2SReading
      +
ARKLResult
      ↓
Alert Engine
```

Minimum input environmental:

```text
ppm
level
status
device
simulated
```

Minimum input risk:

```text
rq
interpretation
calculation_type
calculation_version
source_simulated
```

Alert Engine tidak boleh menerima client-calculated severity sebagai source of truth.

---

## 15.3 Architecture

Target structure:

```text
alerts/
├── models.py
├── serializers.py
├── views.py
├── urls.py
├── admin.py
├── services/
│   ├── alert_engine.py
│   ├── recommendation.py
│   └── deduplication.py
└── tests/
    ├── test_alert_engine.py
    ├── test_recommendation.py
    ├── test_models.py
    └── test_api.py
```

Gunakan existing backend architecture:

```text
View
  ↓
Serializer
  ↓
Service
  ↓
Model / ORM
  ↓
SQLite
```

Jangan membuat tambahan abstraction layer apabila belum diperlukan.

---

## 15.4 Core Rules

Alert Engine wajib mengikuti aturan berikut:

```text
Alert Engine tidak menghitung ulang RQ.
Alert Engine tidak menghitung ulang Exposure Concentration.
Alert Engine tidak mengubah RfC.
Alert Engine tidak mengubah ARKL interpretation.
```

Layer 1 threshold harus tetap berasal dari specification/reference Layer 1.

Layer 3 risk interpretation harus menggunakan hasil `ARKLResult`.

Tidak boleh ada:

```text
medical diagnosis
ISPA probability prediction
clinical decision
```

Recommendation harus:

```text
rule-based
deterministic
documented
testable
```

AI boleh menjelaskan hasil Alert Engine, tetapi tidak boleh menentukan:

```text
RQ
risk interpretation
alert severity
risk status
scientific threshold
```

---

## 15.5 Alert Severity

Candidate machine-readable alert levels:

```text
NONE
LOW
MEDIUM
HIGH
CRITICAL
```

Namun severity matrix final harus dikunci setelah Layer 1 environmental status mapping diaudit.

Alert severity harus mempertimbangkan:

```text
Environmental Dimension
        +
Risk Dimension
```

dan bukan hanya satu nilai.

---

## 15.6 Candidate Decision Matrix

Initial candidate:

Environmental Status

ARKL Interpretation

Alert Level

NORMAL

WITHIN_REFERENCE_LEVEL

NONE

WARNING

WITHIN_REFERENCE_LEVEL

MEDIUM

DANGER

WITHIN_REFERENCE_LEVEL

HIGH

NORMAL

ABOVE_REFERENCE_LEVEL

MEDIUM

WARNING

ABOVE_REFERENCE_LEVEL

HIGH

DANGER

ABOVE_REFERENCE_LEVEL

CRITICAL

Status:

```text
CANDIDATE — NOT SCIENTIFICALLY LOCKED YET
```

Matrix harus diverifikasi terhadap:

```text
Layer 1 threshold specification
environmental status semantics
research risk-management requirements
```

sebelum implementasi final.

---

## 15.7 Risk Status

Candidate risk-management states:

```text
NO_ACTION_REQUIRED
MONITORING_REQUIRED
RISK_MANAGEMENT_REQUIRED
IMMEDIATE_ACTION_REQUIRED
```

Candidate mapping:

```text
NONE
→ NO_ACTION_REQUIRED

LOW
→ MONITORING_REQUIRED

MEDIUM
→ MONITORING_REQUIRED

HIGH
→ RISK_MANAGEMENT_REQUIRED

CRITICAL
→ IMMEDIATE_ACTION_REQUIRED
```

Mapping ini harus deterministic.

---

## 15.8 Recommendation Rules

Recommendation merupakan output rule-based dari alert severity dan risk status.

Candidate recommendation codes:

```text
MONITOR_H2S_LEVEL
REDUCE_EXPOSURE_DURATION
LIMIT_ACCESS_TO_EXPOSURE_AREA
USE_APPROPRIATE_PPE
INCREASE_ENVIRONMENTAL_MONITORING
NOTIFY_RESPONSIBLE_OPERATOR
TEMPORARY_AREA_AVOIDANCE
PERFORM_FURTHER_RISK_EVALUATION
```

Recommendation code lebih disukai daripada hardcoded long text di Alert Engine.

Contoh:

```text
recommendation_code
        ↓
React / API
        ↓
human-readable explanation
```

Hal ini memudahkan:

```text
translation
UI presentation
research documentation
future AI explanation
```

Recommendation tidak boleh dianggap sebagai:

```text
medical treatment
clinical advice
diagnosis
```

---

## 15.9 Alert Lifecycle

Minimum lifecycle:

```text
OPEN
  ↓
ACKNOWLEDGED
  ↓
RESOLVED
```

Meaning:

### OPEN

```text
Alert baru dan membutuhkan perhatian.
```

### ACKNOWLEDGED

```text
Alert telah diketahui oleh pengguna/operator.
```

### RESOLVED

```text
Alert telah ditutup karena kondisi atau tindak lanjut
sudah dianggap selesai.
```

Jangan menambahkan state lain sampai ada kebutuhan nyata.

---

## 15.10 Alert Deduplication

MQTT dapat mengirim telemetry dengan frekuensi tinggi.

Sistem tidak boleh membuat alert baru setiap telemetry masuk.

Minimum deduplication concept:

```text
same worker
+
same device
+
same alert level
+
existing OPEN alert
        ↓
do not create duplicate alert
```

Jika severity meningkat:

```text
MEDIUM
↓
HIGH
```

atau:

```text
HIGH
↓
CRITICAL
```

sistem harus memperlakukan kondisi tersebut sebagai:

```text
alert escalation
```

dan bukan sebagai duplicate biasa.

Strategi update/create final ditentukan pada implementation design Phase 5.

---

## 15.11 Realtime Alert Behaviour

Raw telemetry tidak otomatis menghasilkan ARKLResult setiap detik.

Alert evaluation direkomendasikan terjadi ketika:

```text
new valid ARKLResult exists
OR
environmental state changes
OR
risk state changes
OR
alert severity escalates
```

Tujuan:

```text
avoid alert spam
avoid unnecessary database writes
avoid repeated identical notifications
```

---

## 15.12 Realtime vs Historical ARKL

### REALTIME ARKL

Eligible untuk:

```text
realtime alert
risk-management recommendation
warning UI
future notification
```

### HISTORICAL ARKL

Eligible untuk:

```text
historical analysis
risk-management insight
research reporting
trend analysis
```

Historical calculation tidak otomatis menghasilkan emergency alert.

Default:

```text
HISTORICAL
→ analytical result

REALTIME
→ realtime alert eligible
```

---

## 15.13 Simulated Data Provenance

Jika input menggunakan:

```text
simulated = true
```

maka alert harus mempertahankan provenance.

Recommended:

```text
source_simulated = true
```

Alert simulated boleh digunakan untuk:

```text
development
testing
demonstration
E2E verification
```

tetapi UI tidak boleh menampilkannya sebagai data sensor fisik.

---

## 15.14 Alert Model

Recommended minimum model:

```text
Alert
├── id
├── worker
├── device
├── reading
├── arkl_result
│
├── environmental_status
├── environmental_level
├── concentration_ppm
│
├── rq
├── risk_interpretation
│
├── alert_level
├── risk_status
│
├── status
├── recommendation_codes
│
├── source_simulated
│
├── acknowledged_at
├── resolved_at
├── created_at
└── updated_at
```

Snapshot fields harus dipertimbangkan untuk menjaga auditability.

Alert lama tidak boleh berubah hanya karena source ARKL atau environmental data kemudian diperbarui.

---

## 15.15 Candidate API Output

```json
{
  "environment": {
    "ppm": 4.2,
    "status": "WARNING",
    "level": 2
  },
  "risk": {
    "rq": 1.42,
    "interpretation": "ABOVE_REFERENCE_LEVEL",
    "calculation_version": "1.1.0-MVP"
  },
  "alert": {
    "level": "HIGH",
    "risk_status": "RISK_MANAGEMENT_REQUIRED",
    "status": "OPEN"
  },
  "recommendations": [
    "REDUCE_EXPOSURE_DURATION",
    "USE_APPROPRIATE_PPE",
    "MONITOR_H2S_LEVEL"
  ],
  "source_simulated": false
}
```

React tidak menentukan:

```text
alert level
risk status
recommendation code
```

React hanya menampilkan hasil backend.

---

## 15.16 Candidate REST API

Minimum candidate endpoints:

```text
GET   /api/v1/alerts/
GET   /api/v1/alerts/{id}/

POST  /api/v1/alerts/evaluate/

PATCH /api/v1/alerts/{id}/acknowledge/
PATCH /api/v1/alerts/{id}/resolve/
```

Endpoint final harus mengikuti kebutuhan implementation dan tidak perlu dibuat seluruhnya apabila belum diperlukan.

---

## 15.17 AI Boundary

Allowed:

```text
Deterministic Alert
        ↓
Optional AI
        ↓
human-readable explanation
risk communication
education
summary
```

AI boleh:

```text
menjelaskan penyebab alert
meringkas rekomendasi
menghasilkan bahasa edukasi
membantu report narrative
```

AI tidak boleh:

```text
menghitung RQ
mengubah RfC
mengubah threshold
memilih alert level
menentukan risk status
membuat diagnosis
```

---

## 15.18 Observability

Gunakan existing observability infrastructure.

HTTP:

```text
existing global middleware
```

Service/background logging:

```text
smart_h2s.alerts
```

Jangan implement ulang:

```text
Request ID
request logging
error logging
performance monitoring
security audit
redaction
rotating logs
```

Alert log tidak boleh memuat data personal yang tidak diperlukan.

---

## 15.19 Testing Requirements

Minimum tests:

```text
alert engine
├── NORMAL + WITHIN
├── WARNING + WITHIN
├── DANGER + WITHIN
├── NORMAL + ABOVE
├── WARNING + ABOVE
└── DANGER + ABOVE

recommendation
├── deterministic mapping
├── expected codes
└── no medical recommendation

deduplication
├── duplicate OPEN alert
├── resolved alert allows new alert
└── severity escalation

lifecycle
├── OPEN
├── ACKNOWLEDGED
└── RESOLVED

persistence
├── source ARKLResult
├── environmental snapshot
├── risk snapshot
└── simulated provenance

API
├── list
├── detail
├── evaluate
├── acknowledge
├── resolve
└── invalid input
```

Full regression wajib memastikan Phase 5 tidak merusak:

```text
MQTT ingestion
Device API
Reading API
Worker API
ExposureProfile API
ARKL v1.1
core observability
```

---

## 15.20 Definition of Done

```text
[ ] Layer 1 environmental threshold/status audited

[ ] environmental dimension documented
[ ] risk dimension documented
[ ] environmental/risk dimensions remain separated

[ ] alert decision matrix locked
[ ] alert level deterministic
[ ] risk status deterministic

[ ] recommendation rules documented
[ ] recommendation codes implemented
[ ] no medical diagnosis/recommendation

[ ] Alert model implemented
[ ] provenance preserved
[ ] lifecycle implemented

[ ] deduplication implemented
[ ] alert escalation handled
[ ] repeated telemetry does not create alert spam

[ ] realtime ARKL integration works
[ ] historical ARKL does not create emergency alert by default

[ ] REST API implemented
[ ] React-compatible output

[ ] AI does not calculate risk or severity

[ ] unit tests pass
[ ] API tests pass
[ ] full regression passes

[ ] Ruff clean
[ ] format clean
[ ] Django check clean
[ ] OpenAPI clean
```

---

## 15.21 Phase 5 Implementation Order

```text
1. Audit Layer 1 status/threshold contract
        ↓
2. Lock alert decision matrix
        ↓
3. Lock risk-status mapping
        ↓
4. Define recommendation codes
        ↓
5. Implement alert_engine.py
        ↓
6. Implement recommendation.py
        ↓
7. Unit tests
        ↓
8. Alert model
        ↓
9. Migration
        ↓
10. Deduplication
        ↓
11. Lifecycle
        ↓
12. REST API
        ↓
13. OpenAPI
        ↓
14. Integration tests
        ↓
15. Full regression
        ↓
16. E2E
        ↓
17. Phase 5 lock
```

---

# 16. Phase 6 — Layer 5 Research & Reporting

## Tujuan

Layer 5 menyediakan data yang siap digunakan untuk:

```text
research analysis
charts
tables
statistics
recapitulation
export
publication
```

Layer ini hanya membaca data yang telah dihasilkan layer sebelumnya dan melakukan analytical aggregation.

Layer 5 tidak menghitung ulang scientific formula ARKL.

---

## 16.1 Data Sources

Primary sources:

```text
H2SReading
ExposureProfile
ARKLResult
Alert
```

Data flow:

```text
Layer 1
H2SReading
     │
     ├───────────────┐
     │               │
Layer 2              │
ExposureProfile      │
     │               │
     ▼               ▼
Layer 3           Layer 4
ARKLResult         Alert
     │               │
     └───────┬───────┘
             ▼
          Layer 5
     Research & Reporting
```

---

## 16.2 Backend Responsibilities

Backend bertanggung jawab terhadap:

```text
query
filtering
aggregation
statistics
summary
research dataset preparation
export
research API
```

Backend tidak bertanggung jawab terhadap final visual layout chart.

---

## 16.3 React Responsibilities

React bertanggung jawab terhadap:

```text
charts
tables
visualization
dashboard
filters UI
report preview
interactive exploration
```

Scientific aggregation tetap dilakukan di backend.

---

## 16.4 Candidate Endpoints

```text
GET /api/v1/research/h2s-summary/
GET /api/v1/research/h2s-trends/
GET /api/v1/research/risk-distribution/
GET /api/v1/research/arkl-results/
GET /api/v1/research/exposure-summary/
GET /api/v1/research/alert-summary/
```

Optional:

```text
GET /api/v1/research/export/
```

hanya jika export benar-benar dibutuhkan.

---

## 16.5 H₂S Summary

Candidate output:

```text
reading_count
minimum_ppm
maximum_ppm
mean_ppm
period_start
period_end
```

Additional statistics hanya ditambahkan jika diperlukan penelitian.

---

## 16.6 H₂S Trend

Output harus chart-ready.

Candidate:

```json
{
  "timestamp": "2026-08-20T08:00:00Z",
  "ppm": 4.21
}
```

Backend dapat melakukan aggregation/downsampling bila jumlah telemetry sudah terlalu besar.

Tidak perlu dilakukan sebelum ada performance need.

---

## 16.7 Risk Distribution

Candidate categories:

```text
WITHIN_REFERENCE_LEVEL
ABOVE_REFERENCE_LEVEL
```

Output dapat mencakup:

```text
count
percentage
```

Jangan mengubah kategori ARKL pada reporting layer.

---

## 16.8 Exposure Summary

Candidate analytical fields:

```text
worker_count
body_weight summary
exposure_time summary
exposure_frequency summary
exposure_duration summary
inhalation_rate summary
```

Data harus diperlakukan sebagai research data.

---

## 16.9 Alert Summary

Candidate:

```text
alert count
alert level distribution
open alerts
acknowledged alerts
resolved alerts
risk-management recommendation frequency
```

Simulated alert harus dapat dibedakan dari physical data.

---

## 16.10 Rules

Jangan duplikasi:

```text
ppm conversion
Exposure Concentration formula
RfC
RQ formula
alert decision matrix
```

Reporting hanya membaca hasil dari source layer.

Correct:

```text
ARKLResult.rq
        ↓
Research aggregation
```

Incorrect:

```text
Research API
        ↓
recalculate RQ
```

---

## 16.11 Filtering

Candidate filters:

```text
start_time
end_time
device
worker
calculation_type
risk_interpretation
alert_level
source_simulated
```

Filter hanya dibuat jika benar-benar dibutuhkan frontend/research.

---

## 16.12 Research Reproducibility

Output research harus mempertahankan informasi seperti:

```text
calculation_version
time range
source provenance
sample/readings count
```

Tujuannya supaya hasil dapat ditelusuri kembali.

---

## 16.13 Export

Candidate formats:

```text
CSV
XLSX
```

Implement export hanya jika diperlukan sebagai luaran penelitian.

Raw database dump tidak digunakan sebagai research export utama.

---

## 16.14 AI Boundary

Optional AI dapat digunakan untuk:

```text
research summary
narrative
trend explanation
report drafting
```

AI tidak boleh:

```text
mengubah raw data
mengubah RQ
mengubah calculation version
mengubah alert severity
menghasilkan statistik yang tidak berasal dari deterministic backend
```

---

## 16.15 Testing Requirements

Minimum:

```text
summary calculations
trend query
risk distribution
exposure summary
alert summary
filters
empty dataset behavior
simulated provenance
API serialization
```

Full regression tidak boleh merusak Layer 1–4.

---

## 16.16 Definition of Done

```text
[ ] historical H₂S summary
[ ] H₂S trend data
[ ] ARKL result recap
[ ] exposure summary
[ ] risk distribution
[ ] alert summary

[ ] time-range filtering
[ ] provenance preserved
[ ] calculation version available

[ ] export implemented bila diperlukan

[ ] React chart-ready API
[ ] no duplicated ARKL formula
[ ] no duplicated alert formula

[ ] unit tests
[ ] API tests
[ ] full regression

[ ] Ruff clean
[ ] format clean
[ ] Django check clean
[ ] OpenAPI clean
```

---

## 16.17 Phase 6 Implementation Order

```text
1. Define research output requirements
       ↓
2. Implement query/aggregation services
       ↓
3. Unit tests
       ↓
4. Research serializers
       ↓
5. REST API
       ↓
6. Filters
       ↓
7. React chart contract
       ↓
8. Export if required
       ↓
9. OpenAPI
       ↓
10. Full regression
       ↓
11. Research E2E
       ↓
12. Phase 6 lock
```

```

Perubahan terpenting untuk **Phase 5** adalah sekarang kita tidak sekadar punya `Alert Engine`, tetapi sudah jelas ada empat kontrak yang sebelumnya hilang:

```text
Decision Matrix
Lifecycle
Deduplication / Escalation
Recommendation Rules
```

Dan saya sengaja memberi status decision matrix:

```text
CANDIDATE — NOT SCIENTIFICALLY LOCKED YET
```

karena **langkah berikutnya bukan membuat `models.py`**, melainkan melakukan **audit ulang Layer 1 `ppm → level → status`** yang sekarang dikirim ESP32/MQTT. Setelah mapping Layer 1 itu terverifikasi, baru kita lock kombinasi:

```text
Environmental Status
        +
ARKL Interpretation
        ↓
Alert Level
```


# 16. Phase 6 — Layer 5 Research & Reporting

## Tujuan

Menyediakan research-ready data untuk grafik, tabel, statistik, export, dan publikasi.

## Backend Responsibilities

- query;
- aggregation;
- statistics;
- summary;
- export;
- research API.

## React Responsibilities

- charts;
- tables;
- visualization;
- dashboard;
- report preview.

## Candidate Endpoints

```text
GET /api/v1/research/h2s-summary/
GET /api/v1/research/h2s-trends/
GET /api/v1/research/risk-distribution/
GET /api/v1/research/arkl-results/
GET /api/v1/research/exposure-summary/
```

## Rules

Jangan duplikasi ARKL formula di reporting.

Reporting hanya membaca:

```text
H2SReading
ExposureProfile
ARKLResult
AlertResult
```

dan melakukan analytical aggregation.

## Definition of Done

```text
[ ] historical H2S summary
[ ] trend data
[ ] ARKL result recap
[ ] exposure summary
[ ] risk distribution
[ ] export bila diperlukan
[ ] React chart-ready API
[ ] tests
```

---

# 17. AI Boundary

AI Agent bukan bagian deterministic calculation engine.

Allowed:

```text
ARKLResult
    ↓
AI
    ↓
natural-language explanation
summary
research narrative
risk communication
```

Forbidden:

```text
Telemetry
 ↓
LLM
 ↓
Intake / RQ
```

AI tidak boleh menentukan:

```text
Intake
RfC
RQ
alert threshold
```

kecuali di masa depan hanya digunakan sebagai assistant di atas deterministic result.

---

# 18. Data Provenance

Semua reading memiliki:

```text
simulated = true/false
```

Wokwi:

```text
simulated = true
```

ARKL result menyimpan:

```text
source_simulated
```

Sistem tidak boleh menampilkan data simulasi sebagai sensor fisik tanpa penandaan.

Jika nanti historical period menggabungkan sumber berbeda, provenance strategy dapat diperluas melalui versioned migration.

---

# 19. Scientific Change Control

Perubahan material pada:

- formula Intake;
- conversion factor;
- RfC;
- unit;
- averaging time;
- aggregation strategy;
- RQ interpretation;

wajib memperbarui:

```text
ARKL_CALCULATION_SPEC.md
calculation version
constants
unit tests
API documentation bila terpengaruh
research documentation
```

Jangan mengubah formula hanya di code.

---

# 20. Testing Strategy

Testing adalah bagian setiap phase.

Pembagian:

```text
Unit
├── pure function
└── validation

Persistence
└── model/database behavior

Integration
└── service orchestration

API
└── HTTP contract

Feature / E2E
└── complete data flow
```

Jangan mengejar 100% coverage framework.

Prioritaskan:

```text
devices/services/
exposure/services/
arkl/services/
alerts/services/
research/services/
```

---

# 21. Test Structure

Untuk app yang sudah besar, gunakan folder test terpisah.

Contoh ARKL:

```text
arkl/tests/
├── __init__.py
├── test_conversion.py
├── test_validation.py
├── test_intake.py
├── test_rq.py
├── test_interpretation.py
├── test_aggregation.py
├── test_models.py
├── test_calculator.py
└── test_api.py
```

Gunakan nama berdasarkan responsibility, bukan urutan eksekusi.

---

# 22. Checklist Sebelum Commit

Wajib:

```bash
ruff check .
ruff format --check .
pytest
python manage.py check
pip-audit
```

Checklist:

```text
[ ] no secrets in source
[ ] .env not committed
[ ] migration committed when model changes
[ ] tests added/updated
[ ] no leftover print()
[ ] no sensitive log payload
[ ] views thin
[ ] business logic in services
[ ] scientific formula only in ARKL services
[ ] API docs updated
[ ] calculation specification updated when required
```

---

# 23. Git Workflow Solo Developer

Gunakan workflow sederhana:

```text
main
 ↑
feature/*
fix/*
refactor/*
```

Contoh:

```text
feature/mqtt-ingestion
feature/exposure-profile
feature/arkl-engine
feature/arkl-api
feature/alert-engine
fix/latest-reading-order
fix/mqtt-reconnect
refactor/arkl-tests
```

Flow:

```text
create branch
   ↓
small implementation
   ↓
tests
   ↓
lint
   ↓
commit
   ↓
merge when stable
```

Hindari Git flow kompleks untuk solo developer.

---

# 24. Definition of Done Keseluruhan Backend

Backend MVP baseline dianggap lengkap jika:

```text
[x] MQTT telemetry masuk otomatis
[x] H2S reading tersimpan
[x] Worker/ExposureProfile tersedia
[x] Layer 2 REST API tersedia

[ ] Smart ARKL REST API final
[ ] ARKL E2E final
[ ] Alert Engine
[ ] Research API

[x] Observability infrastructure
[x] Security logging baseline
[x] API documentation infrastructure
[x] scientific calculation versioning
[x] simulated-data provenance
```

Final baseline:

```text
[ ] React dapat mengonsumsi seluruh API
[ ] tidak ada scientific formula di frontend
[ ] tidak ada sensitive data di log
[ ] no unnecessary dependency
[ ] full regression green
```

---

# 25. Current Project Status

```text
Phase 0 — Backend Foundation
✅ DONE

Phase 1 — Devices + MQTT Ingestion
✅ DONE

Phase 2 — Layer 2 Data Models
✅ DONE

Phase 3 — Layer 2 REST API
✅ DONE

Phase 4 — Smart ARKL
🟡 IN PROGRESS

├── 4A Scientific Specification
│   ✅ DONE
│
├── 4B Core Calculation Engine
│   ✅ DONE
│
├── 4C ARKLResult Persistence
│   ✅ DONE
│
├── 4D Calculator Orchestration
│   ✅ DONE
│
├── 4E REST API + OpenAPI
│   🟡 IN PROGRESS
│
└── 4F Regression + E2E
    ⬜ NEXT

Phase 5 — Alert & Risk Management
⬜ NOT STARTED

Phase 6 — Research & Reporting
⬜ NOT STARTED
```

---

# 26. Urutan Kerja Saat Ini

Current work:

```text
1. Finalize ARKL API tests
        ↓
2. Ruff
        ↓
3. Django check
        ↓
4. OpenAPI schema generation
        ↓
5. Swagger verification
        ↓
6. Full regression
        ↓
7. E2E:
   Wokwi
      ↓
   MQTT
      ↓
   H2SReading
      ↓
   ARKL API
      ↓
   ARKLResult
        ↓
8. Lock Phase 4 DONE
        ↓
9. Start Phase 5 Alert Engine
```

---

# 27. Daily Development Rule

Jika bingung harus mengerjakan apa:

```text
1. Baca phase aktif.
2. Pilih satu acceptance item.
3. Implementasikan perubahan minimum.
4. Jalankan focused test.
5. Jalankan lint.
6. Jalankan regression relevan.
7. Periksa log/error.
8. Commit.
9. Update SOP/checklist.
10. Baru lanjut item berikutnya.
```

Jangan:

```text
Phase 4 belum selesai
 ↓
langsung Phase 6 reporting
 ↓
kembali Phase 5
 ↓
ubah MQTT
```

Yang benar:

```text
Foundation
 ↓
MQTT
 ↓
Data
 ↓
REST API
 ↓
ARKL
 ↓
Alert
 ↓
Reporting
```

---

# 28. Roadmap Ringkas

Phase

Nama

Hasil Utama

Status

0

Backend Foundation

Django + observability siap

✅

1

Devices + MQTT

Telemetry masuk backend

✅

2

Layer 2 Models

Worker + Exposure data

✅

3

Layer 2 REST API

React dapat membaca/mengelola data

✅

4

Smart ARKL

Deterministic risk calculation

🟡

5

Alert & Risk Management

Early warning + risk action

⬜

6

Research & Reporting

Research-ready data & API

⬜

---

# 29. System Flow

Alur utama sistem:

```text
Wokwi / Physical Sensor
        ↓
MQTT
        ↓
Django MQTT Ingestion
        ↓
Device + H2SReading
        ↓
Layer 2 Exposure Data
        ↓
Worker + ExposureProfile
        ↓
Smart ARKL Engine
        ├── Validate
        ├── Convert
        ├── Aggregate
        ├── Intake
        ├── RQ
        └── Interpret
        ↓
ARKLResult
        ↓
Alert & Risk Management
        ↓
Research & Reporting
        ↓
React
```

Observability melintang pada seluruh backend:

```text
HTTP ───────┐
MQTT ───────┼──→ OBSERVABILITY
Services ───┘
```

---

# 30. Prinsip Akhir

> Jangan mengejar jumlah fitur. Kejar alur data yang benar, formula yang reproducible, kontrak API yang jelas, test yang relevan, dan sistem yang mudah dirawat.

Mnemonic utama:

```text
Ukur
 ↓
Terima
 ↓
Validasi
 ↓
Simpan
 ↓
Hitung
 ↓
Uji
 ↓
Peringatkan
 ↓
Laporkan
```

Engineering principle:

```text
THE MVP MAY EVOLVE,
BUT IT MUST NEVER HIDE ITS ASSUMPTIONS.

FORMULAS ARE VERSIONED.
CONSTANTS ARE SOURCED.
UNITS ARE EXPLICIT.
RESULTS ARE REPRODUCIBLE.
OBSERVABILITY IS SHARED.
AI DOES NOT DEFINE THE RISK.
```

```

Versi ini sudah lebih cocok dijadikan **dokumen hidup utama proyek**. Perubahan paling besar dibanding SOP v1 adalah Phase test tidak lagi berdiri sendiri, Phase ARKL dipecah menjadi 4A–4F, `lifetime` diganti menjadi `historical` untuk MVP, scientific lock dan versioning sudah formal, serta observability diperlakukan sebagai infrastructure global yang tidak boleh dibuat ulang. 
```
