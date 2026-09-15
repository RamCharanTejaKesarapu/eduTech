# Data Quality & Pipeline Audit Report
**TransOrg Datathon - Track 4: Education & EdTech**
Project: **Student Retention & Welfare Efficacy Tracker**
Generated At: `2026-09-15 22:18:13`

## 1. Pipeline Execution Summary
| Dataset | Raw Records | Clean Records | Duplicate Records Removed | Key Anomaly Metrics |
|---|---|---|---|---|
| `school_master` | 618 | 600 | 18 | unassigned_district: 2 |
| `student_attendance` | 20,800 | 20,000 | 800 | proxy_fraud_count: 979, overflow_count: 806, sunday_records_count: 2878 |
| `school_infrastructure` | 3,150 | 3,000 | 150 | average_infra_score: 69.83557333333333, schools_zero_score: 4 |
| `mid_day_meal` | 12,360 | 12,000 | 360 | sunday_procurement_count: 1688, total_spend_inr: 27915722.0, total_volume_kg: 354504.0 |
| `test_scores` | 8,000 | 8,000 | 0 | average_fln_percentage: 66.7394375, below_basic_count: 581 |

## 2. Detailed Data Quality Issues & Classifications
- **VALID**: Records adhering to domain rules and physical constraints.
- **CORRECTED**: Records with normalized whitespace, canonical casing, unified IDs, or imputed missing districts.
- **SUSPICIOUS**: Records exhibiting proxy attendance indicators (100% attendance on Sunday) or Sunday MDM deliveries.
- **INVALID**: Records violating physical reality (present students > total students).

### Sample Quality Audit Log Entries

| dataset | record_id | column_name | issue_type | raw_value | corrected_value | quality_status | timestamp |
| --- | --- | --- | --- | --- | --- | --- | --- |
| school_master | SCH0205 | district | MISSING_VALUE_IMPUTED | nan | Ferozepur | CORRECTED | 2026-09-15T22:18:11.912088 |
| school_master | SCH0453 | district | MISSING_VALUE_IMPUTED | nan | Ludhiana | CORRECTED | 2026-09-15T22:18:11.912381 |
| school_master | SCH0182 | district | MISSING_VALUE_IMPUTED | nan | Moga | CORRECTED | 2026-09-15T22:18:11.912638 |
| school_master | SCH0279 | district | MISSING_VALUE_IMPUTED | nan | Moga | CORRECTED | 2026-09-15T22:18:11.912877 |
| school_master | SCH0330 | district | MISSING_VALUE_IMPUTED | nan | Moga | CORRECTED | 2026-09-15T22:18:11.913101 |
| school_master | SCH0085 | district | UNRESOLVED_MISSING_DISTRICT | nan | Unassigned | SUSPICIOUS | 2026-09-15T22:18:11.913320 |
| school_master | SCH0491 | district | MISSING_VALUE_IMPUTED | nan | Sangrur | CORRECTED | 2026-09-15T22:18:11.913537 |
| school_master | SCH0519 | district | MISSING_VALUE_IMPUTED | nan | Bathinda | CORRECTED | 2026-09-15T22:18:11.913747 |
| school_master | SCH0582 | district | MISSING_VALUE_IMPUTED | nan | Patiala | CORRECTED | 2026-09-15T22:18:11.913956 |
| school_master | SCH0026 | district | MISSING_VALUE_IMPUTED | nan | Ludhiana | CORRECTED | 2026-09-15T22:18:11.914164 |
| school_master | SCH0355 | district | MISSING_VALUE_IMPUTED | nan | Jalandhar | CORRECTED | 2026-09-15T22:18:11.914374 |
| school_master | SCH0169 | district | UNRESOLVED_MISSING_DISTRICT | nan | Unassigned | SUSPICIOUS | 2026-09-15T22:18:11.914588 |
| school_master | SCH0381 | district | MISSING_VALUE_IMPUTED | nan | Ferozepur | CORRECTED | 2026-09-15T22:18:11.914809 |
| school_master | SCH0480 | district | MISSING_VALUE_IMPUTED | nan | Ferozepur | CORRECTED | 2026-09-15T22:18:11.915030 |
| school_master | SCH0307 | district | MISSING_VALUE_IMPUTED | nan | Patiala | CORRECTED | 2026-09-15T22:18:11.915238 |
| school_master | SCH0233 | district | MISSING_VALUE_IMPUTED | nan | Ludhiana | CORRECTED | 2026-09-15T22:18:11.915441 |
| school_master | SCH0352 | district | MISSING_VALUE_IMPUTED | nan | Jalandhar | CORRECTED | 2026-09-15T22:18:11.915646 |
| school_master | SCH0002 | district | MISSING_VALUE_IMPUTED | nan | Amritsar | CORRECTED | 2026-09-15T22:18:11.915849 |
| school_master | SCH0576 | district | MISSING_VALUE_IMPUTED | nan | Amritsar | CORRECTED | 2026-09-15T22:18:11.916054 |
| school_master | SCH0316 | district | MISSING_VALUE_IMPUTED | nan | Ludhiana | CORRECTED | 2026-09-15T22:18:11.916256 |
| school_master | SCH0563 | district | MISSING_VALUE_IMPUTED | nan | Bathinda | CORRECTED | 2026-09-15T22:18:11.916460 |
| school_master | SCH0561 | district | MISSING_VALUE_IMPUTED | nan | Sangrur | CORRECTED | 2026-09-15T22:18:11.916648 |
| student_attendance | ATT0001394 | present_students | PROXY_ATTENDANCE_SUNDAY_100PCT | Date: 2025-09-07, Present: 183/183 | Flagged as SUSPICIOUS_PROXY | SUSPICIOUS | 2026-09-15T22:18:12.021857 |
| student_attendance | ATT0003932 | present_students | PROXY_ATTENDANCE_SUNDAY_100PCT | Date: 2025-11-09, Present: 296/296 | Flagged as SUSPICIOUS_PROXY | SUSPICIOUS | 2026-09-15T22:18:12.021884 |
| student_attendance | ATT0016450 | present_students | PROXY_ATTENDANCE_SUNDAY_100PCT | Date: 2026-03-22, Present: 236/236 | Flagged as SUSPICIOUS_PROXY | SUSPICIOUS | 2026-09-15T22:18:12.021903 |


## 3. Transformations & Normalization Verification
1. **Entity IDs**: Regex pattern `r'(\d+)'` successfully mapped all variations (`SCH-`, `sch_`, `S`, `1001`) into 600 canonical `SCHxxxx` entities. Zero orphan records.
2. **Multilingual Booleans**: 22 diverse string representations (`Hai`, `Nahi`, `haan`, `Kharab`, `Broken`, `Working`) mapped to 1/0 with 0 unmapped values.
3. **MDM Unit Normalization**: 1,895 embedded unit strings parsed; Grams divided by 1,000; Sacks/Bags/Bori multiplied by 50 kg; 100% normalized into Kilograms.
4. **Currency Standardization**: Slashes, commas, `Rs.`, and `₹` symbols stripped to pure numerical floats.
5. **Academic FLN Standardization**: Letter Grades, CGPA, Raw Marks, and Percentages mapped to an identical 0-100% scale with matching statistical percentiles.
