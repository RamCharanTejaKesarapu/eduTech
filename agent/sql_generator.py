"""
agent/sql_generator.py
Synthesizes safe, schema-grounded DuckDB SQL queries from natural language input.
Works 100% locally and deterministically.
"""

import re

def generate_analytical_sql(intent_meta: dict) -> tuple:
    """
    Translates detected user intent into a safe, valid DuckDB SQL query and chart suggestion.
    
    Returns:
        tuple: (sql_query: str, chart_title: str, chart_type: str)
    """
    q = intent_meta['original_query'].strip().lower()
    entities = intent_meta.get('entities', {})
    district = entities.get('district')
    school_id = entities.get('school_id')

    # Query 1: Total number of students
    if ('total' in q or 'how many' in q) and 'student' in q and not any(k in q for k in ['district', 'top', 'bottom', 'by']):
        sql = "SELECT SUM(total_enrolled_students) AS total_students FROM dim_school;"
        return sql, "Total Student Enrollment", "metric"

    # Query 2: Total number of schools
    if ('total' in q or 'how many' in q) and 'school' in q and not any(k in q for k in ['district', 'top', 'bottom', 'by']):
        sql = "SELECT COUNT(*) AS total_schools FROM dim_school;"
        return sql, "Total Government Schools", "metric"

    # Query 3: District with highest proxy attendance anomalies
    if ('proxy' in q or 'anomal' in q or 'fraud' in q) and ('district' in q or 'highest' in q):
        sql = """
        SELECT 
            district,
            SUM(proxy_fraud_count) AS total_proxy_records,
            ROUND(AVG(proxy_fraud_rate_pct), 2) AS avg_proxy_fraud_rate_pct
        FROM agg_school_retention_risk
        GROUP BY district
        ORDER BY avg_proxy_fraud_rate_pct DESC;
        """
        return sql.strip(), "Proxy Attendance Fraud Rate by District (%)", "horizontal_bar"

    # Query 4: Monthly attendance trend
    if any(k in q for k in ['trend', 'over time', 'monthly', 'month']) and 'attendance' in q:
        sql = """
        SELECT 
            strftime(attendance_date, '%Y-%m') AS month,
            ROUND(AVG(attendance_rate_capped) * 100.0, 2) AS avg_attendance_pct
        FROM fct_attendance
        WHERE quality_status = 'VALID'
        GROUP BY month
        ORDER BY month;
        """
        return sql.strip(), "Monthly Average Student Attendance Trend (%)", "line"

    # Query 5: Compare test scores by electricity
    if ('electric' in q) and ('test' in q or 'score' in q or 'performance' in q or 'fln' in q):
        sql = """
        SELECT 
            CASE WHEN i.has_electricity = 1 THEN 'With Functional Electricity' ELSE 'Without Electricity' END AS electricity_status,
            ROUND(AVG(t.score_percentage), 2) AS avg_fln_score_pct
        FROM fct_test_scores t
        JOIN fct_infrastructure i ON t.school_id = i.school_id
        GROUP BY electricity_status;
        """
        return sql.strip(), "Average FLN Score by Electricity Availability (%)", "bar"

    # Query 6: Compare attendance by electricity
    if ('electric' in q) and ('attendance' in q or 'rate' in q):
        sql = """
        SELECT 
            CASE WHEN i.has_electricity = 1 THEN 'With Electricity' ELSE 'Without Electricity' END AS electricity_status,
            ROUND(AVG(a.attendance_rate_capped) * 100.0, 2) AS avg_attendance_pct
        FROM fct_attendance a
        JOIN fct_infrastructure i ON a.school_id = i.school_id
        WHERE a.quality_status = 'VALID'
        GROUP BY electricity_status;
        """
        return sql.strip(), "Average Attendance Rate by Electricity Availability (%)", "bar"

    # Query 7: Compare attendance by drinking water
    if ('water' in q) and ('attendance' in q or 'rate' in q or 'impact' in q):
        sql = """
        SELECT 
            CASE WHEN i.has_drinking_water = 1 THEN 'With Drinking Water' ELSE 'Without Drinking Water' END AS water_status,
            ROUND(AVG(a.attendance_rate_capped) * 100.0, 2) AS avg_attendance_pct
        FROM fct_attendance a
        JOIN fct_infrastructure i ON a.school_id = i.school_id
        WHERE a.quality_status = 'VALID'
        GROUP BY water_status;
        """
        return sql.strip(), "Impact of Drinking Water on Attendance (%)", "bar"

    # Query 8: Compare attendance by toilet
    if ('toilet' in q) and ('attendance' in q or 'rate' in q or 'female' in q or 'impact' in q):
        sql = """
        SELECT 
            CASE WHEN i.has_functional_toilet = 1 THEN 'With Functional Toilets' ELSE 'Without Functional Toilets' END AS toilet_status,
            ROUND(AVG(a.attendance_rate_capped) * 100.0, 2) AS avg_attendance_pct
        FROM fct_attendance a
        JOIN fct_infrastructure i ON a.school_id = i.school_id
        WHERE a.quality_status = 'VALID'
        GROUP BY toilet_status;
        """
        return sql.strip(), "Attendance Rate by Functional Toilet Availability (%)", "bar"

    # Query 9: Correlation: Attendance vs Test Scores
    if ('relat' in q or 'correlat' in q or 'versus' in q) and ('attendance' in q and ('score' in q or 'fln' in q or 'academic' in q)):
        sql = """
        SELECT 
            avg_attendance_rate_pct,
            avg_fln_score_pct,
            school_name,
            total_enrolled_students
        FROM agg_school_retention_risk
        ORDER BY total_enrolled_students DESC
        LIMIT 200;
        """
        return sql.strip(), "Correlation: Attendance Rate vs FLN Test Scores", "scatter"

    # Query 10: Top N schools with highest dropout / retention risk
    if ('highest' in q or 'top' in q or 'most vulnerable' in q) and ('risk' in q or 'dropout' in q or 'retention' in q):
        limit = 10
        m = re.search(r'\b(\d+)\b', q)
        if m:
            limit = int(m.group(1))
        sql = f"""
        SELECT 
            school_name,
            srdri_score,
            district,
            srdri_risk_level
        FROM agg_school_retention_risk
        ORDER BY srdri_score DESC
        LIMIT {limit};
        """
        return sql.strip(), f"Top {limit} Schools by Student Retention & Dropout Risk (SRDRI)", "horizontal_bar"

    # Query 11: District with lowest average test scores
    if ('district' in q) and ('lowest' in q or 'worst' in q or 'poor' in q) and ('test' in q or 'score' in q or 'fln' in q):
        sql = """
        SELECT 
            district,
            ROUND(AVG(avg_fln_score_pct), 2) AS avg_fln_score_pct
        FROM agg_school_retention_risk
        GROUP BY district
        ORDER BY avg_fln_score_pct ASC;
        """
        return sql.strip(), "Average FLN Test Score by District (%)", "horizontal_bar"

    # Query 12: MDM procurement cost by vendor
    if ('mdm' in q or 'vendor' in q or 'grain' in q or 'food' in q) and ('cost' in q or 'spend' in q or 'budget' in q):
        sql = """
        SELECT 
            vendor_name,
            ROUND(SUM(total_cost_inr), 2) AS total_spend_inr
        FROM fct_mdm_procurement
        GROUP BY vendor_name
        ORDER BY total_spend_inr DESC;
        """
        return sql.strip(), "Total MDM Procurement Spend by Vendor (INR)", "horizontal_bar"

    # Query 13: MDM volume and supply analysis by vendor
    if ('vendor' in q or 'supply' in q) and ('volume' in q or 'quantity' in q or 'grain' in q):
        sql = """
        SELECT 
            vendor_name,
            ROUND(SUM(quantity_kg), 2) AS total_volume_kg,
            ROUND(SUM(total_cost_inr), 2) AS total_spend_inr
        FROM fct_mdm_procurement
        GROUP BY vendor_name
        ORDER BY total_volume_kg DESC;
        """
        return sql.strip(), "Vendor-wise MDM Supply Volume (KG)", "horizontal_bar"

    # Query 14: Schools that reported 100% attendance on Sundays
    if ('sunday' in q) and ('100' in q or 'proxy' in q or 'fraud' in q or 'school' in q):
        sql = """
        SELECT 
            s.school_name,
            COUNT(*) AS sunday_100pct_records,
            s.district
        FROM fct_attendance a
        JOIN dim_school s ON a.school_id = s.school_id
        WHERE a.is_proxy_attendance = 1
        GROUP BY s.school_name, s.district
        ORDER BY sunday_100pct_records DESC
        LIMIT 10;
        """
        return sql.strip(), "Top 10 Schools with 100% Sunday Proxy Attendance Records", "horizontal_bar"

    # Query 15: Distribution of grading scales
    if ('scale' in q or 'grading' in q or 'evaluation' in q) and ('distribution' in q or 'breakdown' in q or 'share' in q or 'used' in q):
        sql = """
        SELECT 
            original_scale AS grading_scale,
            COUNT(*) AS total_assessments
        FROM fct_test_scores
        GROUP BY original_scale
        ORDER BY total_assessments DESC;
        """
        return sql.strip(), "Distribution of Raw FLN Grading Scales", "donut"

    # Query 16: Top schools with highest MDM grain wastage / procurement ratio
    if ('wastage' in q or 'highest mdm' in q or 'grain per student' in q or 'anomalous procurement' in q):
        sql = """
        SELECT 
            school_name,
            kg_grain_per_student,
            total_enrolled_students,
            district
        FROM agg_school_retention_risk
        ORDER BY kg_grain_per_student DESC
        LIMIT 10;
        """
        return sql.strip(), "Top 10 Schools by MDM Grain Supplied per Student (KG)", "horizontal_bar"

    # Query 17: Math vs Science test scores by district
    if ('math' in q and 'science' in q) and 'district' in q:
        sql = """
        SELECT 
            s.district,
            ROUND(AVG(CASE WHEN t.subject = 'Mathematics' THEN t.score_percentage ELSE NULL END), 2) AS math_score_pct,
            ROUND(AVG(CASE WHEN t.subject = 'Science' THEN t.score_percentage ELSE NULL END), 2) AS science_score_pct
        FROM fct_test_scores t
        JOIN dim_school s ON t.school_id = s.school_id
        GROUP BY s.district
        ORDER BY s.district;
        """
        return sql.strip(), "Comparison: Mathematics vs Science FLN Scores by District (%)", "bar"

    # Query 18: Specific school lookup
    if school_id:
        sql = f"""
        SELECT 
            school_name,
            district,
            school_type,
            total_enrolled_students,
            avg_attendance_rate_pct,
            avg_fln_score_pct,
            avg_infra_score,
            srdri_score,
            srdri_risk_level
        FROM agg_school_retention_risk
        WHERE school_id = '{school_id}';
        """
        return sql.strip(), f"School Profile: {school_id}", "bar"

    # Default fallback query: District overview ranking
    sql = """
    SELECT 
        district,
        total_schools,
        total_enrolled_students,
        avg_attendance_rate_pct,
        avg_proxy_fraud_rate_pct,
        avg_fln_score_pct,
        avg_infra_score,
        vulnerable_schools_count
    FROM agg_district_summary
    ORDER BY vulnerable_schools_count DESC;
    """
    return sql.strip(), "District Executive Performance Summary", "bar"
