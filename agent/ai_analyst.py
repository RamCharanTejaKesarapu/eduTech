"""
agent/ai_analyst.py
Main Graph-First AI Analyst orchestrator.
Executes intent parsing, safe SQL synthesis, AST guardrail validation,
DuckDB query execution, and interactive Plotly chart rendering.
"""

import os
from typing import Optional, Tuple, Dict, Any
import duckdb
import pandas as pd
from .intent_detector import detect_query_intent
from .sql_generator import generate_analytical_sql
from .sql_guardrails import validate_sql_query
from .chart_selector import generate_graph_first_chart

def get_duckdb_path() -> str:
    proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(proj_root, "data", "processed", "education_data.duckdb")

class AIAnalystAgent:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or get_duckdb_path()

    def is_database_available(self) -> bool:
        """
        Checks whether the DuckDB analytical database exists and is readable.
        """
        if not os.path.exists(self.db_path):
            return False
        try:
            con = duckdb.connect(self.db_path, read_only=True)
            con.close()
            return True
        except Exception:
            return False

    def execute_safe_query(self, sql_query: str) -> pd.DataFrame:
        """
        Validates SQL against guardrails and executes it read-only on DuckDB.
        Raises ValueError if query violates guardrails or runtime error on DB failure.
        """
        is_safe, error_msg = validate_sql_query(sql_query)
        if not is_safe:
            raise ValueError(f"SQL Guardrail Violation: {error_msg}")
        con = duckdb.connect(self.db_path, read_only=True)
        try:
            return con.execute(sql_query).df()
        finally:
            con.close()

    def answer_question(self, user_question: str) -> Dict[str, Any]:
        """
        Processes a natural language question through the Graph-First AI Pipeline.
        """
        if not user_question or not user_question.strip():
            return {
                'is_success': False,
                'error': 'Please enter a question to analyze.',
                'answer': 'Please enter a valid question.',
                'sql': None,
                'chart': None,
                'result_df': None,
                'intent': 'empty'
            }

        # 1. Intent Detection
        intent_meta = detect_query_intent(user_question)

        # 2. SQL Synthesis
        sql_query, chart_title, chart_type = generate_analytical_sql(intent_meta)

        # 3. Security & Safety Validation
        is_safe, error_msg = validate_sql_query(sql_query)
        if not is_safe:
            return {
                'is_success': False,
                'error': error_msg,
                'answer': f"Query rejected by AI Safety Guardrails: {error_msg}",
                'sql': sql_query,
                'chart': None,
                'result_df': None,
                'intent': intent_meta['intent']
            }

        # 4. DuckDB Analytical Execution
        try:
            result_df = self.execute_safe_query(sql_query)
        except Exception as e:
            return {
                'is_success': False,
                'error': str(e),
                'answer': f"Database execution error: {str(e)}",
                'sql': sql_query,
                'chart': None,
                'result_df': None,
                'intent': intent_meta['intent']
            }

        # 5. Graph-First Chart Generation
        chart = None
        if intent_meta['requires_chart'] and not result_df.empty:
            chart = generate_graph_first_chart(result_df, chart_type, title=chart_title)

        # 6. Natural Language Answer & Analytical Context Synthesis
        answer, explanation = self._synthesize_response(user_question, intent_meta, result_df, sql_query)

        return {
            'is_success': True,
            'error': None,
            'intent': intent_meta['intent'],
            'sql': sql_query,
            'chart': chart,
            'chart_title': chart_title,
            'result_df': result_df,
            'answer': answer,
            'explanation': explanation
        }

    def _synthesize_response(self, user_question: str, intent_meta: dict, df: pd.DataFrame, sql: str) -> tuple:
        """
        Synthesizes concise, data-grounded answers without hallucination.
        Never implies causality from correlation.
        """
        if df.empty:
            return "No matching records found in the official education dataset.", "The query executed safely but returned 0 matching rows."

        # Case 1: Single scalar metric
        if len(df) == 1 and len(df.columns) == 1:
            col = df.columns[0]
            val = df.iloc[0, 0]
            if isinstance(val, (int, float)):
                val_formatted = f"{val:,.0f}" if isinstance(val, int) or val > 100 else f"{val:.2f}"
            else:
                val_formatted = str(val)
            col_label = col.replace('_', ' ').title()
            answer = f"**{col_label}**: {val_formatted}"
            explanation = f"Calculated from the verified data records in the analytical model ({col} = {val_formatted})."
            return answer, explanation

        # Case 2: Ranking / District Highest / Lowest
        if intent_meta['intent'] == 'ranking' or 'district' in user_question.lower():
            first_row = df.iloc[0]
            cat_col = df.columns[0]
            val_col = df.columns[1]
            top_entity = first_row[cat_col]
            top_val = first_row[val_col]
            val_str = f"{top_val:,.1f}" if isinstance(top_val, (int, float)) else str(top_val)

            answer = f"**{top_entity}** ranks highest with a value of **{val_str}** for `{val_col}`."
            explanation = f"Based on ranking across {len(df)} entities in the processed education dataset."
            return answer, explanation

        # Case 3: Comparison (e.g. electricity vs no electricity)
        if intent_meta['intent'] == 'comparison':
            cat_col = df.columns[0]
            val_col = df.columns[1]
            rows_desc = [f"- **{row[cat_col]}**: {row[val_col]:.2f}%" for _, row in df.iterrows()]
            answer = f"Observed comparison across groups:\n" + "\n".join(rows_desc)
            explanation = "Note: These represent observed historical averages across inspected government schools; no causal effect is claimed."
            return answer, explanation

        # Case 4: Correlation
        if intent_meta['intent'] == 'correlation':
            x_col = df.columns[0]
            y_col = df.columns[1]
            corr = df[[x_col, y_col]].corr().iloc[0, 1]
            answer = f"The sample correlation between `{x_col}` and `{y_col}` across {len(df)} schools is **{corr:.2f}**."
            explanation = "A positive/neutral association is observed in the distribution. Wording adheres to correlation and does not imply causation."
            return answer, explanation

        # Case 5: Trend
        if intent_meta['intent'] == 'trend':
            date_col = df.columns[0]
            val_col = df.columns[1]
            start_val = df.iloc[0][val_col]
            end_val = df.iloc[-1][val_col]
            answer = f"Tracking over {len(df)} periods shows an initial average of **{start_val:.1f}%** moving to **{end_val:.1f}%**."
            explanation = f"Longitudinal attendance data aggregated monthly from verified daily logs across all schools."
            return answer, explanation

        # General response
        first_col = df.columns[0]
        answer = f"Found {len(df)} analytical records matching your inquiry."
        explanation = f"Query executed successfully over DuckDB analytical mart (`{first_col}`)."
        return answer, explanation

# Singleton instance
agent_instance = AIAnalystAgent()
