"""
dashboard/pages/8_AI_Analyst.py
Graph-First AI Analyst: Conversational intelligence with automated SQL generation and visualization.
"""

import os
import sys
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="AI Graph-First Analyst • EduTech",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), "..", "styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Add project root to sys.path
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

from agent.ai_analyst import agent_instance
from components.kpi_cards import render_page_header
from components.top_nav import render_top_masthead
from components.creator_card import render_creator_card
from components.footer import render_editorial_footer

render_top_masthead("AI Agent")

render_page_header(
    title="AI Graph-First Analyst",
    subtitle="Natural Language Decision Intelligence with Safe DuckDB SQL Execution & Automated Plotly Charting",
    badge="Autonomous AgentIQ AI"
)

st.markdown("""
Ask any question regarding student attendance, Mid-Day Meal procurement, infrastructure quality, or student retention risk.
The **Graph-First AI Engine** automatically plans an analytical query, validates security guardrails, executes against DuckDB,
and renders an interactive Plotly visualization alongside a data-grounded synthesis.
""")

# Quick Prompt Suggestions
st.markdown("##### 💡 Suggested Executive Inquiries (Click to run):")
col_s1, col_s2, col_s3 = st.columns(3)

prompt_choice = None

with col_s1:
    if st.button("🚨 Highest proxy fraud district?"):
        prompt_choice = "Which district has the highest proxy attendance anomalies?"
    if st.button("📈 Monthly attendance trend?"):
        prompt_choice = "Show me the monthly trend of average student attendance."
    if st.button("⚡ Electricity vs test scores?"):
        prompt_choice = "Compare average test scores between schools with and without functional electricity."
    if st.button("🏫 Top 10 highest risk schools?"):
        prompt_choice = "Show me the 10 schools with the highest dropout rate."

with col_s2:
    if st.button("📊 Attendance vs Test Scores correlation?"):
        prompt_choice = "Is attendance related to test scores?"
    if st.button("💰 Total MDM cost by vendor?"):
        prompt_choice = "Show total MDM procurement cost by vendor."
    if st.button("📅 100% attendance on Sundays?"):
        prompt_choice = "Which schools reported 100% attendance on Sundays?"
    if st.button("🎓 Distribution of grading scales?"):
        prompt_choice = "Show the distribution of grading scales used across schools."

with col_s3:
    if st.button("🍲 Top 10 schools by grain per student?"):
        prompt_choice = "Show top 10 schools with highest MDM grain wastage."
    if st.button("💧 Impact of drinking water?"):
        prompt_choice = "Impact of functional drinking water on overall attendance %."
    if st.button("📐 Math vs Science by district?"):
        prompt_choice = "Average test scores in Math vs Science across districts."
    if st.button("👥 Total enrolled students?"):
        prompt_choice = "What is the total number of students?"

# User Query Input
user_query = st.text_input(
    "Or type your custom question here:",
    value=prompt_choice or "",
    placeholder="e.g. Which district has the lowest average test scores?"
)

run_button = st.button("🚀 Analyze with AI Analyst", type="primary")

if (run_button or prompt_choice) and user_query:
    with st.spinner("Analyzing intent, synthesizing SQL, enforcing security guardrails, and querying DuckDB..."):
        res = agent_instance.answer_question(user_query)

    if not res['is_success']:
        st.error(f"❌ {res['error']}")
    else:
        st.markdown("---")
        st.markdown("### 💬 Executive Intelligence Synthesis")

        # Display Natural Language Answer
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 5px solid #1E3A8A; background-color: #F8FAFC;">
            <div style="font-size: 16px; color: #0F172A; margin-bottom: 8px;">{res['answer']}</div>
            <div style="font-size: 13px; color: #64748B;">{res['explanation']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Graph-First Visualization
        if res.get('chart'):
            st.markdown(f"### 📈 Graph-First Visualization: {res.get('chart_title', 'Analytical Result')}")
            st.plotly_chart(res['chart'], use_container_width=True)

        # Forensic Audit Details (Expandable)
        with st.expander("🛠️ Generated SQL Query & Security Guardrail Audit", expanded=False):
            st.markdown(f"**Detected Intent:** `{res['intent']}`")
            st.markdown("**Validated Read-Only DuckDB SQL:**")
            st.code(res['sql'], language="sql")
            st.success("✅ Passed strict AST security guardrails (Read-Only SELECT; zero destructive operations allowed).")

        # Raw Result Data Table
        if res.get('result_df') is not None and not res['result_df'].empty:
            with st.expander(f"📋 Analytical Result Dataset ({len(res['result_df'])} records)", expanded=False):
                st.dataframe(res['result_df'], use_container_width=True)

# Render The Architect (Creator Profile) and Project Reference Mega-Footer
render_creator_card()
render_editorial_footer()
