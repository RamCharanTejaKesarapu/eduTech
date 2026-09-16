"""
dashboard/components/creator_card.py
Editorial-themed "Built by / The Architect" creator profile and technical dossier.
Matches the Kyoto cyber-editorial aesthetic with:
- Cropped avatar with glowing red circular border and 'ARCHITECT' badge
- Ram Charan Teja attribution with handle @LUN0895 and email
- Full bio, technical tags, and dossier / project links
"""

import os
import base64
import streamlit as st


def _get_pfp_base64() -> str:
    """Load and base64-encode the creator profile picture."""
    asset_path = os.path.join(os.path.dirname(__file__), "..", "assets", "creator_pfp.png")
    if os.path.exists(asset_path):
        with open(asset_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


def render_creator_card():
    """
    Renders the '06 — The Architect // SYSTEM CREATOR & CRAFT' section
    matching the exact reference layout from the user.
    """
    pfp_b64 = _get_pfp_base64()
    pfp_img_html = (
        f'<img src="data:image/png;base64,{pfp_b64}" alt="Ram Charan Teja" class="creator-avatar-img" />'
        if pfp_b64
        else '<span class="creator-avatar-initials">RC</span>'
    )

    card_lines = [
        '<div class="creator-section" id="architect-section">',
        '<div class="creator-kicker">06 — The Architect 創造主 // SYSTEM CREATOR & CRAFT</div>',
        '<div class="creator-headline-row">',
        '<h2 class="creator-headline">CRAFTED BY RAM<br>CHARAN TEJA WITH<br>UNCOMPROMISING<br>VISION.</h2>',
        '<p class="creator-manifesto">Behind this platform is an obsession with merging high-frequency analytical warehousing, reproducible ELT forensics, and a bespoke editorial aesthetic into an autonomous educational intelligence system.</p>',
        '</div>',
        '<div class="creator-card">',
        '<div class="creator-card-body">',
        '<div class="creator-profile-col">',
        '<div class="creator-avatar-container">',
        pfp_img_html,
        '</div>',
        '</div>',
        '<div class="creator-content-col">',
        '<div class="creator-meta-header">',
        '<span class="creator-name">Ram Charan Teja</span>',
        '<span class="creator-badge-handle">@LUN0895</span>',
        '<a href="mailto:luno97802@gmail.com" class="creator-badge-email">✉ luno97802@gmail.com</a>',
        '</div>',
        '<p class="creator-bio">Full-Stack AI Systems Architect, Data Engineer & Creative Technologist. Sole creator and builder of the EduTech Student Retention & Welfare Efficacy Tracker ecosystem.</p>',
        '<div class="creator-tags-row">',
        '<span class="creator-pill-tag">DUCKDB WAREHOUSE</span>',
        '<span class="creator-pill-tag">STREAMLIT BI</span>',
        '<span class="creator-pill-tag">PREDICTIVE ML PIPELINE</span>',
        '<span class="creator-pill-tag">GRAPH-FIRST AI ANALYST</span>',
        '<span class="creator-pill-tag">ELT DATA CLEANING</span>',
        '<span class="creator-pill-tag">INTERACTIVE DECISION MATRIX</span>',
        '<span class="creator-pill-tag">WCAG 2.1 ACCESSIBLE</span>',
        '<span class="creator-pill-tag">HEAVENLY RESTRICTION</span>',
        '</div>',
        '<div class="creator-buttons-row">',
        '<a href="https://github.com/RamCharanTejaKesarapu/eduTech" target="_blank" class="creator-btn creator-btn-dossier">VIEW FULL CREATOR DOSSIER & TECH ARSENAL ↗</a>',
        '<a href="mailto:luno97802@gmail.com?subject=EduTech%20Sponsorship%20Inquiry" class="creator-btn creator-btn-donate">❤ DONATE TO CREATOR</a>',
        '</div>',
        '</div>',
        '</div>',
        '</div>',
        '</div>'
    ]

    clean_html = "".join([line.strip() for line in card_lines])
    st.markdown(clean_html, unsafe_allow_html=True)
