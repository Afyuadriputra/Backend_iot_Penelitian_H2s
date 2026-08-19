# ARKL Calculation Specification

**Project:** Smart H₂S — Environmental Health Risk Assessment
**Module:** Layer 3 — Smart ARKL Services
**Document:** `ARKL_CALCULATION_SPEC.md`
**Version:** `1.0.0-MVP`
**Status:** `MVP SCIENTIFIC LOCK`
**Last Updated:** 20 August 2026

---

# 1. Purpose

Dokumen ini merupakan **source of truth metodologi perhitungan ARKL untuk MVP Smart H₂S**.

Tujuannya adalah memastikan bahwa seluruh perhitungan:

- deterministic;
- reproducible;
- memiliki satuan eksplisit;
- memiliki konstanta yang terdokumentasi;
- tidak bergantung pada AI/LLM;
- tidak tersebar di React, View, Serializer, atau Model;
- dapat diuji dengan known-case unit tests;
- dapat direvisi melalui versioning apabila metodologi penelitian diperbarui.

Prinsip utama:

```text
DEFINE THE SCIENCE
        ↓
IMPLEMENT THE SCIENCE
        ↓
TEST THE IMPLEMENTATION
```

Bukan:

```text
IMPLEMENT FIRST
        ↓
ASSUME THE SCIENCE
```

---

# 2. MVP Scope

MVP Layer 3 melakukan analisis risiko kesehatan lingkungan untuk:

```text
Pollutant       : Hydrogen Sulfide / H₂S
Exposure route  : Inhalation
Risk type       : Non-carcinogenic
Primary metrics : Intake dan Risk Quotient (RQ)
```

Sistem tidak melakukan:

```text
medical diagnosis
prediction of ISPA probability
clinical diagnosis
individual disease prediction
```

ARKL digunakan sebagai **risk characterization**, bukan alat diagnosis.

---

# 3. Calculation Pipeline

Alur utama:

```text
H₂S Reading
     +
Exposure Profile
     ↓
Input Validation
     ↓
Unit Conversion
     ↓
Concentration Selection
     ↓
Intake Calculation
     ↓
RfC
     ↓
RQ Calculation
     ↓
Risk Interpretation
     ↓
ARKLResult
```

Implementasi backend:

```text
React
  ↓
API View
  ↓
Serializer
  ↓
ARKL Service
  ↓
Calculation Engine
  ↓
Model / ORM
  ↓
SQLite
```

---

# 4. Architectural Rules

Formula ARKL hanya boleh berada di:

```text
arkl/services/
```

Target struktur:

```text
arkl/
├── models.py
├── serializers.py
├── views.py
├── urls.py
└── services/
    ├── constants.py
    ├── conversion.py
    ├── validation.py
    ├── aggregation.py
    ├── intake.py
    ├── rq.py
    ├── interpretation.py
    └── calculator.py
```

Formula tidak boleh berada di:

```text
React
views.py
serializers.py
models.py
AI / LLM
```

Views hanya mengatur HTTP flow.

Serializers hanya menangani representation dan request validation.

Model hanya menangani persistence.

---

# 5. Deterministic Requirement

Calculation engine wajib deterministic.

```text
same inputs
+
same constants
+
same calculation version
=
same result
```

Dilarang menggunakan:

```text
randomness
LLM output
generative AI
hidden defaults
non-versioned constants
```

dalam proses calculation.

---

# 6. Scientific Separation

Layer 1 dan Layer 3 menggunakan referensi untuk tujuan yang berbeda.

## 6.1 Layer 1 — Environmental / Safety Monitoring

Layer 1 digunakan untuk:

- realtime H₂S monitoring;
- OLED;
- LED;
- buzzer;
- status lingkungan;
- operational warning;
- informasi efek konsentrasi H₂S.

Referensi dapat mencakup:

```text
NIOSH REL
OSHA PEL
NIOSH IDLH
literatur efek fisiologis H₂S
```

Contoh:

```text
NIOSH IDLH = 100 ppm
```

Nilai tersebut **bukan RfC ARKL**.

---

## 6.2 Layer 3 — ARKL Risk Assessment

Layer 3 menggunakan:

```text
Concentration
Exposure Parameters
Intake
RfC
RQ
```

Occupational exposure limits seperti:

```text
NIOSH REL
OSHA PEL
NIOSH IDLH
```

tidak digunakan sebagai penyebut RQ.

---

# 7. Data Sources

## 7.1 Environmental Data

Sumber:

```text
Device
   ↓
H2SReading
```

Field utama:

```text
ppm
device
received_at
simulated
```

Raw telemetry dapat diterima dengan frekuensi tinggi.

ARKL tidak harus menghitung setiap raw reading sebagai satu hasil risiko.

---

## 7.2 Exposure Data

Sumber:

```text
Worker
   ↓
ExposureProfile
```

Parameter:

```text
body_weight
exposure_time
exposure_frequency
exposure_duration
inhalation_rate
```

Nilai parameter berasal dari:

```text
data responden
atau
input penelitian
```

Tidak ada default responden yang dibuat oleh developer.

---

# 8. H₂S Concentration

## 8.1 Sensor Unit

Layer 1 menghasilkan:

```text
ppm
```

Status:

```text
LOCKED
```

---

## 8.2 ARKL Calculation Unit

ARKL menggunakan konsentrasi:

```text
mg/m³
```

Status:

```text
LOCKED
```

Alasan utama:

RfC H₂S yang digunakan dalam MVP dinyatakan dalam:

```text
mg/m³
```

---

# 9. H₂S Unit Conversion

Faktor konversi MVP:

```text
1 ppm H₂S = 1.40 mg/m³
```

Formula:

```text
C_mg_m3 = C_ppm × 1.40
```

Constant:

```text
H2S_PPM_TO_MG_M3 = 1.40
```

Status:

```text
LOCKED
```

Source category:

```text
CDC / NIOSH
NIOSH Pocket Guide to Chemical Hazards
Hydrogen Sulfide
```

Contoh:

```text
10 ppm
↓
10 × 1.40
↓
14.00 mg/m³
```

Implementation target:

```text
arkl/services/conversion.py
```

---

# 10. MVP Intake Equation

Formula yang dikunci untuk MVP:

```text
             C × R × tE × fE × Dt
Intake = ───────────────────────────
                  Wb × tavg
```

Parameter:

```text
C     = H₂S concentration
R     = inhalation rate
tE    = exposure time
fE    = exposure frequency
Dt    = exposure duration
Wb    = body weight
tavg  = averaging time
```

Status:

```text
LOCKED FOR MVP v1
```

---

# 11. Parameter Units

## 11.1 Concentration — C

```text
Symbol : C
Unit   : mg/m³
Source : H2SReading.ppm converted to mg/m³
```

Status:

```text
LOCKED
```

---

## 11.2 Inhalation Rate — R

```text
Model field : inhalation_rate
Symbol      : R
Unit        : m³/hour
```

Status:

```text
LOCKED FOR MVP
```

Nilai harus berasal dari:

```text
ExposureProfile
```

Tidak ada hidden default.

---

## 11.3 Exposure Time — tE

```text
Model field : exposure_time
Symbol      : tE
Meaning     : duration of exposure per working/exposure day
Unit        : hour/day
```

Status:

```text
LOCKED FOR MVP
```

Domain candidate:

```text
0 <= tE <= 24
```

Validation maksimum 24 dapat diterapkan karena unit telah dikunci menjadi hour/day.

---

## 11.4 Exposure Frequency — fE

```text
Model field : exposure_frequency
Symbol      : fE
Meaning     : number of exposure days per year
Unit        : day/year
```

Status:

```text
LOCKED FOR MVP
```

Domain:

```text
0 <= fE <= 365
```

---

## 11.5 Exposure Duration — Dt

```text
Model field : exposure_duration
Symbol      : Dt
Meaning     : number of years exposed
Unit        : year
```

Status:

```text
LOCKED FOR MVP
```

Constraint:

```text
Dt >= 0
```

---

## 11.6 Body Weight — Wb

```text
Model field : body_weight
Symbol      : Wb
Unit        : kg
```

Status:

```text
LOCKED
```

Constraint:

```text
Wb > 0
```

Tidak ada default body weight.

---

# 12. Averaging Time

Untuk MVP non-carcinogenic calculation:

```text
tavg = Dt × 365
```

Unit:

```text
day
```

Status:

```text
LOCKED FOR MVP
```

Dengan demikian:

```text
tavg_days = exposure_duration_years × 365
```

Jika:

```text
Dt = 10 years
```

maka:

```text
tavg = 10 × 365
     = 3650 days
```

Implementation target:

```text
calculate_averaging_time()
```

atau calculation internal yang equivalent.

---

# 13. Dimensional Contract

Input:

```text
C   = mg/m³
R   = m³/hour
tE  = hour/day
fE  = day/year
Dt  = year
Wb  = kg
tavg = day
```

Intermediate:

```text
R × tE
=
m³/hour × hour/day
=
m³/day
```

Kemudian:

```text
C × R × tE
=
mg/m³ × m³/day
=
mg/day
```

Formula engine harus menjaga contract unit ini secara eksplisit.

Developer tidak boleh mengganti unit suatu field tanpa:

```text
updating this specification
+
calculation version
+
tests
```

---

# 14. Reference Concentration — RfC

MVP menggunakan:

```text
H₂S RfC = 0.002 mg/m³
```

Constant:

```text
H2S_RFC_MG_M3 = 0.002
```

Status:

```text
LOCKED FOR MVP v1
```

Primary reference:

```text
United States Environmental Protection Agency
Integrated Risk Information System — IRIS
Hydrogen Sulfide
```

RfC digunakan sebagai reference concentration untuk inhalation non-carcinogenic risk assessment.

RfC bukan:

```text
NIOSH REL
OSHA PEL
IDLH
```

---

# 15. Risk Quotient

Formula:

```text
       Intake
RQ = ─────────
        RfC
```

atau:

```text
RQ = Intake / RfC
```

Status:

```text
LOCKED
```

Implementation target:

```text
arkl/services/rq.py
```

Function target:

```python
calculate_rq()
```

Requirement:

```text
RfC > 0
```

dan unit Intake harus compatible dengan reference calculation contract.

---

# 16. RQ Interpretation

MVP menggunakan dua machine-readable interpretation states.

## RQ <= 1

```text
WITHIN_REFERENCE_LEVEL
```

Meaning:

```text
Calculated non-carcinogenic risk does not exceed
the reference level for the evaluated exposure scenario.
```

---

## RQ > 1

```text
ABOVE_REFERENCE_LEVEL
```

Meaning:

```text
Calculated exposure scenario exceeds the reference level
and requires further risk evaluation and/or risk management.
```

Status:

```text
LOCKED FOR MVP
```

---

# 17. Forbidden Risk Interpretation

RQ bukan probabilitas penyakit.

Dilarang mengatakan:

```text
RQ = 1.5
→ kemungkinan sakit 50%
```

Dilarang mengatakan:

```text
RQ > 1
→ pasti mengalami ISPA
```

Dilarang mengatakan:

```text
RQ < 1
→ pasti aman dari seluruh efek kesehatan
```

Correct concept:

```text
RQ = risk characterization relative to reference level
```

Bukan:

```text
clinical diagnosis
```

---

# 18. Realtime ARKL

MVP menyediakan realtime risk calculation.

## Concentration Source

Realtime calculation menggunakan:

```text
latest valid H₂S reading
```

Pipeline:

```text
Latest valid H2SReading.ppm
        ↓
ppm_to_mg_m3()
        ↓
ExposureProfile
        ↓
calculate_intake()
        ↓
calculate_rq()
        ↓
interpret_rq()
```

Status:

```text
LOCKED FOR MVP
```

Target service:

```python
calculate_realtime_risk()
```

---

# 19. Definition of Valid Reading

Untuk MVP, valid reading minimal memenuhi:

```text
reading exists
ppm >= 0
device is active
payload has passed MQTT ingestion validation
```

`simulated=true` tidak membuat reading invalid.

Namun provenance harus tetap dibawa ke hasil ARKL.

---

# 20. Historical ARKL

MVP menyediakan historical risk scenario berdasarkan data sensor pada periode tertentu.

Concentration aggregation:

```text
arithmetic mean
```

Formula:

```text
                    Σ C
C_historical = ─────────────
                    n
```

dengan:

```text
C = valid reading concentration
n = number of readings
```

Status:

```text
LOCKED FOR MVP
```

Pipeline:

```text
Selected historical readings
        ↓
Arithmetic mean ppm
        ↓
ppm → mg/m³
        ↓
ExposureProfile
        ↓
Intake
        ↓
RQ
        ↓
Interpretation
```

Target:

```python
calculate_historical_risk()
```

---

# 21. Terminology: Historical vs Lifetime

Backend MVP menggunakan istilah:

```text
historical
```

untuk kalkulasi berdasarkan kumpulan telemetry aktual pada interval tertentu.

Istilah:

```text
lifetime
```

tidak boleh digunakan untuk menyatakan bahwa sistem memiliki pemantauan sepanjang hidup seseorang jika data tersebut tidak tersedia.

Dalam metodologi penelitian, lifetime scenario dapat dikembangkan kemudian sebagai skenario terpisah.

---

# 22. Historical Time Range

Historical calculation harus menerima batas waktu eksplisit:

```text
start_time
end_time
```

Query:

```text
received_at >= start_time
received_at <= end_time
```

Jika tidak ada reading dalam range:

```text
calculation must fail explicitly
```

Engine tidak boleh:

```text
return 0 concentration
```

secara diam-diam.

---

# 23. Raw Telemetry Frequency

MQTT dapat menghasilkan sekitar:

```text
1 reading / second
```

ARKL historical tidak menghitung seluruh raw readings sebagai hasil risiko terpisah.

Raw readings hanya menjadi dataset untuk menghasilkan:

```text
mean concentration
```

pada range yang diminta.

Optimisasi/downsampling belum diperlukan untuk MVP selama SQLite masih memenuhi kebutuhan PoC.

---

# 24. Simulated Data Provenance

Current Wokwi data menggunakan:

```text
simulated = true
```

Data simulated tetap boleh digunakan untuk:

```text
development
integration testing
MVP demonstration
calculation verification
```

Hasil ARKL harus menyimpan provenance.

Field:

```text
source_simulated
```

Status:

```text
LOCKED
```

Jika source reading simulated:

```text
source_simulated = true
```

Sistem tidak boleh menyamarkan data simulasi sebagai data sensor fisik.

---

# 25. ARKLResult

`ARKLResult` digunakan sebagai immutable calculation snapshot secara konseptual.

Minimum fields:

```text
ARKLResult
├── id
├── worker
├── reading
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
└── created_at
```

Untuk historical calculation, hubungan ke single reading dapat:

```text
nullable
```

karena result berasal dari aggregate readings.

Jika diperlukan, historical result menyimpan:

```text
period_start
period_end
reading_count
```

---

# 26. Snapshot Requirement

ARKLResult harus menyimpan parameter calculation sebagai snapshot.

Contoh:

```text
Worker PML-001
body_weight = 55 kg
```

ARKL result dibuat.

Kemudian profil diubah menjadi:

```text
body_weight = 58 kg
```

Historical ARKL result lama harus tetap menyimpan:

```text
55 kg
```

agar calculation lama tetap reproducible.

---

# 27. Calculation Type

MVP minimum:

```text
REALTIME
HISTORICAL
```

Recommended enum:

```text
REALTIME
HISTORICAL
```

Jangan menambahkan tipe calculation lain sampai diperlukan.

---

# 28. Calculation Version

Constant:

```text
ARKL_CALCULATION_VERSION = "1.0.0-MVP"
```

Setiap ARKLResult wajib menyimpan:

```text
calculation_version
```

Tujuan:

- auditability;
- reproducibility;
- methodology change tracking;
- scientific traceability.

Jika rumus atau konstanta berubah secara material:

```text
calculation version must change
```

---

# 29. Constants

Target `constants.py`:

```text
H2S_PPM_TO_MG_M3 = 1.40

H2S_RFC_MG_M3 = 0.002

DAYS_PER_YEAR = 365

ARKL_CALCULATION_VERSION = "1.0.0-MVP"
```

Gunakan numeric representation yang deterministic.

Recommended:

```text
Decimal
```

untuk calculation engine.

---

# 30. Numeric Strategy

ARKL engine menggunakan:

```text
Decimal
```

untuk:

```text
unit conversion
averaging time
intake
RfC
RQ
```

Tujuannya menghindari uncontrolled binary floating-point variation.

Input ORM FloatField dapat dikonversi menggunakan:

```python
Decimal(str(value))
```

Bukan:

```python
Decimal(value)
```

untuk nilai float.

---

# 31. Rounding Strategy

Rule:

```text
DO NOT ROUND INTERMEDIATE VALUES
```

Pipeline:

```text
raw input
   ↓
Decimal conversion
   ↓
full precision calculation
   ↓
stored result
   ↓
presentation rounding
```

API/UI boleh membatasi decimal display.

Calculation engine tidak boleh melakukan presentation rounding.

---

# 32. Basic Validation Rules

MVP validation:

```text
concentration_ppm >= 0

body_weight > 0

0 <= exposure_time <= 24

0 <= exposure_frequency <= 365

exposure_duration >= 0

inhalation_rate >= 0

RfC > 0
```

Untuk calculation yang membutuhkan averaging time:

```text
exposure_duration > 0
```

karena:

```text
tavg = Dt × 365
```

dan denominator tidak boleh nol.

---

# 33. Missing Inputs

Calculation engine tidak boleh menggunakan implicit defaults.

Jika required parameter tidak tersedia:

```text
raise explicit domain validation error
```

Contoh:

```text
ARKLValidationError
```

Tidak boleh:

```text
None → 0
missing body_weight → assumed 55 kg
missing R → hardcoded default
```

---

# 34. Intake Calculation Contract

Target function:

```python
calculate_intake(
    *,
    concentration_mg_m3,
    inhalation_rate_m3_hour,
    exposure_time_hour_day,
    exposure_frequency_day_year,
    exposure_duration_year,
    body_weight_kg,
)
```

Function menghitung averaging time:

```text
tavg = exposure_duration_year × 365
```

kemudian:

```text
             C × R × tE × fE × Dt
Intake = ───────────────────────────
                  Wb × tavg
```

Function harus:

- pure;
- deterministic;
- tidak membaca database;
- tidak membaca HTTP request;
- tidak memanggil AI;
- tidak melakukan logging data pribadi yang tidak diperlukan.

---

# 35. RQ Calculation Contract

Target:

```python
calculate_rq(
    *,
    intake,
    rfc=H2S_RFC_MG_M3,
)
```

Formula:

```text
RQ = Intake / RfC
```

Validation:

```text
intake >= 0
rfc > 0
```

Function harus pure dan deterministic.

---

# 36. Interpretation Contract

Target:

```python
interpret_rq(rq)
```

Output:

```text
WITHIN_REFERENCE_LEVEL
```

jika:

```text
RQ <= 1
```

Output:

```text
ABOVE_REFERENCE_LEVEL
```

jika:

```text
RQ > 1
```

No medical diagnosis.

---

# 37. Aggregation Contract

Target:

```python
calculate_mean_concentration(readings)
```

Input:

```text
collection of valid H₂S concentrations
```

Output:

```text
arithmetic mean concentration
```

Empty collection:

```text
must raise explicit error
```

Do not silently return:

```text
0
```

---

# 38. Realtime Calculator Contract

Target:

```python
calculate_realtime_risk(
    *,
    reading,
    exposure_profile,
)
```

Conceptual orchestration:

```text
validate reading
validate exposure profile
        ↓
ppm → mg/m³
        ↓
calculate intake
        ↓
calculate RQ
        ↓
interpret RQ
        ↓
persist ARKLResult
```

Calculation service may use persistence orchestration, but core mathematical functions remain pure.

---

# 39. Historical Calculator Contract

Target:

```python
calculate_historical_risk(
    *,
    worker,
    readings,
    exposure_profile,
    period_start,
    period_end,
)
```

Conceptual flow:

```text
validate readings
      ↓
mean ppm
      ↓
ppm → mg/m³
      ↓
calculate intake
      ↓
calculate RQ
      ↓
interpret RQ
      ↓
persist ARKLResult
```

Store:

```text
period_start
period_end
reading_count
```

where supported by the model.

---

# 40. AI Boundary

Optional AI functionality may use deterministic ARKL result for:

```text
explanation
summary
risk communication
research narrative
report generation
```

AI may not calculate:

```text
Intake
RfC
RQ
```

Correct:

```text
Deterministic Engine
        ↓
ARKLResult
        ↓
Optional AI Explanation
```

Incorrect:

```text
Telemetry
   ↓
LLM
   ↓
RQ
```

---

# 41. Observability

Existing core observability must be reused.

HTTP:

```text
existing global middleware
```

ARKL service/application logs:

```text
smart_h2s.arkl
```

Do not rebuild:

```text
Request ID middleware
request logging
error logging
security audit
performance middleware
redaction
rotating log infrastructure
```

Sensitive worker data must not be unnecessarily emitted to log files.

---

# 42. REST API Target

After calculation engine is tested, MVP may expose:

```text
POST /api/v1/arkl/realtime/
POST /api/v1/arkl/historical/

GET  /api/v1/arkl/results/
GET  /api/v1/arkl/results/{id}/
```

Optional API naming can be refined during REST implementation.

Views must not contain calculation formula.

---

# 43. Realtime Request Concept

Example conceptual request:

```json
{
  "worker": 1,
  "device": 1
}
```

Backend resolves:

```text
worker
↓
ExposureProfile

device
↓
latest valid H2SReading
```

Then deterministic calculation runs.

Do not require React to send calculated Intake/RQ.

---

# 44. Historical Request Concept

Example:

```json
{
  "worker": 1,
  "device": 1,
  "start_time": "2026-08-20T00:00:00+07:00",
  "end_time": "2026-08-20T08:00:00+07:00"
}
```

Backend:

```text
query readings
↓
mean concentration
↓
ARKL calculation
↓
ARKLResult
```

---

# 45. Known-Case Tests

Mandatory tests:

```text
ppm conversion:
0 ppm
10 ppm
fractional ppm
negative ppm
non-numeric input

validation:
zero/negative body weight
exposure_time > 24
exposure_frequency > 365
zero exposure duration where calculation requires tavg
invalid inhalation rate

intake:
known manually calculated case
zero concentration
deterministic repeated calculation

RQ:
RQ < 1
RQ = 1
RQ > 1
zero intake
invalid RfC

interpretation:
exact threshold behavior

aggregation:
single reading
multiple readings
empty readings

persistence:
snapshot values
calculation version
simulated provenance
historical metadata
```

---

# 46. Full Regression Requirement

Phase 4 changes must not break:

```text
MQTT ingestion
Device API
Reading API
Worker API
ExposureProfile API
core observability
```

Required quality gate:

```text
ruff check
pytest
python manage.py check
```

All existing tests must remain green.

---

# 47. Source Hierarchy

Priority:

## Tier 1

```text
US EPA IRIS
CDC / NIOSH
official environmental health risk assessment guidance
```

## Tier 2

```text
peer-reviewed scientific journals
```

## Tier 3

Other references may support documentation but should not silently override authoritative constants.

---

# 48. MVP Scientific Lock

Current locked configuration:

```text
Pollutant
H₂S
LOCKED

Exposure route
Inhalation
LOCKED

Sensor unit
ppm
LOCKED

Calculation concentration unit
mg/m³
LOCKED

Conversion
1 ppm = 1.40 mg/m³
LOCKED

RfC
0.002 mg/m³
LOCKED FOR MVP

Body weight
kg
LOCKED

Inhalation rate
m³/hour
LOCKED FOR MVP

Exposure time
hour/day
LOCKED FOR MVP

Exposure frequency
day/year
LOCKED FOR MVP

Exposure duration
year
LOCKED FOR MVP

Averaging time
Dt × 365 days
LOCKED FOR MVP

Intake equation
(C × R × tE × fE × Dt) / (Wb × tavg)
LOCKED FOR MVP

RQ
Intake / RfC
LOCKED

Realtime concentration
latest valid reading
LOCKED FOR MVP

Historical concentration
arithmetic mean of selected readings
LOCKED FOR MVP

RQ <= 1
WITHIN_REFERENCE_LEVEL

RQ > 1
ABOVE_REFERENCE_LEVEL
```

---

# 49. MVP Assumptions

Beberapa keputusan merupakan **MVP methodological assumptions**, bukan klaim bahwa tidak ada metodologi alternatif.

MVP assumption list:

```text
R uses m³/hour
tE uses hour/day
fE uses day/year
Dt uses year
non-carcinogenic tavg = Dt × 365 days
realtime uses latest valid concentration
historical uses arithmetic mean concentration
```

Jika penelitian kemudian menetapkan metode berbeda:

```text
do not silently modify existing engine
```

Buat:

```text
new calculation version
+
updated specification
+
new known-case tests
```

---

# 50. Change Control

Perubahan material pada:

```text
formula
unit
RfC
conversion constant
averaging time
aggregation method
interpretation threshold
```

wajib memperbarui:

```text
ARKL_CALCULATION_SPEC.md
calculation version
constants
unit tests
API documentation if affected
research documentation
```

---

# 51. Implementation Status

Dengan scientific lock ini:

```text
constants.py                      ALLOWED
conversion.py                     ALLOWED
validation.py                     ALLOWED
aggregation.py                    ALLOWED

intake.py                         ALLOWED
rq.py                             ALLOWED
interpretation.py                 ALLOWED
calculator.py                     ALLOWED

ARKLResult                        ALLOWED
Realtime ARKL API                 ALLOWED
Historical ARKL API               ALLOWED

Known-case tests                  REQUIRED
Full regression tests             REQUIRED
```

Scientific implementation gate untuk MVP:

```text
OPEN
```

---

# 52. Phase 4 Development Checklist

## Scientific Specification

```text
[x] H₂S defined
[x] Inhalation pathway defined
[x] Concentration units defined
[x] ppm conversion locked
[x] RfC locked for MVP
[x] Exposure parameter units locked
[x] Averaging time locked
[x] Intake formula locked
[x] RQ formula locked
[x] Interpretation locked
[x] Realtime concentration strategy locked
[x] Historical aggregation strategy locked
```

## Core Engine

```text
[ ] constants.py
[ ] conversion.py
[ ] validation.py
[ ] aggregation.py
[ ] intake.py
[ ] rq.py
[ ] interpretation.py
[ ] calculator.py
```

## Persistence

```text
[ ] ARKLResult finalized
[ ] Calculation type
[ ] Calculation version
[ ] Source simulated provenance
[ ] Snapshot parameters
[ ] Historical period metadata
```

## API

```text
[ ] Realtime calculation endpoint
[ ] Historical calculation endpoint
[ ] Result list endpoint
[ ] Result detail endpoint
[ ] OpenAPI documentation
```

## Testing

```text
[ ] Unit conversion tests
[ ] Validation tests
[ ] Known intake calculation
[ ] Known RQ calculation
[ ] RQ interpretation tests
[ ] Aggregation tests
[ ] Realtime calculator tests
[ ] Historical calculator tests
[ ] Persistence tests
[ ] Invalid API input tests
[ ] Full regression suite
```

---

# 53. Definition of Done — Phase 4 MVP

Phase 4 dianggap selesai ketika:

```text
[ ] calculate_intake() tersedia dan tested
[ ] calculate_rq() tersedia dan tested
[ ] interpret_rq() tersedia dan tested
[ ] calculate_realtime_risk() tersedia
[ ] calculate_historical_risk() tersedia

[ ] ppm dikonversi secara deterministic
[ ] averaging time dihitung secara deterministic
[ ] historical mean dihitung secara deterministic

[ ] ARKLResult menyimpan calculation snapshot
[ ] calculation version tersimpan
[ ] simulated provenance tersimpan

[ ] realtime endpoint bekerja
[ ] historical endpoint bekerja

[ ] invalid input menghasilkan 4xx yang jelas
[ ] tidak ada rumus ARKL di View
[ ] tidak ada rumus ARKL di Model
[ ] tidak ada rumus ARKL di React
[ ] AI tidak menghitung Intake/RQ

[ ] Ruff clean
[ ] Django check clean
[ ] seluruh test suite pass
```

---

# 54. Next Development Step

Scientific gate MVP telah terbuka.

Urutan implementasi:

```text
1. constants.py
       ↓
2. conversion.py
       ↓
3. validation.py
       ↓
4. aggregation.py
       ↓
5. intake.py
       ↓
6. rq.py
       ↓
7. interpretation.py
       ↓
8. known-case unit tests
       ↓
9. ARKLResult
       ↓
10. calculator.py
       ↓
11. realtime calculation
       ↓
12. historical calculation
       ↓
13. REST API
       ↓
14. OpenAPI
       ↓
15. full regression
```

---

# 55. Core Principle

```text
THE MVP MAY EVOLVE,
BUT IT MUST NEVER HIDE ITS ASSUMPTIONS.

FORMULAS ARE VERSIONED.
CONSTANTS ARE SOURCED.
UNITS ARE EXPLICIT.
RESULTS ARE REPRODUCIBLE.
AI DOES NOT DEFINE THE RISK.
```

```

Perubahan terbesarnya dibanding versi sebelumnya adalah statusnya sekarang sudah **`MVP SCIENTIFIC LOCK`**, jadi item yang sebelumnya `NOT LOCKED` untuk `R`, `tE`, `fE`, `Dt`, `tavg`, formula Intake, realtime, dan historical sudah memiliki kontrak MVP yang eksplisit. Artinya kita sekarang **boleh lanjut implementasi `intake.py`, `rq.py`, `aggregation.py`, `calculator.py`, serta ARKL API** tanpa lagi memakai placeholder. 
```
