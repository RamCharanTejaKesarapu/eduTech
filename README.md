# Student Retention & Welfare Efficacy Tracker
### State Education Department Analytics & AI Decision Support Platform
**TransOrg Datathon - Track 4: Education & EdTech**

---

## 1. Project Overview

The **Student Retention & Welfare Efficacy Tracker** is an end-to-end, enterprise-grade data intelligence platform engineered for the **State Education Department (Government of Punjab)**. It establishes an integrated analytical foundation to investigate the empirical relationships between the **Mid-Day Meal (MDM) welfare scheme**, **school infrastructure amenities**, **daily student attendance**, **foundational literacy and numeracy (FLN) academic performance**, and **student dropout/retention vulnerability**.

The platform automates the transformation of highly messy, multilingual, multi-unit synthetic education datasets into an audited dimensional data warehouse in **DuckDB**, visualizes state-level insights through a polished 8-page **Government BI Dashboard** (Streamlit + Plotly), and provides natural-language conversational analytics via an autonomous **Graph-First AI Analyst**.

---

## 2. Business Problem & Departmental Objectives

Government educational authorities require empirical decision-support tools to solve critical operational questions:
1. **Attendance Integrity & Proxy Marking**: Are schools recording fraudulent attendance on non-instructional days (e.g. 100% attendance on Sundays) or logging more attendees than enrolled students?
2. **Welfare Scheme Efficacy (Mid-Day Meal)**: Are grain procurements evenly distributed, or do specific vendors/syndicates exhibit delivery anomalies, price discrepancies, or Sunday deliveries to closed schools?
3. **Infrastructure Deficits**: Does the absence of functional electricity, drinking water, and gender-segregated functional toilets correlate with depressed attendance rates?
4. **Student Retention & Early Warning**: How can administrators proactively identify vulnerable schools at risk of chronic absenteeism and learning poverty without relying on non-existent or fabricated survey labels?

---

## 3. System Architecture

The solution adopts a decoupled modern data architecture:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        OFFICIAL RAW DATASETS                           │
│  CSV (Master, Attendance, Infra)  •  XLSX (MDM)  •  JSON (FLN Scores)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   PIPELINE & DATA ENGINEERING (ELT)                    │
│  Regex Normalizer  •  22-Boolean Standardizer  •  Unit Converter (kg)  │
│  Cost & Currency Parser  •  Multi-Scale FLN Normalizer  •  Audit Log   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   DUCKDB ANALYTICAL DATA WAREHOUSE                     │
│  Dimensions: dim_school, dim_vendor                                    │
│  Facts: fct_attendance, fct_infrastructure, fct_mdm, fct_test_scores   │
│  Marts: agg_school_retention_risk, agg_district_summary, agg_vendor    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
┌───────────────────────────────────┐ ┌───────────────────────────────────┐
│     GOVERNMENT BI DASHBOARD       │ │       GRAPH-FIRST AI AGENT        │
│   Streamlit + Plotly (8 Pages)    │ │   AST Guardrails + DuckDB SQL     │
│   Real-Time Filters & Exports     │ │   Auto Plotly Visualizations      │
└───────────────────────────────────┘ └───────────────────────────────────┘
```

---

## 4. Dataset Structure & Data Profiling Findings

Profiling across all 5 official files in `track4_education_dataset_files (1)/` revealed significant real-world data engineering challenges:

| Dataset | Format | Raw Records | Clean Records | Duplicates Removed | Key Data Quality Issues & Anomalies |
|---|---|---|---|---|---|
| **School Master** | CSV | 618 | 600 | 18 | Inconsistent casing (`patiala` vs `Patiala`), 23 missing districts, 64 missing blocks. |
| **Student Attendance** | CSV | 20,800 | 20,000 | 800 | 425 missing IDs; 5 school ID formats; **979 Sunday 100% attendance cases (proxy fraud)**; **806 attendance overflow cases (present > total)**. |
| **School Infrastructure** | CSV | 3,150 | 3,000 | 150 | **22 multilingual boolean representations** (`Hai`, `Nahi`, `haan`, `Kharab`, `Broken`, `Working`, `1`, `0`). |
| **MDM Procurement** | XLSX | 12,360 | 12,000 | 360 | **1,895 embedded unit strings** (`"14.9 kg"`); mixed units (`50kg Bags`, `Sacks`, `Grams`, `KG`); messy currency formats (`Rs. 1,600`, `₹1,317`, `336/-`); 12 messy vendor entities. |
| **FLN Test Scores** | JSON | 8,000 | 8,000 | 0 | **6 conflicting grading scales** (`Letter Grade`, `CGPA`, `Raw Marks`, `Percentage`, `pct`, `%`); mixed subjects (`Math`, `Mathematics`, `Ganit`). |

---

## 5. Data Cleaning & Transformation Pipeline

The automated cleaning pipeline (`pipeline/run_pipeline.py`) enforces strict domain transformations:
1. **School ID Standardization**: Pattern `r'(\d+)'` standardizes all formats (`SCH-`, `sch_`, `S`, `1001`) into canonical `SCHxxxx` (e.g. `SCH0050`).
2. **Missing District Imputation**: 21 out of 23 missing districts imputed using the mode of the school's administrative block; remaining 2 schools assigned `'Unassigned'` with full logging.
3. **Multilingual Boolean Normalization**: Mapped 100% of non-null strings across 22 representations into clean binary flags ($1=\text{Functional/Yes}$, $0=\text{Defective/No}$).
4. **MDM Unit Harmonization**: All procurement quantities converted to **Kilograms (KG)** ($1\text{ Bag/Sack/Bori} = 50\text{ kg}$; $\text{Grams} / 1000$; embedded strings parsed).
5. **Currency Sanitization**: Stripped commas, currency symbols, and slashes to produce numeric float columns.
6. **Multi-Scale FLN Academic Normalization**: Unified Letter Grades (midpoints: $A+=95, A=85, B=75, C=65, D=55, E=45$), CGPA ($\times 10$), Raw Marks ($\text{num}/\text{denom} \times 100$), and Percentages into an identical $0-100\%$ scale.
7. **Anomaly Classification**: Classified attendance records as `VALID`, `SUSPICIOUS_PROXY`, `INVALID_OVERFLOW`, or `SUSPICIOUS_SUNDAY`.

---

## 6. Analytical Data Model (DuckDB)

The clean data is organized into a Star Schema within `data/processed/education_data.duckdb`:
- **Dimension Tables**: `dim_school`, `dim_vendor`
- **Fact Tables**: `fct_attendance`, `fct_infrastructure`, `fct_mdm_procurement`, `fct_test_scores`, `fct_data_quality_log`
- **Analytical Marts**:
  - `agg_school_retention_risk`: School-level composite rollup.
  - `agg_district_summary`: District executive scorecard.
  - `agg_mdm_vendor_summary`: Vendor supply and spend forensics.

---

## 7. Analytical Metrics & Risk Formulations

### 7.1 Student Retention & Dropout Risk Indicator (SRDRI)
Because raw data does not contain fabricated individual dropout labels, the platform implements an interpretable, domain-grounded composite risk indicator:

$$\text{SRDRI} = 0.40 \times C_{\text{Absenteeism}} + 0.30 \times C_{\text{Academic}} + 0.15 \times C_{\text{Infrastructure}} + 0.15 \times C_{\text{MDM}}$$

- **Absenteeism ($40\%$)**: Penalizes chronic absenteeism ($<65\%$ attendance: 100 pts, $<75\%$: 75 pts).
- **Academic Deficit ($30\%$)**: Penalizes low FLN achievement ($<50\%$: 100 pts, $<60\%$: 70 pts).
- **Infrastructure Deficit ($15\%$)**: $100.0 - \text{Infra Quality Score}$.
- **MDM Supply Irregularity ($15\%$)**: Evaluates grain supplied per enrolled student ($<1.5\text{ kg}$: 80 pts).

### 7.2 Proxy Attendance Fraud Rate (%)
$$\text{Proxy Fraud Rate (\%)} = \frac{\sum \text{Sunday 100\% Attendance Records}}{\text{Total Attendance Records}} \times 100$$
- **Forensic Finding**: **Ferozepur** (10.1%) and **Ludhiana** (9.4%) exhibit the highest rates of proxy attendance fraud.

### 7.3 Infrastructure Quality Score
$$\text{Infra Quality Score} = \frac{\sum \text{Functional Amenities (Electricity, Water, Toilet, Wall, Playground)}}{5} \times 100$$

---

## 8. Government BI Dashboard Modules

The Streamlit dashboard features 8 dedicated modules adhering to government BI aesthetics:
1. **Executive Overview**: Statewide scorecard, district performance matrix, and critical early warning alerts.
2. **Student Retention & Risk**: SRDRI drilldown, risk level distributions, and individual school diagnostic radar profile.
3. **Attendance & Academics**: Longitudinal 24-month attendance trendline, day-of-week breakdown, proxy fraud rankings, and subject FLN proficiencies.
4. **Mid-Day Meal**: Food category procurement volumes, vendor spend breakdown, kg/student ratio distribution, and Sunday delivery audit.
5. **Infrastructure**: Amenity coverage comparison, district deficit indices, and empirical attendance differentials.
6. **School & District Comparison**: Side-by-side comparative benchmarking for any two districts or schools.
7. **Data Quality & Audit**: Full transparency audit matrix, anomaly breakdown charts, and real-time audit ledger with CSV export.
8. **AI Analyst**: Graph-First natural-language assistant with automated Plotly chart generation.

---

## 9. Graph-First AI Analyst Engine

- **Natural Language Understanding**: Classifies intent (*trend, ranking, comparison, correlation, distribution, summary, lookup*).
- **Graph-First Rule**: Automatically selects and renders the appropriate interactive Plotly chart (`line`, `bar`, `horizontal_bar`, `scatter`, `donut`) whenever visual inquiry is implied.
- **SQL Security Guardrails**: Enforces read-only `SELECT` statements via AST validation; blocks destructive keywords (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `ATTACH`), filesystem scanners (`read_csv`), and unapproved tables.
- **Zero Paid Dependencies**: Works **100% locally and offline** without requiring paid external API keys.

---

## 10. Installation & Setup

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- pip / virtualenv

### 1. Clone Repository & Install Dependencies
```bash
git clone https://github.com/your-org/student-retention-welfare-tracker.git
cd student-retention-welfare-tracker
pip install -r requirements.txt
```

---

## 11. Running the Pipeline

Execute the master reproducible ELT pipeline with a single command:
```bash
python pipeline/run_pipeline.py
```
*Processes all raw datasets, validates schemas, builds DuckDB analytical tables, and generates audit reports in ~1.65 seconds.*

---

## 12. Running the Dashboard

Launch the interactive Streamlit BI application:
```bash
streamlit run dashboard/app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 13. Running Automated Tests

Run the complete test suite:
```bash
pytest tests/ -v
```
*Validates 14 test cases covering ID normalization, 22-boolean parsing, MDM unit conversions, currency cleaning, score harmonizations, metric formulas, and SQL injection security.*

---

## 14. Reproducibility & Audit Trail

- **Data Integrity**: Clean analytical data is written to `data/processed/` and DuckDB without modifying raw source files.
- **Audit Ledger**: All transformed records and flagged anomalies are logged in `docs/DATA_QUALITY_REPORT.md` and `data/processed/data_quality_audit.csv`.

---

## 15. Known Limitations & Responsible Analytics

1. **Non-Causal Language**: Differences in attendance between schools with and without functional amenities are documented as **observed empirical associations**, not causal claims.
2. **Synthetic Data Characteristics**: The data represents synthetic datathon benchmarks designed to test data cleaning and analytical pipelines.
3. **No Individual Dropout Flags**: In accordance with competition rules, retention risk is modeled as a multi-factor vulnerability score (SRDRI) rather than an invented machine learning prediction.

---

## 16. Technical Documentation Index

- [Architecture Specifications](docs/ARCHITECTURE.md)
- [Data Dictionary & Schemas](docs/DATA_DICTIONARY.md)
- [Data Cleaning Methodology](docs/DATA_CLEANING.md)
- [Graph-First AI Agent Guide](docs/AI_AGENT.md)
- [Metric & Risk Formulations](docs/METHODOLOGY.md)
- [Data Quality Audit Report](docs/DATA_QUALITY_REPORT.md)
