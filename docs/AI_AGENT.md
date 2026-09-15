# Graph-First AI Analyst: Architecture & Technical Guide

## Student Retention & Welfare Efficacy Tracker
**TransOrg Datathon - Track 4: Education & EdTech**

---

## 1. Agent Architecture

The AI Analyst is built on a **Graph-First, Security-Enforced Analytical Execution Pipeline**:

```
[User Question]
       │
       ▼
[Intent Detection & Entity Extractor]
       │
       ▼
[Schema Retrieval & Analytical Query Planner]
       │
       ▼
[Deterministic DuckDB SQL Generator]
       │
       ▼
[AST Security Guardrail Validator]  ──(Rejected)──► [Security Error Message]
       │ (Approved)
       ▼
[DuckDB Analytical Engine Execution]
       │
       ▼
[Result Validator & Dimension Evaluator]
       │
       ├─────────────────────────────────┬─────────────────────────────────┐
       ▼                                 ▼                                 ▼
[Graph-First Chart Selector]     [NL Context Synthesizer]          [Raw Record Audit]
       │                                 │                                 │
       ▼                                 ▼                                 ▼
[Interactive Plotly Figure]      [Data-Grounded Answer]            [Expandable Dataframe]
```

---

## 2. Graph-First Visualization Rule

In accordance with the hackathon rules, if the user inquiry implies visual inquiry (keywords: *show, plot, chart, trend, compare, comparison, distribution, relationship, correlation, ranking, top, bottom, breakdown*), the agent automatically produces an interactive **Plotly chart** alongside the textual answer.

### Chart Selection Logic

| Intent / Question Type | Visual Selection | Visual Construction |
|---|---|---|
| **Longitudinal Trend** | `line` | Date / Month vs Average Metric with spline smoothing. |
| **Rankings / Top N / Bottom N** | `horizontal_bar` | Entity vs Value sorted ascending for clean horizontal reading. |
| **Categorical Comparison** | `bar` | Grouped or individual bar chart with direct data labels. |
| **Correlation / Association** | `scatter` | Metric X vs Metric Y with OLS linear trendline. |
| **Distribution / Share** | `donut` | Proportions / percentages with interior hole. |
| **Single Metric Summary** | `metric_card` | Large numeric display without redundant charts. |

---

## 3. SQL Security Guardrails

The agent enforces strict AST and regular expression security filters before executing any generated SQL against DuckDB:

1. **Analytical Read-Only Enforcement**: Queries must strictly begin with `SELECT` or `WITH` (for CTEs).
2. **Hard Block on Modifying Keywords**: Any presence of `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `CREATE`, `ATTACH`, `DETACH`, `COPY`, `PRAGMA`, `CALL`, `INSTALL`, `LOAD`, `TRUNCATE`, or `REPLACE` triggers immediate rejection.
3. **Filesystem & System Call Prohibition**: External file scanners (`read_csv`, `read_parquet`, `write_csv`, `sqlite_scan`) and operating system calls are strictly blocked.
4. **Table Whitelist Enforcement**: Only approved analytical tables are permitted:
   - `agg_school_retention_risk`
   - `agg_district_summary`
   - `agg_mdm_vendor_summary`
   - `dim_school`
   - `dim_vendor`
   - `fct_attendance`
   - `fct_infrastructure`
   - `fct_mdm_procurement`
   - `fct_test_scores`
   - `fct_data_quality_log`
   - Valid local Common Table Expression (CTE) aliases.
5. **Single Statement Enforcement**: Queries containing multiple statements separated by semicolons are rejected.

---

## 4. Free & Local Execution (No Paid APIs Required)

- The AI Analyst operates **100% offline, locally, and deterministically** out of the box using structured pattern matching, domain entity extraction, and schema-grounded SQL query synthesis.
- It requires **zero external API keys** (no OpenAI, Anthropic, or paid cloud dependencies).
- Can optionally plug into local open-source models (via Ollama) if available, but maintains full standalone functionality without external servers.

---

## 5. Supported Example Queries & Responses

### Query 1: Total Student Enrollment
- **Input**: *"What is the total number of students?"*
- **Generated SQL**: `SELECT SUM(total_enrolled_students) AS total_students FROM dim_school;`
- **Output**: Text Metric: `Total Students: 148,083`.

### Query 2: District with Highest Proxy Attendance Fraud
- **Input**: *"Which district has the highest proxy attendance anomalies?"*
- **Generated SQL**:
  ```sql
  SELECT district, SUM(proxy_fraud_count) AS total_proxy_records, ROUND(AVG(proxy_fraud_rate_pct), 2) AS avg_proxy_fraud_rate_pct
  FROM agg_school_retention_risk
  GROUP BY district
  ORDER BY avg_proxy_fraud_rate_pct DESC;
  ```
- **Output**: Horizontal bar chart + explanation identifying **Ferozepur** (10.1%) and **Ludhiana** (9.4%).

### Query 3: Monthly Attendance Trend
- **Input**: *"Show me the monthly trend of average student attendance."*
- **Generated SQL**:
  ```sql
  SELECT strftime(attendance_date, '%Y-%m') AS month, ROUND(AVG(attendance_rate_capped) * 100.0, 2) AS avg_attendance_pct
  FROM fct_attendance
  WHERE quality_status = 'VALID'
  GROUP BY month
  ORDER BY month;
  ```
- **Output**: Interactive Plotly line chart spanning 24 months.

### Query 4: Infrastructure Impact Comparison
- **Input**: *"Compare average test scores between schools with and without functional electricity."*
- **Generated SQL**:
  ```sql
  SELECT CASE WHEN i.has_electricity = 1 THEN 'With Functional Electricity' ELSE 'Without Electricity' END AS electricity_status,
         ROUND(AVG(t.score_percentage), 2) AS avg_fln_score_pct
  FROM fct_test_scores t
  JOIN fct_infrastructure i ON t.school_id = i.school_id
  GROUP BY electricity_status;
  ```
- **Output**: Bar chart comparing the two cohorts with non-causal analytical interpretation.
