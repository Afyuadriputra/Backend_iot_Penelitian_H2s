Anda bertindak sebagai Senior Software Architect + Backend Engineer + AI/Research System Auditor.

Anda bertindak sebagai Senior Software Architect + Project Manager + Technical Documentation Engineer.

Repository:

D:\Kuliah\joki\dosen\buk reni\projek\Backend

TUGAS ANDA:

Audit repository aktual lalu buat / perbarui SATU dokumen status proyek terbaru agar saya mudah mengetahui:

- proyek ini sebenarnya sedang berada di tahap mana;
- layer mana yang selesai;
- layer mana yang reopened;
- layer mana yang paused;
- task yang sudah selesai;
- task yang belum selesai;
- blocker;
- technical debt;
- keputusan scientific yang belum dikunci;
- test / quality status;
- endpoint yang sudah aktif;
- endpoint yang belum aktif;
- file yang sedang relevan;
- urutan pekerjaan selanjutnya.

Dokumen ini akan menjadi "project handoff / source of truth" untuk melanjutkan development di chat atau agent lain.

==================================================
IMPORTANT SOURCE OF TRUTH
=========================

Prioritas kebenaran teknis:

1. Repository aktual
2. Migrations
3. Tests
4. Runtime configuration
5. schema.yml
6. Dokumentasi/catatan

Jangan mempercayai status lama apabila bertentangan dengan repository aktual.

Untuk keputusan ilmiah ARKL yang belum final:
JANGAN menyimpulkan sendiri.
Tandai sebagai:

NEEDS SCIENTIFIC DECISION

==================================================
PROJECT CONTEXT
===============

Project adalah backend Django untuk:

IoT H₂S Environmental Monitoring
+
Data & Exposure Management
+
Smart ARKL
+
Alert & Risk Management
+
Research & Reporting

Target pengguna ke depan:

ADMIN
OPERATOR
RESEARCHER
WORKER / PEMULUNG

Namun authentication/authorization belum menjadi core existing dan harus diaudit berdasarkan repository.

Konsep layer:

Layer 1 — IoT Environmental Monitoring
Layer 2 — Data & Exposure Management
Layer 3 — Smart ARKL
Layer 4 — Alert & Risk Management
Layer 5 — Research & Reporting

==================================================
CURRENT IMPORTANT PROJECT DECISION
==================================

Perhatian khusus pada Layer 3.

Repository saat ini diketahui memiliki ARKL:

calculation_version = 1.1.0-MVP

Formula runtime harus Anda audit langsung.

Sebelumnya ditemukan formula kira-kira:

C_mg/m3 = ppm × conversion factor

EC = C × (ET / 24) × (EF / 365)

RQ = EC / RfC

Namun penelitian akan mempertimbangkan revisi ke formula intake inhalasi ARKL:

I = (C × R × tE × fE × Dt) / (Wb × tavg)

RQ = I / reference value

Parameter:

C    = concentration
R    = inhalation rate
tE   = exposure time
fE   = exposure frequency
Dt   = exposure duration
Wb   = body weight
tavg = averaging time

JANGAN implementasikan rumus baru.

JANGAN mengarang tavg.

JANGAN mengubah RfC/reference value.

JANGAN menghapus hasil ARKL lama.

Yang harus Anda lakukan hanya mencatat:

- formula runtime aktual;
- calculation version aktual;
- mismatch dengan formula penelitian baru;
- scientific decision yang masih dibutuhkan;
- file yang nantinya terdampak.

Karena formula belum final, status Layer 3 kemungkinan:

REOPENED — SCIENTIFIC REVISION REQUIRED

Tetapi verifikasi berdasarkan repository.

==================================================
LAYER 4 IMPORTANT STATUS
========================

Alert Engine sebelumnya sudah memiliki:

Alert levels:
NONE
LOW
MEDIUM
HIGH
CRITICAL

Risk status:
NO_ACTION_REQUIRED
MONITORING_REQUIRED
RISK_MANAGEMENT_REQUIRED
IMMEDIATE_ACTION_REQUIRED

Lifecycle:
OPEN
ACKNOWLEDGED
RESOLVED

Features:

- deterministic decision matrix;
- recommendation codes;
- persistence;
- deduplication;
- escalation;
- lifecycle;
- REST API;
- E2E tests.

Alert Engine TIDAK BOLEH menghitung ulang ARKL/RQ/RfC.

Jika ARKL formula berubah nanti, Layer 4 seharusnya menjalani regression, bukan otomatis diubah.

Audit status aktualnya.

==================================================
LAYER 5 IMPORTANT STATUS
========================

Research app sudah ada.

Audit apakah sudah ada:

- H2S summary;
- H2S trends;
- time filter;
- device filter;
- simulated/physical filter;
- ARKL recap;
- risk distribution;
- exposure summary;
- alert summary;
- export.

Periksa juga apakah:

research.urls

sudah benar-benar di-include dari:

config/urls.py

dan apakah research endpoints sudah masuk:

schema.yml

Jangan hanya melihat file lokal research/urls.py.

==================================================
OBSERVABILITY
=============

Core observability existing harus dianggap reusable.

Audit:

- Request ID
- request logging
- error logging
- performance monitoring
- security audit
- redaction
- rotating logs
- MQTT/background logger

Jangan implement ulang.

==================================================
DO NOT MODIFY PROJECT LOGIC
===========================

Pada task ini:

JANGAN:

- refactor business code;
- mengubah formula;
- membuat migration;
- mengubah database;
- mengubah .env;
- install dependency;
- memperbaiki bug;
- menambah endpoint;
- menambah role;
- menjalankan destructive command.

Anda hanya boleh:

- inspect;
- run safe/read-only verification;
- membuat/update file dokumentasi status proyek.

==================================================
SAFE VERIFICATION
=================

Jika runtime tersedia, boleh menjalankan:

pytest -v
ruff check .
ruff format --check .
python manage.py check
python manage.py spectacular --file schema.yml
pip-audit

Tetapi:

- jangan mengklaim PASS bila command tidak berhasil dijalankan;
- bedakan VERIFIED vs INFERRED;
- jangan menjalankan migration;
- jangan memodifikasi database produksi.

Jika environment agent tidak kompatibel dengan Windows .venv:
catat sebagai NOT VERIFIED FROM CURRENT ENVIRONMENT.

==================================================
TARGET FILE
===========

Buat atau update file:

catatan/PROJECT_STATUS.md

Jika file tersebut sudah ada:
REFRESH berdasarkan repository aktual.

Jangan membuat banyak file status yang isinya tumpang tindih.

==================================================
FORMAT PROJECT_STATUS.md
========================

Gunakan struktur berikut secara lengkap:

# SMART H2S ARKL — PROJECT STATUS

## 1. Project Identity

Tuliskan:

- tujuan project;
- backend stack;
- database;
- protocol IoT;
- current architecture style.

## 2. Current Overall Status

Buat tabel:

| Layer | Name | Status | Notes |
| ----- | ---- | ------ | ----- |

Status hanya gunakan:

LOCKED
DONE
IN PROGRESS
REOPENED
PAUSED
NOT STARTED

Contoh jangan diikuti tanpa audit:

Layer 1 | IoT Monitoring | DONE
Layer 2 | Data & Exposure | DONE
Layer 3 | Smart ARKL | REOPENED
Layer 4 | Alert | LOCKED
Layer 5 | Research | PAUSED/IN PROGRESS

Tentukan berdasarkan repository aktual.

## 3. Current Development Position

Tulis satu kalimat sangat jelas:

"Project saat ini berada pada ..."

Lalu diagram:

Completed
↓
Current
↓
Next
↓
Later

## 4. Layer 1 — IoT Environmental Monitoring

Catat:

Implemented:

- ...

Verified:

- ...

Remaining:

- ...

Future physical IoT work:

- ...

Technical debt:

- message id/idempotency
- source timestamp
- calibration
- physical sensor transition
  hanya jika repository mendukung temuan tersebut.

## 5. Layer 2 — Data & Exposure Management

Catat:

Models:

- Device
- H2SReading
- Worker
- ExposureProfile

Actual fields penting.

Implemented API.

Remaining work.

Role-related future impact.

## 6. Layer 3 — Smart ARKL

WAJIB DETAIL.

### Current Runtime Formula

Tulis formula aktual persis berdasarkan code.

### Current Version

calculation_version = ...

### Inputs Actually Used

...

### Inputs Stored But Not Used

...

### Current Output

...

### Scientific Revision Under Consideration

Tuliskan formula intake yang direncanakan:

I = ...

RQ = ...

Tetapi tandai:

NOT IMPLEMENTED
NEEDS SCIENTIFIC DECISION

### Missing Scientific Decisions

Contoh:

- exact tavg for non-carcinogenic exposure;
- exact reference value/RfC compatibility and units;
- formula transcription verification;
- scientific source/version.

Jangan mengarang jawabannya.

### Expected Impact

List file/layer yang nanti terdampak.

## 7. Layer 4 — Alert & Risk Management

Catat:

- rule version;
- environmental mapping;
- final matrix;
- risk status;
- recommendation;
- persistence;
- deduplication;
- escalation;
- lifecycle;
- API;
- E2E.

Status apakah LOCKED atau tidak berdasarkan test/source.

Tuliskan juga:

"Jika ARKL v2 dibuat, Layer 4 membutuhkan regression but not automatic rule rewrite."

## 8. Layer 5 — Research & Reporting

Pisahkan:

IMPLEMENTED
PARTIAL
MISSING

Audit:

H2S summary
H2S trends
ARKL recap
risk distribution
exposure summary
alert summary
export

Catat apakah URL root sudah aktif.

## 9. End-to-End Current Flow

Buat diagram sesuai implementasi AKTUAL.

Contoh:

MQTT
↓
H2SReading
↓
manual/caller ARKL API
↓
ARKLResult
↓
manual/caller Alert evaluate API
↓
Alert
↓
Research

Jika tidak ada automation langsung:
tulis eksplisit.

## 10. REST API Inventory

Kelompokkan actual endpoint:

Devices
Exposure
ARKL
Alerts
Research
Docs

Bedakan:

ACTIVE
LOCAL ONLY / NOT PUBLISHED
MISSING

## 11. Database Relationship

Buat diagram:

Device
H2SReading
Worker
ExposureProfile
ARKLResult
Alert

Catat on_delete policy yang penting.

## 12. Testing Status

Berikan:

- jumlah test bila dapat diverifikasi;
- per-app count jika dapat dihitung;
- latest runtime result jika dapat dijalankan.

Gunakan tabel:

| Check | Status | Evidence |
| ----- | ------ | -------- |

Status:

VERIFIED PASS
VERIFIED FAIL
NOT RUN
INFERRED

Checks:

pytest
ruff
format
Django check
OpenAPI
pip-audit

## 13. Locked Components

List yang jangan diubah sembarangan.

Contoh:

- MQTT payload contract
- observability
- Alert Engine rule version
- historical ARKL records
- API v1 prefix

Hanya masukkan bila benar berdasarkan code.

## 14. Reopened Components

Terutama ARKL scientific calculation jika memang sesuai audit.

Tuliskan alasan REOPENED.

## 15. Paused Work

Jika Phase 6 perlu dipause karena ARKL formula belum final:
catat.

Jangan menganggap paused jika repository menunjukkan development sedang lanjut tanpa dependency.

## 16. Backlog / Remaining Tasks

Gunakan prioritas:

P0 — BLOCKER
P1 — HIGH
P2 — MEDIUM
P3 — OPTIONAL

Format:

### P0

- [ ] ...

### P1

- [ ] ...

### P2

- [ ] ...

### P3

- [ ] ...

Task harus konkret, bukan kalimat abstrak.

Contoh:

- [ ] Lock tavg non-carcinogenic from approved scientific source.
- [ ] Decide ARKL v2 reference value/unit compatibility.
- [ ] Create versioned ARKL migration only after formula approval.
- [ ] Run full alert regression after ARKL v2.
- [ ] Finish research ARKL recap.
- [ ] Add authentication/authorization.
- [ ] Add Worker ownership.
- [ ] Prepare physical IoT calibration.

Tetapi sesuaikan dengan repository aktual.

## 17. Current Blockers

Tulis setiap blocker dengan:

Blocker:
Why:
Required decision:
Blocks which task:

## 18. Technical Debt

Gunakan severity:

CRITICAL
HIGH
MEDIUM
LOW

Jangan membuat debt palsu.

## 19. Authentication & Role Future Plan

Current auth status:
...

Future roles:

ADMIN
OPERATOR
RESEARCHER
WORKER

Recommended relation:

Django User
↓ optional link
Worker

Catat permission/ownership requirement.

JANGAN implementasikan.

## 20. Physical IoT Transition

List:

Already reusable:
...

Must change:
...

Must verify scientifically:
...

Contoh:

firmware
sensor calibration
simulated=false
device identity
MQTT resilience
timestamp/idempotency

## 21. Recommended Next Tasks

Tuliskan maksimal 10 task berurutan.

Harus sangat konkret.

Contoh format:

1. ...
2. ...
3. ...

## 22. Do Not Do Yet

List hal yang harus ditunda.

Misalnya:

- do not finish risk reporting before ARKL formula lock;
- do not overwrite calculation version 1.1;
- do not add AI diagnosis;
- do not migrate Worker directly into auth model.

Sesuaikan audit.

## 23. Handoff Summary

Buat ringkasan maksimal 20 baris yang dapat saya copy ke agent/chat baru.

Harus mencakup:

- current stage;
- locked layer;
- reopened layer;
- paused layer;
- main blocker;
- immediate next task;
- important versions;
- do-not-touch components.

==================================================
TASK COMPLETION REQUIREMENT
===========================

Setelah file selesai:

1. Tampilkan path file:
   catatan/PROJECT_STATUS.md
2. Ringkas apa yang berubah dari status lama.
3. Tampilkan:

   - CURRENT PHASE
   - NEXT TASK
   - MAIN BLOCKER
   - LOCKED COMPONENTS
4. JANGAN mulai coding task berikutnya.
5. Berhenti dan tunggu approva

Saya memiliki project Django backend untuk sistem monitoring H₂S berbasis IoT yang terintegrasi dengan Analisis Risiko Kesehatan Lingkungan (ARKL), alert/risk management, dan research/reporting.

Root project:

D:\\Kuliah\\joki\\dosen\\buk reni\\projek\\Backend

Struktur utama:

Backend/

├── alerts/

├── arkl/

├── catatan/

├── config/

├── core/

├── devices/

├── exposure/

├── logs/

├── requirements/

├── research/

├── .env

├── .env.example

├── db.sqlite3

├── manage.py

├── pyproject.toml

├── pytest.ini

└── schema.yml

TUGAS UTAMA ANDA:

JANGAN LANGSUNG MENGUBAH CODE.

Langkah pertama adalah melakukan AUDIT dan PEMAHAMAN MENYELURUH terhadap repository ini.

Saya ingin Anda menjelaskan kepada saya:

1\. Project ini sebenarnya melakukan apa.

2\. Tujuan masing-masing app/module.

3\. Alur data end-to-end.

4\. Bagaimana hubungan antar layer.

5\. Bagaimana backend menerima data IoT.

6\. Bagaimana data H₂S disimpan.

7\. Bagaimana data worker/pemulung dan profil pajanan digunakan.

8\. Bagaimana Smart ARKL dihitung.

9\. Bagaimana ARKLResult digunakan oleh Alert Engine.

10\. Bagaimana deduplication, escalation, dan lifecycle alert bekerja.

11\. Bagaimana Research & Reporting membaca data layer sebelumnya.

12\. Endpoint REST API yang tersedia.

13\. Test coverage dan kualitas repository saat ini.

14\. Bagian yang sudah stabil/locked.

15\. Bagian yang masih dalam development.

16\. Technical debt, inkonsistensi, bug potensial, atau architectural smell.

17\. Dampak jika rumus ARKL diganti.

18\. Dampak jika nanti ditambahkan authentication dan role:

\- ADMIN

\- OPERATOR

\- RESEARCHER

\- WORKER / PEMULUNG

19\. Bagian mana yang HARUS dipertahankan dan tidak boleh direfactor sembarangan.

20\. Rekomendasi urutan development selanjutnya.

\==================================================

DOMAIN SYSTEM

\==================================================

Secara konseptual sistem terdiri dari 5 layer:

Layer 1 — IoT Environmental Monitoring

Layer 2 — Data & Exposure Management

Layer 3 — Smart ARKL

Layer 4 — Alert & Risk Management

Layer 5 — Research & Reporting

Alur konseptual:

IoT Sensor / Wokwi

↓

MQTT

↓

H2SReading

↓

Worker + ExposureProfile

↓

Smart ARKL

↓

ARKLResult

↓

Alert Engine

↓

Alert + Recommendation

↓

Research & Reporting

↓

React Frontend

\==================================================

LAYER 1 — IOT

\==================================================

IoT menggunakan ESP32/Wokwi untuk simulasi H₂S.

Telemetry dikirim via MQTT.

Payload umumnya memiliki:

device\_id

ppm

adc

filtered\_adc

level

status

uptime\_ms

simulated

Backend harus menyimpan data valid sebagai H2SReading.

Simulated data harus tetap dapat dibedakan dari physical sensor data.

JANGAN mengubah MQTT contract tanpa alasan teknis yang kuat.

\==================================================

LAYER 2 — DATA & EXPOSURE

\==================================================

Model utama:

Device

H2SReading

Worker

ExposureProfile

ExposureProfile memiliki parameter seperti:

body\_weight

exposure\_time

exposure\_frequency

exposure\_duration

inhalation\_rate

Worker saat ini merupakan domain entity/subjek pajanan.

Worker BUKAN authentication user.

Jika nanti ditambahkan login untuk pemulung, sebaiknya User Account dihubungkan dengan Worker, bukan mengganti Worker menjadi auth model secara sembarangan.

\==================================================

LAYER 3 — SMART ARKL

\==================================================

PERHATIAN:

Layer 3 adalah scientific calculation layer.

Jangan berasumsi rumus yang ada saat ini sudah final tanpa audit code.

Rumus ARKL yang sedang dipertimbangkan sebagai rumus penelitian adalah intake inhalasi:

I = (C × R × fE × Dt) / (Wb × tavg)

dengan:

C = concentration

R = inhalation rate

tE = exposure time

fE = exposure frequency

Dt = exposure duration

Wb = body weight

tavg = averaging time

dan karakterisasi risiko:

RQ = I / RfC

Namun repository saat ini mungkin masih menggunakan ARKL calculation version sebelumnya.

AUDIT IMPLEMENTASI AKTUAL.

Jangan langsung mengganti formula.

Laporkan secara jelas:

\- formula aktual di code;

\- field yang digunakan;

\- field yang hanya disimpan sebagai snapshot;

\- calculation\_version;

\- perbedaan antara implementation existing dengan formula intake di atas;

\- file yang harus berubah jika formula diganti.

Jangan mengarang nilai tavg.

Jangan mengubah RfC tanpa scientific source.

RQ bukan probability penyakit dan bukan diagnosis ISPA.

\==================================================

LAYER 4 — ALERT & RISK MANAGEMENT

\==================================================

Layer 4 sudah cukup matang dan sebisa mungkin dianggap stable.

Alert Engine tidak boleh:

\- menghitung ulang RQ;

\- menghitung ulang ARKL;

\- mengubah RfC;

\- menentukan diagnosis;

\- mengubah scientific threshold secara sembarangan.

Layer 4 membaca:

H2SReading

ARKLResult

dan menghasilkan deterministic:

Alert Level:

NONE

LOW

MEDIUM

HIGH

CRITICAL

Risk Status:

NO\_ACTION\_REQUIRED

MONITORING\_REQUIRED

RISK\_MANAGEMENT\_REQUIRED

IMMEDIATE\_ACTION\_REQUIRED

Lifecycle:

OPEN

ACKNOWLEDGED

RESOLVED

Deduplication harus mencegah repeated identical active alert.

ACKNOWLEDGED masih dianggap active.

RESOLVED memungkinkan alert baru.

Severity increase merupakan escalation.

Jangan mengubah decision matrix tanpa menemukan kebutuhan domain/scientific yang valid.

Alert rule version existing harus diaudit.

\==================================================

LAYER 5 — RESEARCH & REPORTING

\==================================================

Research layer harus bersifat read-oriented.

Ia membaca:

H2SReading

ExposureProfile

ARKLResult

Alert

dan melakukan:

query

filter

aggregation

statistics

trend preparation

reporting

Research layer TIDAK BOLEH menduplikasi:

ARKL formula

alert decision matrix

environmental threshold

Audit current research app.

Cek apakah sudah terdapat:

h2s summary

h2s trends

ARKL recap

risk distribution

exposure summary

alert summary

Pisahkan:

IMPLEMENTED

PARTIAL

NOT IMPLEMENTED

\==================================================

OBSERVABILITY

\==================================================

Core observability sudah ada.

Jangan implement ulang tanpa alasan.

Audit keberadaan:

Request ID

request logging

error logging

performance monitoring

security audit

redaction

rotating logs

HTTP feature harus memakai middleware existing.

Background/MQTT logging harus mengikuti logger existing.

\==================================================

ARCHITECTURE PRINCIPLES

\==================================================

Pertahankan arsitektur sederhana:

View

↓

Serializer

↓

Service

↓

Model / ORM

↓

SQLite

Gunakan prinsip:

SOLID

KISS

YAGNI

JANGAN menambahkan tanpa kebutuhan nyata:

Repository Pattern

DI Container

Celery

Redis

Channels

Kafka

Microservices

Event Bus

Pandas dalam request path

Data Warehouse

\==================================================

SECURITY

\==================================================

JANGAN:

\- membaca atau menampilkan value dari .env;

\- mencetak secret;

\- menampilkan password/token;

\- memasukkan secret ke hasil audit.

Anda boleh memeriksa NAMA environment variable bila memang perlu, tetapi jangan tampilkan nilainya.

\==================================================

AUDIT ORDER

\==================================================

Lakukan audit dengan urutan berikut:

1\. Inspect root repository.

2\. Inspect config/settings.py.

3\. Inspect config/urls.py.

4\. Inspect pyproject.toml.

5\. Inspect pytest.ini.

6\. Inspect requirements.

7\. Inspect devices app.

8\. Inspect exposure app.

9\. Inspect arkl app.

10\. Inspect alerts app.

11\. Inspect research app.

12\. Inspect core observability.

13\. Inspect migrations.

14\. Inspect tests.

15\. Inspect schema.yml bila relevan.

16\. Jalankan static reasoning terhadap dependency flow.

17\. Jika environment memungkinkan, jalankan test suite READ-ONLY.

18\. Jangan modify files.

\==================================================

OUTPUT YANG SAYA MAU

\==================================================

Setelah audit, berikan laporan dengan format ini:

\# 1. Executive Summary

Jelaskan dalam bahasa sederhana:

\- project ini apa;

\- siapa pengguna potensialnya;

\- problem yang diselesaikan;

\- kondisi repository saat ini.

\# 2. Actual Architecture

Buat diagram text:

IoT

↓

MQTT

↓

Device/H2SReading

↓

Exposure

↓

ARKL

↓

Alert

↓

Research

↓

Frontend

Tetapi sesuaikan berdasarkan IMPLEMENTASI AKTUAL, bukan asumsi saya.

\# 3. Application / Module Map

Untuk setiap app:

config

core

devices

exposure

arkl

alerts

research

jelaskan:

\- responsibility;

\- model;

\- services;

\- API;

\- tests;

\- dependency.

\# 4. End-to-End Data Flow

Jelaskan langkah demi langkah dari MQTT message sampai research API.

\# 5. Database Model Relationship

Jelaskan relasi:

Device

H2SReading

Worker

ExposureProfile

ARKLResult

Alert

Buat diagram relational text.

\# 6. Smart ARKL Audit

WAJIB DETAIL.

Tuliskan:

Current formula in repository:

...

Current calculation version:

...

Inputs actually used:

...

Inputs stored but not used:

...

Outputs:

...

Scientific assumptions:

...

Mismatch dengan formula intake inhalasi:

...

Files impacted if formula changes:

...

Jangan modify code.

\# 7. Alert Engine Audit

Jelaskan:

\- environmental mapping;

\- decision matrix;

\- risk-status mapping;

\- recommendations;

\- persistence;

\- deduplication;

\- escalation;

\- lifecycle;

\- API;

\- rule version.

\# 8. Research Layer Audit

Pisahkan:

Implemented:

...

Partial:

...

Missing:

...

\# 9. REST API Map

List semua endpoint berdasarkan urls.py dan schema.

Kelompokkan:

Devices

Exposure

ARKL

Alerts

Research

Documentation

\# 10. Testing & Quality Status

Laporkan:

\- total tests bila dapat diverifikasi;

\- test distribution per app;

\- Ruff config;

\- Django check;

\- OpenAPI;

\- pip-audit jika tersedia.

Jangan mengklaim PASS jika tidak dijalankan.

Pisahkan:

VERIFIED

INFERRED

NOT CHECKED

\# 11. Locked / Stable Components

List code yang jangan disentuh tanpa alasan kuat.

\# 12. In-Progress Components

List fitur yang belum selesai.

\# 13. Risks & Technical Debt

Prioritaskan:

CRITICAL

HIGH

MEDIUM

LOW

Jangan membuat masalah palsu hanya untuk mengisi daftar.

\# 14. ARKL Formula Migration Impact

Analisis bila formula diubah menjadi:

I = (C × R × fE × Dt) / (Wb × tavg)

RQ = I / RfC

Jelaskan dampak ke:

Layer 1

Layer 2

Layer 3

Layer 4

Layer 5

tests

database

API

frontend

\# 15. Future Role Architecture

Analisis penambahan role:

ADMIN

OPERATOR

RESEARCHER

WORKER

Dengan prinsip:

Auth User

↓

optional link

↓

Worker

Worker tidak otomatis menjadi auth model.

Jelaskan authorization/ownership yang dibutuhkan.

\# 16. Recommended Development Roadmap

Susun urutan yang paling aman berdasarkan repository aktual.

Contoh, JANGAN IKUTI BUTA-BUTA:

Scientific formula lock

↓

ARKL migration

↓

Alert regression

↓

Research continuation

↓

Authentication

↓

Role/permissions

↓

Frontend

↓

Physical IoT transition

↓

Deployment

Tentukan urutan berdasarkan temuan aktual.

\# 17. Files That Would Change

JANGAN mengubahnya.

Hanya list:

MODIFY

NEW

VERIFY

DO NOT TOUCH

untuk perubahan rumus ARKL + role system.

\==================================================

CRITICAL RULE

\==================================================

Jangan melakukan coding atau refactor pada tahap audit.

Jangan membuat file.

Jangan menjalankan migration.

Jangan menghapus file.

Jangan mengubah database.

Jangan mengubah formula.

Jangan mengubah .env.

Jangan install dependency.

Jangan menjalankan command destructive.

Pertama pahami project secara aktual.

Jika dokumentasi/chat saya berbeda dengan repository:

REPOSITORY + TESTS + MIGRATIONS adalah source of truth teknis.

Tetapi untuk keputusan scientific yang belum final:

jangan menyimpulkan sendiri.

Tandai sebagai NEEDS SCIENTIFIC DECISION.

Setelah selesai, berhenti dan tunggu approval saya sebelum melakukan perubahan.
