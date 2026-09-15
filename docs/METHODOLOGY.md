# Analytical Methodology & Metric Formulations

## Student Retention & Welfare Efficacy Tracker
**TransOrg Datathon - Track 4: Education & EdTech**

---

## 1. Student Retention & Dropout Risk Indicator (SRDRI)

### 1.1 Rationale
The raw synthetic datasets supplied by the organizers contain institutional logs of attendance, infrastructure inspections, MDM grain delivery receipts, and foundational test scores. **No explicit individual student dropout survey column exists in the dataset.**

In accordance with competition rules, we do not fabricate ground-truth dropout labels or train a speculative machine learning model on invented target columns. Instead, we formulate an interpretable, domain-grounded **Student Retention & Dropout Risk Indicator (SRDRI)**.

### 1.2 Mathematical Formulation
The SRDRI score is bounded between $0.0$ (Lowest Risk) and $100.0$ (Critical Risk):

$$\text{SRDRI} = 0.40 \times C_{\text{Absenteeism}} + 0.30 \times C_{\text{Academic}} + 0.15 \times C_{\text{Infrastructure}} + 0.15 \times C_{\text{MDM}}$$

#### Component 1: Chronic Absenteeism Risk ($C_{\text{Absenteeism}}$, Weight: 40%)
Based on Right to Education (RTE) and UNESCO benchmarks:
- $\text{Attendance} < 65\% \implies C_{\text{Absenteeism}} = 100.0$ (Critical chronic absenteeism)
- $65\% \le \text{Attendance} < 75\% \implies C_{\text{Absenteeism}} = 75.0$ (High vulnerability)
- $75\% \le \text{Attendance} < 82\% \implies C_{\text{Absenteeism}} = 45.0$ (Moderate irregularity)
- $\text{Attendance} \ge 82\% \implies C_{\text{Absenteeism}} = 15.0$ (Low risk)

#### Component 2: Academic FLN Deficit ($C_{\text{Academic}}$, Weight: 30%)
Based on standardized Foundational Literacy and Numeracy (FLN) achievement:
- $\text{FLN Score} < 50\% \implies C_{\text{Academic}} = 100.0$ (Severe learning poverty)
- $50\% \le \text{FLN Score} < 60\% \implies C_{\text{Academic}} = 70.0$ (Below grade level)
- $60\% \le \text{FLN Score} < 70\% \implies C_{\text{Academic}} = 35.0$ (Average competency)
- $\text{FLN Score} \ge 70\% \implies C_{\text{Academic}} = 10.0$ (Proficient / distinction)

#### Component 3: Infrastructure Deficit ($C_{\text{Infrastructure}}$, Weight: 15%)
Directly derived from the school's **Infrastructure Deficit Index**:
$$C_{\text{Infrastructure}} = \text{Infra Deficit Index} = 100.0 - \text{Infra Quality Score}$$

#### Component 4: MDM Supply Irregularity ($C_{\text{MDM}}$, Weight: 15%)
Evaluates nutritional safety net disruption based on grain delivered per enrolled student:
- $\text{Grain / Student} < 1.5\text{ kg} \implies C_{\text{MDM}} = 80.0$ (Severe meal deficit)
- $1.5\text{ kg} \le \text{Grain / Student} < 2.5\text{ kg} \implies C_{\text{MDM}} = 40.0$ (Moderate supply)
- $\text{Grain / Student} \ge 2.5\text{ kg} \implies C_{\text{MDM}} = 10.0$ (Adequate grain supply)

### 1.3 Risk Tiers & Administrative Triggers
| SRDRI Range | Classification | Triggered Administrative Action |
|---|---|---|
| $\ge 65.0$ | **Critical Risk** | Immediate field inspection, remedial teaching camps, and welfare audit. |
| $48.0 - 64.9$ | **High Risk** | Targeted parent counseling, attendance tracking, and sanitation repair. |
| $32.0 - 47.9$ | **Medium Risk** | Routine monitoring and periodic FLN progress checks. |
| $< 32.0$ | **Low Risk** | Stable retention environment. |

### 1.4 Retention Efficacy Proxy
$$\text{Retention Proxy (\%)} = \max\Big(50.0, \min\big(98.0, 100.0 - (\text{SRDRI} \times 0.45)\big)\Big)$$

---

## 2. Attendance Forensics & Proxy Fraud Formulations

### 2.1 Proxy Attendance Fraud Rate (%)
Identifies instances where school staff logged 100% student attendance on a Sunday (when government schools are officially closed):

$$\text{Proxy Fraud Rate (\%)} = \frac{\sum \text{Sunday 100\% Attendance Records}}{\text{Total Attendance Records}} \times 100$$

### 2.2 Attendance Overflow
Instances where $\text{Present Students} > \text{Total Enrolled Students}$. Flagged as invalid records and capped at 1.0 (100%) during clean analytical processing.

---

## 3. Infrastructure Scoring

### 3.1 Infrastructure Quality Score (0 - 100)
For each school across 5 core statutory amenities (Electricity, Drinking Water, Functional Toilets, Boundary Wall, Playground):

$$\text{Infra Quality Score} = \frac{\sum_{i=1}^{5} \text{Amenity}_i}{5} \times 100$$

### 3.2 Infrastructure Deficit Index (0 - 100)
$$\text{Deficit Index} = 100.0 - \text{Infra Quality Score}$$

---

## 4. Principles of Causal & Correlation Integrity

1. **Non-Causal Language**: In accordance with statistical rigor, observed differences between schools with and without functional amenities are documented as **"observed associations"** or **"higher/lower empirical averages"**. The term *"causes"* is never utilized without randomized controlled trial (RCT) or instrumental variable identification.
2. **Data Transparency**: Every chart, KPI, and agent answer displays underlying sample sizes, timeframes, and filter parameters.
