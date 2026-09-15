# Data Cleaning & Normalization Methodology

## Student Retention & Welfare Efficacy Tracker
**TransOrg Datathon - Track 4: Education & EdTech**

---

## 1. Overview of Data Cleaning Pipeline

The data cleaning pipeline (`pipeline/run_pipeline.py`) transforms raw, messy, and heterogeneous education records into standardized, validated dimensional models. The pipeline is **100% automated, deterministic, and reproducible** with zero manual dataset manipulation.

---

## 2. Specific Cleaning Strategies

### 2.1 Entity ID Normalization (`school_id`)
- **Problem**: School IDs appeared in at least 5 inconsistent formats across files:
  - `SCH0050` (Standard Master format)
  - `SCH-0596` (Hyphenated format)
  - `sch_0054` (Lowercase with underscore)
  - `S0433` (Abbreviated prefix)
  - `208` / `1001` (Unpadded digits)
- **Transformation**: Extracted numerical digits via regular expression `r'(\d+)'` and padded to 4 digits prefixed by `SCH`:
  ```python
  def normalize_school_id(val):
      if pd.isna(val): return None
      digits = re.findall(r"\d+", str(val).strip())
      return f"SCH{int(digits[0]):04d}" if digits else str(val).upper()
  ```
- **Verification**: Exactly 600 unique schools (`SCH0001` to `SCH0600`). 0 orphan foreign key records across all fact tables.

---

### 2.2 Multilingual Boolean Normalization
- **Problem**: Infrastructure amenities and teacher attendance columns contained 22 diverse multilingual string representations:
  `{'Hai', 'haan', 'Haan', 'H', 'Functional', 'Working', 'Available', 'Yes', 'Y', '1', 'True', 'Nahi', 'nahi hai', 'na', 'Broken', 'Kharab', 'Under Repair', 'Not Available', 'No', 'N', '0', 'False'}`
- **Transformation**:
  - **Positive / Functional (1)**: `{'true', 'yes', 'y', '1', 'hai', 'haan', 'h', 'functional', 'working', 'available'}`
  - **Negative / Defective (0)**: `{'false', 'no', 'n', '0', 'nahi', 'nahi hai', 'na', 'broken', 'kharab', 'under repair', 'not available'}`
  - **Missing / Unrecorded**: Preserved as `NULL` / `None` in database and tracked in the quality ledger.
- **Verification**: 100% of non-null values mapped into 1 or 0 with 0 unmapped strings.

---

### 2.3 MDM Unit Standardization & Embedded Parsing
- **Problem**: Grain procurement quantities were represented across multiple conflicting units:
  - Raw numbers with separate unit column: `50kg Bags`, `Bags`, `Bori`, `Sacks`, `Grams`, `grams`, `g`, `KG`, `kg`, `Kgs`, `KGS`.
  - Embedded unit strings inside the quantity column: `"14.9 kg"`, `"30.6 kg"` with `unit = NaN` (1,895 rows).
  - Pure missing quantities (1,909 rows).
- **Transformation**:
  - Embedded strings: Extracted float via regex `r'([\d\.]+)'` $\implies$ quantity in KG.
  - Sacks / Bags / Bori: Multiplied by $50.0 \text{ kg}$ (1 bag = 50 kg). Profiling verified raw bag quantities were $0.2 - 1.2 \text{ bags} \implies 10 - 60 \text{ kg}$.
  - Grams / g: Divided by $1,000.0 \text{ kg}$. Profiling verified raw grams were $10,000 - 60,000 \text{ g} \implies 10 - 60 \text{ kg}$.
  - Direct KG / kg: Preserved as float.
- **Verification**: Yields a single standard unit: `quantity_kg` across all rows.

---

### 2.4 Currency & Cost Normalization
- **Problem**: MDM `total_cost` contained mixed currency symbols, commas, and trailing slashes:
  `'Rs. 1,600'`, `'₹1,317'`, `'336/-'`, `'2,466/-'`, `'4992'`.
- **Transformation**: Stripped all non-numeric characters via regex `re.sub(r'[Rs\.\₹\,\/\-\s]', '', s)` and converted to float `total_cost_inr`.
- **Verification**: 100% of non-null costs parsed cleanly into floats.

---

### 2.5 Multi-Scale FLN Test Score Normalization
- **Problem**: Standardized test assessments used 6 conflicting scales:
  - `Letter Grade`: `'A+'`, `'A'`, `'B'`, `'C'`, `'D'`, `'E'`
  - `CGPA`: Floats between 4.0 and 9.5 (out of 10)
  - `Raw Marks`: Fractional strings like `'20.2/25'`, `'38.0/50'`, `'89.5/100'`
  - `Percentage` / `pct` / `%`: Strings like `'63.4%'`, `'88.1%'`
- **Transformation**: Unified all scores to a standard 0 to 100% scale:
  - Letter Grades mapped to midpoints: `A+` $\to 95\%$, `A` $\to 85\%$, `B` $\to 75\%$, `C` $\to 65\%$, `D` $\to 55\%$, `E` $\to 45\%$.
  - CGPA converted via $\text{CGPA} \times 10.0$.
  - Raw Marks parsed as $\frac{\text{Numerator}}{\text{Denominator}} \times 100.0$.
  - Percentages stripped of `%` and cast to float.
- **Verification**: Statistical deciles across all scales align identically: 25th percentile is $53\%$, 50th percentile is $67\%$, 75th percentile is $81\%$.

---

### 2.6 Attendance Anomaly & Proxy Fraud Classification
- **Domain Anomalies Identified**:
  1. **Proxy Attendance Fraud**: 979 clean records where 100% student attendance was recorded on a Sunday (school closed). Flagged as `SUSPICIOUS_PROXY`.
  2. **Attendance Overflow**: 806 clean records where present students strictly exceeded total enrolled students. Flagged as `INVALID_OVERFLOW`.
  3. **Sunday School Sessions**: All Sunday attendance records flagged as `is_sunday = 1`.
- **Handling**: Valid weekday records are classified as `VALID`. For clean analytical attendance reporting, rates are capped at 1.0 (100%) and filtered to `VALID` records.

---

### 2.7 Missing Value Resolution & Imputation
- **School Master Districts (23 missing)**: 21 missing districts were imputed by determining the modal district of the school's administrative `block`. The 2 schools with missing blocks (`SCH0085`, `SCH0169`) were assigned `'Unassigned'` with full logging in the data quality audit ledger.
- **Attendance Record IDs (425 missing)**: Deterministic surrogates (`ATT_GEN_000001` to `ATT_GEN_000425`) generated to ensure primary key integrity.
