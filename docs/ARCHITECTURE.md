# System Architecture & Technical Specifications

## Student Retention & Welfare Efficacy Tracker
**State Education Department Analytics & AI Decision Support Platform**

---

## 1. Architectural Overview

The platform is designed as an end-to-end, modular, and reproducible data intelligence system structured into three primary tiers:

```mermaid
flowchart TD
    subgraph Ingestion["1. Raw Data Ingestion"]
        RAW_CSV["CSV Files (Master, Attendance, Infra)"]
        RAW_XLSX["Excel (MDM Grain Procurement)"]
        RAW_JSON["JSON (Foundational Test Scores)"]
    end

    subgraph Pipeline["2. Data Engineering & ELT Pipeline"]
        CLEAN_MASTER["Master Cleaner & District Imputer"]
        CLEAN_ATT["Attendance Cleaner & Fraud Detector"]
        CLEAN_INFRA["Infrastructure 22-Boolean Normalizer"]
        CLEAN_MDM["MDM Unit Standardizer & Currency Parser"]
        CLEAN_FLN["FLN Multi-Scale Score Standardizer"]
        AUDIT_LOG["Data Quality Audit Engine"]
    end

    subgraph Storage["3. Analytical Storage (DuckDB)"]
        DIM_SCHOOL[("dim_school")]
        DIM_VENDOR[("dim_vendor")]
        FCT_ATT[("fct_attendance")]
        FCT_INFRA[("fct_infrastructure")]
        FCT_MDM[("fct_mdm_procurement")]
        FCT_FLN[("fct_test_scores")]
        MART_RISK[("agg_school_retention_risk")]
        MART_DIST[("agg_district_summary")]
        MART_VEND[("agg_mdm_vendor_summary")]
    end

    subgraph Analytics["4. Government BI Presentation Layer"]
        DASHBOARD["Streamlit BI Dashboard (8 Modules)"]
        PLOTLY["Plotly Interactive Visualizations"]
    end

    subgraph Agent["5. Graph-First AI Analyst"]
        INTENT["Intent Detection & Entity Extractor"]
        SQL_GEN["Safe SQL Generator"]
        GUARDRAILS["AST Security Guardrails"]
        CHART_ENGINE["Plotly Chart Generator"]
        NL_SYNTH["Data-Grounded Answer Synthesizer"]
    end

    RAW_CSV --> CLEAN_MASTER
    RAW_CSV --> CLEAN_ATT
    RAW_CSV --> CLEAN_INFRA
    RAW_XLSX --> CLEAN_MDM
    RAW_JSON --> CLEAN_FLN

    CLEAN_MASTER --> AUDIT_LOG
    CLEAN_ATT --> AUDIT_LOG
    CLEAN_INFRA --> AUDIT_LOG
    CLEAN_MDM --> AUDIT_LOG
    CLEAN_FLN --> AUDIT_LOG

    CLEAN_MASTER --> DIM_SCHOOL
    CLEAN_MDM --> DIM_VENDOR
    CLEAN_ATT --> FCT_ATT
    CLEAN_INFRA --> FCT_INFRA
    CLEAN_MDM --> FCT_MDM
    CLEAN_FLN --> FCT_FLN

    DIM_SCHOOL & FCT_ATT & FCT_INFRA & FCT_MDM & FCT_FLN --> MART_RISK
    MART_RISK --> MART_DIST
    FCT_MDM --> MART_VEND

    Storage --> DASHBOARD
    DASHBOARD --> PLOTLY

    INTENT --> SQL_GEN
    SQL_GEN --> GUARDRAILS
    GUARDRAILS --> Storage
    Storage --> CHART_ENGINE & NL_SYNTH
    CHART_ENGINE & NL_SYNTH --> DASHBOARD
```

---

## 2. Component Specifications

### 2.1 Data Engineering & Processing Layer (`pipeline/`)
- **Technology**: Python 3.12+, Pandas, NumPy, Regex.
- **Execution Script**: `python pipeline/run_pipeline.py`.
- **Runtime Performance**: Processes 44,928 raw records, performs deduplication, multidimensional transformations, and writes to DuckDB in **1.65 seconds**.
- **Audit Engine**: Tracks before/after records, null counts, imputed values, unit conversions, and domain anomaly flags in `data/processed/data_quality_audit.csv`.

### 2.2 Analytical Database Layer (`data/processed/education_data.duckdb`)
- **Technology**: DuckDB columnar database.
- **Benefits**:
  - Zero-server embeddable relational database.
  - Sub-millisecond analytical aggregations over tens of thousands of rows.
  - High concurrency support for dashboard sessions.
  - Native support for window functions, string matching, and CTEs.
- **Schema Design**: Star schema with materialized analytical marts (`agg_school_retention_risk`, `agg_district_summary`, `agg_mdm_vendor_summary`).

### 2.3 Web Dashboard Layer (`dashboard/`)
- **Technology**: Python, Streamlit, Plotly.
- **Styling**: Custom Government BI CSS (`dashboard/styles.css`) tailored with clean typography, navy/slate blue palette (`#0F172A`, `#1E3A8A`), responsive metric cards, and accessible colorways.
- **8 Dedicated Modules**:
  1. Executive Overview
  2. Student Retention & Early Warning (SRDRI)
  3. Attendance Integrity & Academic FLN Performance
  4. Mid-Day Meal (MDM) Efficacy & Supply Chain
  5. School Infrastructure & Basic Amenities
  6. School & District Comparison
  7. Data Quality & Pipeline Forensics
  8. AI Graph-First Analyst

### 2.4 Graph-First AI Analyst Layer (`agent/`)
- **Safe Pipeline**:
  `User Question` $\to$ `Intent Detection` $\to$ `Schema Grounding` $\to$ `SQL Generation` $\to$ `AST Security Guardrail` $\to$ `DuckDB Execution` $\to$ `Chart Selection` $\to$ `Data-Grounded Synthesis`
- **Security Features**:
  - Strict AST validation: Permits only analytical `SELECT` and `WITH` (CTE) queries.
  - Hard blocks: `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`, `ATTACH`, `COPY`, `PRAGMA`, filesystem access (`read_csv`, `read_parquet`), system commands.
  - Whitelist: Only approved tables and views can be referenced.
- **No Paid APIs Required**: Operates 100% locally and deterministically.
