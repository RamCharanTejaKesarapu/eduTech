"""
agent/chart_selector.py
Graph-First Plotly chart generator for the AI Analyst.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

GOV_THEME = {
    'primary': '#1E3A8A',    # Navy
    'secondary': '#0D9488',  # Teal
    'accent': '#F59E0B',     # Amber
    'danger': '#EF4444',     # Crimson
    'purple': '#6366F1',     # Indigo
    'background': '#FFFFFF',
    'paper': '#F8FAFC',
    'text': '#1E293B',
    'grid': '#E2E8F0'
}

COLOR_SEQUENCE = ['#1E3A8A', '#0D9488', '#F59E0B', '#6366F1', '#EC4899', '#14B8A6', '#8B5CF6', '#F97316']

def style_figure(fig, title=""):
    fig.update_layout(
        title={
            'text': f"<b>{title}</b>" if title else "",
            'font': {'size': 16, 'color': GOV_THEME['text'], 'family': 'Inter, Roboto, sans-serif'},
            'x': 0.02,
            'xanchor': 'left'
        },
        paper_bgcolor=GOV_THEME['paper'],
        plot_bgcolor=GOV_THEME['background'],
        font={'family': 'Inter, Roboto, sans-serif', 'color': GOV_THEME['text']},
        margin={'l': 40, 'r': 30, 't': 50, 'b': 40},
        xaxis={'gridcolor': GOV_THEME['grid'], 'showgrid': True, 'linecolor': '#CBD5E1'},
        yaxis={'gridcolor': GOV_THEME['grid'], 'showgrid': True, 'linecolor': '#CBD5E1'},
        hoverlabel={'bgcolor': '#1E293B', 'font_size': 13, 'font_color': '#FFFFFF'},
        legend={'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'right', 'x': 1}
    )
    return fig

def generate_graph_first_chart(df: pd.DataFrame, chart_type: str, title: str = ""):
    """
    Builds an interactive Plotly figure based on the analytical query result and chart type.
    """
    if df is None or df.empty or len(df.columns) < 2:
        return None

    cols = list(df.columns)

    # 1. Line Chart (Trend)
    if chart_type == 'line':
        x_col = cols[0]
        y_col = cols[1]
        fig = px.line(
            df, x=x_col, y=y_col,
            markers=True,
            line_shape='spline',
            color_discrete_sequence=[GOV_THEME['primary']]
        )
        return style_figure(fig, title)

    # 2. Horizontal Bar Chart (Ranking / Top N)
    elif chart_type == 'horizontal_bar':
        cat_col = cols[0]
        val_col = cols[1]
        # Sort ascending for horizontal bar display
        df_sorted = df.sort_values(val_col, ascending=True)
        fig = px.bar(
            df_sorted, y=cat_col, x=val_col,
            orientation='h',
            text_auto='.1f',
            color=val_col,
            color_continuous_scale=['#93C5FD', '#1E3A8A']
        )
        fig.update_layout(coloraxis_showscale=False)
        return style_figure(fig, title)

    # 3. Bar Chart (Comparison / Grouping)
    elif chart_type == 'bar':
        cat_col = cols[0]
        val_col = cols[1]
        color_col = cols[2] if len(cols) > 2 else None
        fig = px.bar(
            df, x=cat_col, y=val_col,
            color=color_col,
            barmode='group',
            text_auto='.1f',
            color_discrete_sequence=COLOR_SEQUENCE
        )
        return style_figure(fig, title)

    # 4. Scatter Plot (Correlation / Relationship)
    elif chart_type == 'scatter':
        x_col = cols[0]
        y_col = cols[1]
        hover_name = cols[2] if len(cols) > 2 else None
        size_col = cols[3] if len(cols) > 3 else None
        fig = px.scatter(
            df, x=x_col, y=y_col,
            hover_name=hover_name,
            size=size_col,
            trendline='ols' if len(df) > 5 else None,
            color_discrete_sequence=[GOV_THEME['secondary']]
        )
        return style_figure(fig, title)

    # 5. Donut Chart (Distribution / Share)
    elif chart_type == 'donut':
        cat_col = cols[0]
        val_col = cols[1]
        fig = px.pie(
            df, names=cat_col, values=val_col,
            hole=0.45,
            color_discrete_sequence=COLOR_SEQUENCE
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return style_figure(fig, title)

    # Fallback to bar
    cat_col = cols[0]
    val_col = cols[1]
    fig = px.bar(df, x=cat_col, y=val_col, color_discrete_sequence=[GOV_THEME['primary']])
    return style_figure(fig, title)
