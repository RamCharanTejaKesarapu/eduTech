"""
pipeline/build_duckdb.py
Builds the analytical DuckDB database, populates dimension & fact tables,
and materializes executive analytical data marts.
"""

import os
import duckdb
import pandas as pd
import numpy as np
from .utils import get_processed_data_dir, audit_logger

def build_duckdb_database():
    proc_dir = get_processed_data_dir()
    db_path = os.path.join(proc_dir, "education_data.duckdb")

    # Connect to DuckDB (creates or overwrites)
    if os.path.exists(db_path):
        os.remove(db_path)

    con = duckdb.connect(db_path)

    print(f"[pipeline] Building DuckDB database at {db_path}...")

    # 1. Load Dimension: dim_school
    school_csv = os.path.join(proc_dir, "dim_school.csv")
    con.execute(f"""
        CREATE TABLE dim_school AS 
        SELECT 
            school_id,
            school_name,
            district,
            block,
            CAST(total_enrolled_students AS INTEGER) AS total_enrolled_students,
            school_type,
            medium
        FROM read_csv_auto('{school_csv}');
    """)

    # 2. Load Dimension: dim_vendor
    vendor_csv = os.path.join(proc_dir, "dim_vendor.csv")
    con.execute(f"""
        CREATE TABLE dim_vendor AS 
        SELECT 
            vendor_id,
            vendor_name,
            vendor_group
        FROM read_csv_auto('{vendor_csv}');
    """)

    # 3. Load Fact: fct_attendance
    att_csv = os.path.join(proc_dir, "fct_attendance.csv")
    con.execute(f"""
        CREATE TABLE fct_attendance AS 
        SELECT 
            record_id,
            CAST(attendance_date AS DATE) AS attendance_date,
            day_of_week,
            school_id,
            grade,
            CAST(total_students AS INTEGER) AS total_students,
            CAST(present_students AS INTEGER) AS present_students,
            CAST(attendance_rate_raw AS DOUBLE) AS attendance_rate_raw,
            CAST(attendance_rate_capped AS DOUBLE) AS attendance_rate_capped,
            CAST(teacher_present AS INTEGER) AS teacher_present,
            marked_by,
            CAST(is_sunday AS INTEGER) AS is_sunday,
            CAST(is_proxy_attendance AS INTEGER) AS is_proxy_attendance,
            CAST(is_attendance_overflow AS INTEGER) AS is_attendance_overflow,
            quality_status
        FROM read_csv_auto('{att_csv}');
    """)

    # 4. Load Fact: fct_infrastructure
    infra_csv = os.path.join(proc_dir, "fct_infrastructure.csv")
    con.execute(f"""
        CREATE TABLE fct_infrastructure AS 
        SELECT 
            inspection_id,
            CAST(inspection_date AS DATE) AS inspection_date,
            school_id,
            CAST(has_electricity AS INTEGER) AS has_electricity,
            CAST(has_drinking_water AS INTEGER) AS has_drinking_water,
            CAST(has_functional_toilet AS INTEGER) AS has_functional_toilet,
            CAST(has_boundary_wall AS INTEGER) AS has_boundary_wall,
            CAST(has_playground AS INTEGER) AS has_playground,
            CAST(infra_score AS DOUBLE) AS infra_score,
            CAST(infra_deficit_index AS DOUBLE) AS infra_deficit_index,
            inspector_name,
            remarks
        FROM read_csv_auto('{infra_csv}');
    """)

    # 5. Load Fact: fct_mdm_procurement
    mdm_csv = os.path.join(proc_dir, "fct_mdm_procurement.csv")
    con.execute(f"""
        CREATE TABLE fct_mdm_procurement AS 
        SELECT 
            procurement_id,
            CAST(procurement_date AS DATE) AS procurement_date,
            day_of_week,
            CAST(is_sunday_procurement AS INTEGER) AS is_sunday_procurement,
            school_id,
            vendor_name,
            vendor_group,
            food_category,
            raw_grain_type,
            CAST(quantity_kg AS DOUBLE) AS quantity_kg,
            CAST(total_cost_inr AS DOUBLE) AS total_cost_inr,
            CAST(cost_per_kg AS DOUBLE) AS cost_per_kg,
            payment_status
        FROM read_csv_auto('{mdm_csv}');
    """)

    # 6. Load Fact: fct_test_scores
    scores_csv = os.path.join(proc_dir, "fct_test_scores.csv")
    con.execute(f"""
        CREATE TABLE fct_test_scores AS 
        SELECT 
            assessment_id,
            CAST(assessment_date AS DATE) AS assessment_date,
            school_id,
            grade,
            subject,
            original_scale,
            original_score,
            max_marks,
            CAST(score_percentage AS DOUBLE) AS score_percentage,
            proficiency_tier,
            CAST(total_students_assessed AS INTEGER) AS total_students_assessed
        FROM read_csv_auto('{scores_csv}');
    """)

    # 7. Load Fact: fct_data_quality_log
    audit_df = audit_logger.to_dataframe()
    if not audit_df.empty:
        con.register('temp_audit_df', audit_df)
        con.execute("CREATE TABLE fct_data_quality_log AS SELECT * FROM temp_audit_df;")
    else:
        con.execute("""
            CREATE TABLE fct_data_quality_log (
                dataset VARCHAR,
                record_id VARCHAR,
                column_name VARCHAR,
                issue_type VARCHAR,
                raw_value VARCHAR,
                corrected_value VARCHAR,
                quality_status VARCHAR,
                timestamp VARCHAR
            );
        """)

    # 8. Build Analytical Mart: agg_school_retention_risk
    con.execute("""
        CREATE TABLE agg_school_retention_risk AS
        WITH att_agg AS (
            SELECT 
                school_id,
                COUNT(*) AS total_att_records,
                SUM(CASE WHEN quality_status = 'VALID' THEN 1 ELSE 0 END) AS valid_att_records,
                AVG(CASE WHEN quality_status = 'VALID' THEN attendance_rate_capped ELSE NULL END) AS avg_clean_attendance_rate,
                SUM(is_proxy_attendance) AS proxy_fraud_count,
                SUM(is_attendance_overflow) AS overflow_count,
                ROUND(SUM(is_proxy_attendance) * 100.0 / COUNT(*), 2) AS proxy_fraud_rate_pct
            FROM fct_attendance
            GROUP BY school_id
        ),
        fln_agg AS (
            SELECT 
                school_id,
                COUNT(*) AS total_assessments,
                ROUND(AVG(score_percentage), 2) AS avg_fln_score_pct,
                ROUND(SUM(CASE WHEN score_percentage < 45.0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_below_basic
            FROM fct_test_scores
            GROUP BY school_id
        ),
        infra_agg AS (
            SELECT 
                school_id,
                COUNT(*) AS total_inspections,
                ROUND(AVG(infra_score), 2) AS avg_infra_score,
                ROUND(AVG(infra_deficit_index), 2) AS infra_deficit_index,
                ROUND(AVG(has_electricity) * 100.0, 1) AS electricity_pct,
                ROUND(AVG(has_drinking_water) * 100.0, 1) AS drinking_water_pct,
                ROUND(AVG(has_functional_toilet) * 100.0, 1) AS functional_toilet_pct,
                ROUND(AVG(has_boundary_wall) * 100.0, 1) AS boundary_wall_pct,
                ROUND(AVG(has_playground) * 100.0, 1) AS playground_pct
            FROM fct_infrastructure
            GROUP BY school_id
        ),
        mdm_agg AS (
            SELECT 
                school_id,
                COUNT(*) AS total_mdm_orders,
                ROUND(SUM(quantity_kg), 2) AS total_grain_kg,
                ROUND(SUM(total_cost_inr), 2) AS total_mdm_cost_inr,
                SUM(is_sunday_procurement) AS sunday_orders_count
            FROM fct_mdm_procurement
            GROUP BY school_id
        )
        SELECT 
            s.school_id,
            s.school_name,
            s.district,
            s.block,
            s.school_type,
            s.medium,
            s.total_enrolled_students,
            
            -- Attendance
            COALESCE(a.total_att_records, 0) AS total_att_records,
            COALESCE(a.valid_att_records, 0) AS valid_att_records,
            ROUND(COALESCE(a.avg_clean_attendance_rate, 0.0) * 100.0, 2) AS avg_attendance_rate_pct,
            COALESCE(a.proxy_fraud_count, 0) AS proxy_fraud_count,
            COALESCE(a.proxy_fraud_rate_pct, 0.0) AS proxy_fraud_rate_pct,
            
            -- FLN Academics
            COALESCE(f.total_assessments, 0) AS total_assessments,
            COALESCE(f.avg_fln_score_pct, 65.0) AS avg_fln_score_pct,
            COALESCE(f.pct_below_basic, 0.0) AS pct_below_basic,
            
            -- Infrastructure
            COALESCE(i.avg_infra_score, 70.0) AS avg_infra_score,
            COALESCE(i.infra_deficit_index, 30.0) AS infra_deficit_index,
            COALESCE(i.electricity_pct, 70.0) AS electricity_pct,
            COALESCE(i.drinking_water_pct, 80.0) AS drinking_water_pct,
            COALESCE(i.functional_toilet_pct, 75.0) AS functional_toilet_pct,
            
            -- MDM
            COALESCE(m.total_mdm_orders, 0) AS total_mdm_orders,
            COALESCE(m.total_grain_kg, 0.0) AS total_grain_kg,
            COALESCE(m.total_mdm_cost_inr, 0.0) AS total_mdm_cost_inr,
            ROUND(COALESCE(m.total_grain_kg, 0.0) / NULLIF(s.total_enrolled_students, 0), 2) AS kg_grain_per_student,
            COALESCE(m.sunday_orders_count, 0) AS sunday_procurements,
            
            -- Multi-Factor SRDRI (Student Retention & Dropout Risk Indicator) Components
            CASE 
                WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.65 THEN 100.0
                WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.75 THEN 75.0
                WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.82 THEN 45.0
                ELSE 15.0
            END AS risk_component_absenteeism,
            
            CASE 
                WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 50.0 THEN 100.0
                WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 60.0 THEN 70.0
                WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 70.0 THEN 35.0
                ELSE 10.0
            END AS risk_component_academic,
            
            COALESCE(i.infra_deficit_index, 30.0) AS risk_component_infrastructure,
            
            CASE 
                WHEN (COALESCE(m.total_grain_kg, 0.0) / NULLIF(s.total_enrolled_students, 0)) < 1.5 THEN 80.0
                WHEN (COALESCE(m.total_grain_kg, 0.0) / NULLIF(s.total_enrolled_students, 0)) < 2.5 THEN 40.0
                ELSE 10.0
            END AS risk_component_mdm,

            -- Composite SRDRI Score
            ROUND(
                (0.40 * CASE 
                    WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.65 THEN 100.0
                    WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.75 THEN 75.0
                    WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.82 THEN 45.0
                    ELSE 15.0
                END) +
                (0.30 * CASE 
                    WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 50.0 THEN 100.0
                    WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 60.0 THEN 70.0
                    WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 70.0 THEN 35.0
                    ELSE 10.0
                END) +
                (0.15 * COALESCE(i.infra_deficit_index, 30.0)) +
                (0.15 * CASE 
                    WHEN (COALESCE(m.total_grain_kg, 0.0) / NULLIF(s.total_enrolled_students, 0)) < 1.5 THEN 80.0
                    WHEN (COALESCE(m.total_grain_kg, 0.0) / NULLIF(s.total_enrolled_students, 0)) < 2.5 THEN 40.0
                    ELSE 10.0
                END),
                2
            ) AS srdri_score,

            -- Risk Tier
            CASE 
                WHEN (
                    (0.40 * CASE 
                        WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.65 THEN 100.0
                        WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.75 THEN 75.0
                        WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.82 THEN 45.0
                        ELSE 15.0
                    END) +
                    (0.30 * CASE 
                        WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 50.0 THEN 100.0
                        WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 60.0 THEN 70.0
                        WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 70.0 THEN 35.0
                        ELSE 10.0
                    END) +
                    (0.15 * COALESCE(i.infra_deficit_index, 30.0)) +
                    (0.15 * CASE 
                        WHEN (COALESCE(m.total_grain_kg, 0.0) / NULLIF(s.total_enrolled_students, 0)) < 1.5 THEN 80.0
                        WHEN (COALESCE(m.total_grain_kg, 0.0) / NULLIF(s.total_enrolled_students, 0)) < 2.5 THEN 40.0
                        ELSE 10.0
                    END)
                ) >= 65.0 THEN 'Critical Risk'
                WHEN (
                    (0.40 * CASE 
                        WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.65 THEN 100.0
                        WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.75 THEN 75.0
                        WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.82 THEN 45.0
                        ELSE 15.0
                    END) +
                    (0.30 * CASE 
                        WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 50.0 THEN 100.0
                        WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 60.0 THEN 70.0
                        WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 70.0 THEN 35.0
                        ELSE 10.0
                    END) +
                    (0.15 * COALESCE(i.infra_deficit_index, 30.0)) +
                    (0.15 * CASE 
                        WHEN (COALESCE(m.total_grain_kg, 0.0) / NULLIF(s.total_enrolled_students, 0)) < 1.5 THEN 80.0
                        WHEN (COALESCE(m.total_grain_kg, 0.0) / NULLIF(s.total_enrolled_students, 0)) < 2.5 THEN 40.0
                        ELSE 10.0
                    END)
                ) >= 48.0 THEN 'High Risk'
                WHEN (
                    (0.40 * CASE 
                        WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.65 THEN 100.0
                        WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.75 THEN 75.0
                        WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.82 THEN 45.0
                        ELSE 15.0
                    END) +
                    (0.30 * CASE 
                        WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 50.0 THEN 100.0
                        WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 60.0 THEN 70.0
                        WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 70.0 THEN 35.0
                        ELSE 10.0
                    END) +
                    (0.15 * COALESCE(i.infra_deficit_index, 30.0)) +
                    (0.15 * CASE 
                        WHEN (COALESCE(m.total_grain_kg, 0.0) / NULLIF(s.total_enrolled_students, 0)) < 1.5 THEN 80.0
                        WHEN (COALESCE(m.total_grain_kg, 0.0) / NULLIF(s.total_enrolled_students, 0)) < 2.5 THEN 40.0
                        ELSE 10.0
                    END)
                ) >= 32.0 THEN 'Medium Risk'
                ELSE 'Low Risk'
            END AS srdri_risk_level,

            -- Retention Efficacy Proxy (%)
            ROUND(
                GREATEST(50.0, LEAST(98.0, 100.0 - (
                    (0.40 * CASE 
                        WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.65 THEN 100.0
                        WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.75 THEN 75.0
                        WHEN COALESCE(a.avg_clean_attendance_rate, 0.8) < 0.82 THEN 45.0
                        ELSE 15.0
                    END) +
                    (0.30 * CASE 
                        WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 50.0 THEN 100.0
                        WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 60.0 THEN 70.0
                        WHEN COALESCE(f.avg_fln_score_pct, 65.0) < 70.0 THEN 35.0
                        ELSE 10.0
                    END) +
                    (0.15 * COALESCE(i.infra_deficit_index, 30.0)) +
                    (0.15 * CASE 
                        WHEN (COALESCE(m.total_grain_kg, 0.0) / NULLIF(s.total_enrolled_students, 0)) < 1.5 THEN 80.0
                        WHEN (COALESCE(m.total_grain_kg, 0.0) / NULLIF(s.total_enrolled_students, 0)) < 2.5 THEN 40.0
                        ELSE 10.0
                    END)
                ) * 0.45)),
                2
            ) AS retention_proxy_pct

        FROM dim_school s
        LEFT JOIN att_agg a ON s.school_id = a.school_id
        LEFT JOIN fln_agg f ON s.school_id = f.school_id
        LEFT JOIN infra_agg i ON s.school_id = i.school_id
        LEFT JOIN mdm_agg m ON s.school_id = m.school_id;
    """)

    # 9. Build Analytical Mart: agg_district_summary
    con.execute("""
        CREATE TABLE agg_district_summary AS
        SELECT 
            district,
            COUNT(*) AS total_schools,
            SUM(total_enrolled_students) AS total_enrolled_students,
            ROUND(AVG(avg_attendance_rate_pct), 2) AS avg_attendance_rate_pct,
            ROUND(AVG(proxy_fraud_rate_pct), 2) AS avg_proxy_fraud_rate_pct,
            ROUND(AVG(avg_fln_score_pct), 2) AS avg_fln_score_pct,
            ROUND(AVG(avg_infra_score), 2) AS avg_infra_score,
            ROUND(AVG(infra_deficit_index), 2) AS avg_infra_deficit_index,
            ROUND(SUM(total_grain_kg), 2) AS total_grain_supplied_kg,
            ROUND(SUM(total_mdm_cost_inr), 2) AS total_mdm_spend_inr,
            ROUND(AVG(srdri_score), 2) AS avg_srdri_score,
            SUM(CASE WHEN srdri_risk_level IN ('Critical Risk', 'High Risk') THEN 1 ELSE 0 END) AS vulnerable_schools_count,
            ROUND(AVG(retention_proxy_pct), 2) AS avg_retention_proxy_pct
        FROM agg_school_retention_risk
        GROUP BY district
        ORDER BY vulnerable_schools_count DESC, avg_srdri_score DESC;
    """)

    # 10. Build Analytical Mart: agg_mdm_vendor_summary
    con.execute("""
        CREATE TABLE agg_mdm_vendor_summary AS
        SELECT 
            vendor_name,
            vendor_group,
            COUNT(*) AS total_procurement_records,
            ROUND(SUM(quantity_kg), 2) AS total_volume_kg,
            ROUND(SUM(total_cost_inr), 2) AS total_cost_inr,
            ROUND(AVG(cost_per_kg), 2) AS avg_cost_per_kg,
            SUM(is_sunday_procurement) AS sunday_procurements_count,
            ROUND(SUM(is_sunday_procurement) * 100.0 / COUNT(*), 2) AS sunday_procurement_rate_pct
        FROM fct_mdm_procurement
        GROUP BY vendor_name, vendor_group
        ORDER BY total_cost_inr DESC;
    """)

    # Verify table counts
    tables = con.execute("SHOW TABLES;").fetchall()
    print("[pipeline] DuckDB analytical tables created successfully:")
    for t in tables:
        t_name = t[0]
        cnt = con.execute(f"SELECT COUNT(*) FROM {t_name};").fetchone()[0]
        print(f"  - {t_name}: {cnt} rows")

    con.close()
    print("[pipeline] DuckDB database build complete.")

if __name__ == '__main__':
    build_duckdb_database()
