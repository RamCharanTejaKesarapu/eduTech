"""
dashboard/components/theme.py
Editorial Design System & Plotly Theme.
Implements the Meng To Sketchbook aesthetic (Instrument Serif, Newsreader, Warm Paper & Charcoal Ink).
"""

import plotly.io as pio
import plotly.graph_objects as go

# Color Tokens
INK = "#2b2721"
INK_SOFT = "rgba(43, 39, 33, 0.58)"
INK_FAINT = "rgba(43, 39, 33, 0.36)"
HAIRLINE = "rgba(43, 39, 33, 0.14)"
PAPER = "#f7f4ed"
PAPER_CARD = "#fbf9f5"
EARTH = "#9a6a3e"
BRASS = "#c2a26a"
VERMILION = "#b34f3e"
MOSS = "#486950"
SLATE_BLUE = "#4a677a"

COLORWAY = [
    "#2b2721",  # Warm Charcoal Ink
    "#9a6a3e",  # Earth / Cognac Terracotta
    "#b34f3e",  # Vermilion
    "#486950",  # Botanical Moss Green
    "#c2a26a",  # Warm Brass / Gold
    "#4a677a",  # Muted River Slate
    "#785b46",  # Deep Ochre
]

# Configure global Plotly template
editorial_template = go.layout.Template(
    layout=go.Layout(
        font=dict(family="'Newsreader', Georgia, 'Times New Roman', serif", color=INK, size=13),
        title=dict(
            font=dict(family="'Instrument Serif', Georgia, 'Times New Roman', serif", size=22, color=INK)
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#fcfbf8",
        colorway=COLORWAY,
        xaxis=dict(
            gridcolor="rgba(43, 39, 33, 0.07)",
            linecolor="rgba(43, 39, 33, 0.22)",
            tickfont=dict(family="'Newsreader', serif", size=12, color=INK),
            title_font=dict(family="'Instrument Serif', serif", size=15, color=INK),
            zerolinecolor="rgba(43, 39, 33, 0.15)"
        ),
        yaxis=dict(
            gridcolor="rgba(43, 39, 33, 0.07)",
            linecolor="rgba(43, 39, 33, 0.22)",
            tickfont=dict(family="'Newsreader', serif", size=12, color=INK),
            title_font=dict(family="'Instrument Serif', serif", size=15, color=INK),
            zerolinecolor="rgba(43, 39, 33, 0.15)"
        ),
        legend=dict(
            font=dict(family="'Newsreader', serif", size=12, color=INK),
            bgcolor="rgba(251, 249, 245, 0.85)",
            bordercolor="rgba(43, 39, 33, 0.12)",
            borderwidth=1
        ),
        margin=dict(l=40, r=20, t=50, b=40)
    )
)

pio.templates["editorial"] = editorial_template
pio.templates.default = "editorial"

def apply_editorial_theme(fig, title: str = None):
    """Apply editorial styling to any Plotly figure."""
    updates = {
        "template": "editorial",
        "font_family": "'Newsreader', Georgia, serif",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "#fcfbf8",
        "font_color": INK
    }
    if title:
        updates["title"] = dict(
            text=title,
            font=dict(family="'Instrument Serif', Georgia, serif", size=22, color=INK)
        )
    fig.update_layout(**updates)
    fig.update_xaxes(gridcolor="rgba(43, 39, 33, 0.07)", linecolor="rgba(43, 39, 33, 0.22)")
    fig.update_yaxes(gridcolor="rgba(43, 39, 33, 0.07)", linecolor="rgba(43, 39, 33, 0.22)")
    return fig
