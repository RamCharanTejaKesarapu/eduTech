# Data Dictionary: Student Retention & Welfare Efficacy Tracker

This document provides complete technical specifications for all tables, fields, types, constraints, and formulas within the analytical DuckDB database (`education_data.duckdb`).

---

## 1. Dimension Tables

### 1.1 `dim_school`
Master registry of all 600 verified government schools.

| Column Name | Data Type | Constraint | Description | Sample Values |
|---|---|---|---|---|
| `school_id` | VARCHAR | PRIMARY KEY | Canonical school identifier (`SCHxxxx`). | `'SCH0001'`, `'SCH0600'` |
| `school_name` | VARCHAR | NOT NULL | Official registered name of the school. | `'Govt. Senior Secondary School Tank'` |
| `district` | VARCHAR | NOT NULL | Administrative district in Punjab (Title Case). | `'Patiala'`, `'Ferozepur'`, `'Moga'` |
| `block` | VARCHAR | NOT NULL | Administrative educational sub-district block. | `'Moga-I'`, `'Makhu'`, `'Samana'` |
| `total_enrolled_students`| INTEGER | > 0 | Total active enrolled students at start of session. | `249`, `424`, `196` |
| `school_type` | VARCHAR | NOT NULL | Educational level category. | `'Primary'`, `'Upper Primary'`, `'Secondary'`, `'Higher Secondary'` |
| `medium` | VARCHAR | NOT NULL | Primary medium of instruction. | `'Punjabi'`, `'Hindi'`, `'English'` |

---

### 1.2 `dim_vendor`
Registry of Mid-Day Meal grain suppliers and parent commercial groups.

| Column Name | Data Type | Constraint | Description | Sample Values |
|---|---|---|---|---|
| `vendor_id` | VARCHAR | PRIMARY KEY | Canonical vendor identifier (`VNDxxx`). | `'VND001'`, `'VND010'` |
| `vendor_name` | VARCHAR | NOT NULL | Standardized corporate/trader business name. | `'Sharma Traders'`, `'Goyal Rice Mill'` |
| `vendor_group` | VARCHAR | NOT NULL | Parent corporate syndicate / supplier house. | `'Sharma Group'`, `'Goyal Group'`, `'Kumar Group'`, `'Singh Group'` |

---

## 2. Fact Tables

### 2.1 `fct_attendance`
Daily attendance logs per grade and school.

| Column Name | Data Type | Constraint | Description | Sample Values |
|---|---|---|---|---|
| `record_id` | VARCHAR | PRIMARY KEY | Unique attendance entry ID. | `'ATT0014650'`, `'ATT_GEN_000001'` |
| `attendance_date` | DATE | NOT NULL | Standardized date of attendance record (`YYYY-MM-DD`). | `'2025-07-26'`, `'2026-03-11'` |
| `day_of_week` | VARCHAR | NOT NULL | Day name extracted from date. | `'Monday'`, `'Sunday'` |
| `school_id` | VARCHAR | FK `dim_school` | Canonical school identifier. | `'SCH0596'` |
| `grade` | VARCHAR | NOT NULL | Standardized grade level (`1` to `10`). | `'1'`, `'5'`, `'8'` |
| `total_students` | INTEGER | $\ge 0$ | Total enrolled students registered for that grade. | `85`, `197`, `58` |
| `present_students` | INTEGER | $\ge 0$ | Number of students marked present. | `60`, `119`, `52` |
| `attendance_rate_raw`| DOUBLE | None | Raw ratio (`present_students / total_students`). | `0.8125`, `1.2050` |
| `attendance_rate_capped`| DOUBLE| $\le 1.0$ | Rate capped at 1.0 (100%) for clean analysis. | `0.8125`, `1.0000` |
| `teacher_present` | INTEGER | 0, 1, or NULL | Normalized teacher attendance indicator (1=Yes, 0=No). | `1`, `0` |
| `marked_by` | VARCHAR | NOT NULL | Designation of staff logging attendance. | `'Class Teacher'`, `'Headmaster'`, `'Admin'` |
| `is_sunday` | INTEGER | 0 or 1 | Flag indicating record logged on a Sunday. | `1`, `0` |
| `is_proxy_attendance`| INTEGER | 0 or 1 | Flag: 100% attendance logged on Sunday (Proxy Fraud). | `1`, `0` |
| `is_attendance_overflow`| INTEGER | 0 or 1 | Flag: Present students > Total enrolled students. | `1`, `0` |
| `quality_status` | VARCHAR | NOT NULL | Validation classification (`VALID`, `SUSPICIOUS_PROXY`, `INVALID_OVERFLOW`, `SUSPICIOUS_SUNDAY`). | `'VALID'`, `'SUSPICIOUS_PROXY'` |

---

### 2.2 `fct_infrastructure`
Periodic inspection logs of school physical amenities.

| Column Name | Data Type | Constraint | Description | Sample Values |
|---|---|---|---|---|
| `inspection_id` | VARCHAR | PRIMARY KEY | Unique inspection visit ID. | `'INSP02966'` |
| `inspection_date` | DATE | NOT NULL | Standardized inspection date (`YYYY-MM-DD`). | `'2025-04-02'` |
| `school_id` | VARCHAR | FK `dim_school` | Canonical school identifier. | `'SCH0476'` |
| `has_electricity` | INTEGER | 0, 1, or NULL | Functional electricity grid access (1=Yes, 0=No). | `1`, `0` |
| `has_drinking_water`| INTEGER | 0, 1, or NULL | Potable drinking water access (1=Yes, 0=No). | `1`, `0` |
| `has_functional_toilet`| INTEGER | 0, 1, or NULL | Functional sanitation facility (1=Yes, 0=No). | `1`, `0` |
| `has_boundary_wall` | INTEGER | 0, 1, or NULL | Perimeter security wall (1=Yes, 0=No). | `1`, `0` |
| `has_playground` | INTEGER | 0, 1, or NULL | Recreational playground (1=Yes, 0=No). | `1`, `0` |
| `infra_score` | DOUBLE | 0.0 to 100.0 | Quality score (% of functional amenities). | `80.0`, `100.0` |
| `infra_deficit_index`| DOUBLE | 0.0 to 100.0 | Deficit index (`100.0 - infra_score`). | `20.0`, `0.0` |
| `inspector_name` | VARCHAR | NOT NULL | Name of inspecting official. | `'Fariq Tripathi'` |
| `remarks` | VARCHAR | NOT NULL | Qualitative observation notes. | `'Good condition'`, `'Toilets locked'` |

---

### 2.3 `fct_mdm_procurement`
Grain procurement logs for the Mid-Day Meal scheme.

| Column Name | Data Type | Constraint | Description | Sample Values |
|---|---|---|---|---|
| `procurement_id` | VARCHAR | PRIMARY KEY | Unique MDM delivery receipt ID. | `'MDM008522'` |
| `procurement_date`| DATE | NOT NULL | Standardized date of delivery (`YYYY-MM-DD`). | `'2025-08-10'` |
| `day_of_week` | VARCHAR | NOT NULL | Day name extracted from date. | `'Tuesday'`, `'Sunday'` |
| `is_sunday_procurement`| INTEGER | 0 or 1 | Flag: Delivery recorded on Sunday (school closed). | `1`, `0` |
| `school_id` | VARCHAR | FK `dim_school` | Canonical school identifier. | `'SCH0249'` |
| `vendor_name` | VARCHAR | NOT NULL | Standardized supplier company name. | `'Sharma Traders'` |
| `vendor_group` | VARCHAR | NOT NULL | Parent supplier syndicate. | `'Sharma Group'` |
| `food_category` | VARCHAR | NOT NULL | Standardized staple category (`Rice`, `Wheat`, `Mustard Oil`, `Pulses / Dal`). | `'Rice'`, `'Wheat'` |
| `raw_grain_type` | VARCHAR | NOT NULL | Original uncleaned grain name. | `'chawal'`, `'gehun'`, `'Sarson Tel'` |
| `quantity_kg` | DOUBLE | > 0 | Total quantity standardized into Kilograms (KG). | `40.7`, `54.2`, `14.9` |
| `total_cost_inr` | DOUBLE | > 0 | Total invoice amount in Indian Rupees (₹). | `336.0`, `1600.0` |
| `cost_per_kg` | DOUBLE | > 0 | Effective unit cost per kilogram (`total_cost_inr / quantity_kg`). | `48.5`, `52.0` |
| `payment_status` | VARCHAR | NOT NULL | Normalized payment status (`PAID`, `PENDING`, `DUE`). | `'PAID'`, `'PENDING'` |

---

### 2.4 `fct_test_scores`
Foundational Literacy and Numeracy (FLN) standardized assessments.

| Column Name | Data Type | Constraint | Description | Sample Values |
|---|---|---|---|---|
| `assessment_id` | VARCHAR | PRIMARY KEY | Unique test assessment ID. | `'TST005495'` |
| `assessment_date` | DATE | NOT NULL | Standardized test date (`YYYY-MM-DD`). | `'2025-05-05'` |
| `school_id` | VARCHAR | FK `dim_school` | Canonical school identifier. | `'SCH0083'` |
| `grade` | VARCHAR | NOT NULL | Assessed grade level (`3` to `8`). | `'5'`, `'8'` |
| `subject` | VARCHAR | NOT NULL | Unified subject (`Mathematics`, `Science`, `English`, `Hindi`, `Punjabi`, `EVS`). | `'Mathematics'` |
| `original_scale` | VARCHAR | NOT NULL | Raw grading scale used (`Letter Grade`, `CGPA`, `Raw Marks`, `Percentage`). | `'Letter Grade'` |
| `original_score` | VARCHAR | NOT NULL | Uncleaned score value. | `'C'`, `'7.7'`, `'20.2/25'` |
| `max_marks` | VARCHAR | None | Raw denominator / maximum marks. | `'NA'`, `'100'`, `'25'`, `'50'` |
| `score_percentage`| DOUBLE | 0.0 to 100.0 | Normalized test performance percentage. | `65.0`, `77.0`, `80.8` |
| `proficiency_tier`| VARCHAR | NOT NULL | Standardized achievement tier (`Distinction`, `Proficient`, `Basic`, `Below Basic`). | `'Proficient (Level 3)'` |
| `total_students_assessed`| INTEGER | > 0 | Number of students evaluated in assessment. | `125`, `76` |

---

## 3. Analytical Marts

### 3.1 `agg_school_retention_risk`
School-level executive analytical mart joining attendance, FLN academics, infrastructure, and MDM metrics with the composite **Student Retention & Dropout Risk Indicator (SRDRI)**.

| Column Name | Type | Description | Formula / Source |
|---|---|---|---|
| `school_id` | VARCHAR | Canonical School ID. | `dim_school.school_id` |
| `school_name` | VARCHAR | School Name. | `dim_school.school_name` |
| `district` | VARCHAR | District. | `dim_school.district` |
| `block` | VARCHAR | Block. | `dim_school.block` |
| `total_enrolled_students`| INTEGER | Active enrollment. | `dim_school.total_enrolled_students` |
| `avg_attendance_rate_pct`| DOUBLE | Clean attendance rate %. | Verified weekday logs only. |
| `proxy_fraud_count` | INTEGER | Sunday 100% attendance cases. | Sum of proxy fraud logs. |
| `proxy_fraud_rate_pct`| DOUBLE | Proxy fraud rate %. | `(proxy_fraud_count / total_att) * 100` |
| `avg_fln_score_pct` | DOUBLE | Mean FLN test percentage. | Mean of normalized scores. |
| `avg_infra_score` | DOUBLE | Mean infrastructure score. | Mean of amenity scores. |
| `infra_deficit_index`| DOUBLE | Infrastructure deficit %. | `100.0 - avg_infra_score` |
| `total_grain_kg` | DOUBLE | Total grain delivered (kg). | Sum of MDM procurement kg. |
| `kg_grain_per_student`| DOUBLE | MDM grain per student. | `total_grain_kg / total_enrolled_students` |
| `risk_component_absenteeism`| DOUBLE | Absenteeism risk component (0-100). | Based on attendance brackets. |
| `risk_component_academic`| DOUBLE | Academic risk component (0-100). | Based on FLN score brackets. |
| `risk_component_infrastructure`| DOUBLE | Infrastructure risk component (0-100). | `infra_deficit_index` |
| `risk_component_mdm` | DOUBLE | MDM supply irregularity risk (0-100). | Based on kg/student ratio. |
| `srdri_score` | DOUBLE | Composite SRDRI Risk Score (0-100). | $0.40 \times \text{Abs} + 0.30 \times \text{Acad} + 0.15 \times \text{Infra} + 0.15 \times \text{MDM}$ |
| `srdri_risk_level` | VARCHAR | Risk Tier. | `'Critical Risk'`, `'High Risk'`, `'Medium Risk'`, `'Low Risk'` |
| `retention_proxy_pct`| DOUBLE | Estimated Retention Efficacy %. | $\max(50, \min(98, 100 - (\text{SRDRI} \times 0.45)))$ |
