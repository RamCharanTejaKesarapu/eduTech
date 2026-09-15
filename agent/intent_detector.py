"""
agent/intent_detector.py
Natural language intent detection and Graph-First visualization routing.
"""

import re

GRAPH_FIRST_KEYWORDS = [
    'show', 'plot', 'chart', 'trend', 'compare', 'comparison', 'distribution',
    'relationship', 'correlation', 'ranking', 'top', 'bottom', 'breakdown',
    'graph', 'visualize', 'spread', 'proportion', 'highest', 'lowest'
]

DISTRICTS = [
    'amritsar', 'bathinda', 'ferozepur', 'jalandhar', 'ludhiana', 'moga', 'patiala', 'sangrur'
]

SUBJECTS = [
    'math', 'mathematics', 'ganit', 'science', 'english', 'hindi', 'punjabi', 'evs'
]

VENDORS = [
    'sharma', 'goyal', 'kumar', 'singh'
]

def detect_query_intent(user_query: str):
    """
    Analyzes user natural language question and returns structured intent metadata.
    """
    q = user_query.strip().lower()

    # Determine if visualization is requested (Graph-First rule)
    requires_chart = any(k in q for k in GRAPH_FIRST_KEYWORDS)

    # Detect entity filters
    detected_district = None
    for d in DISTRICTS:
        if d in q:
            detected_district = d.title()
            break

    detected_subject = None
    for s in SUBJECTS:
        if s in q:
            detected_subject = 'Mathematics' if s in ['math', 'ganit'] else s.title()
            break

    school_id_match = re.search(r'sch[_-]?(\d+)', q)
    detected_school_id = f"SCH{int(school_id_match.group(1)):04d}" if school_id_match else None

    # Detect primary intent
    intent = 'summary'
    chart_type = 'metric'

    if any(k in q for k in ['trend', 'over time', 'monthly', 'daily', 'academic year']):
        intent = 'trend'
        chart_type = 'line'
        requires_chart = True

    elif any(k in q for k in ['top', 'bottom', 'highest', 'lowest', 'rank', 'ranking']):
        intent = 'ranking'
        chart_type = 'horizontal_bar'
        requires_chart = True

    elif any(k in q for k in ['compare', 'comparison', 'versus', 'vs', 'difference between']):
        intent = 'comparison'
        chart_type = 'bar'
        requires_chart = True

    elif any(k in q for k in ['relat', 'correlat', 'scatter', 'impact of', 'effect of']):
        intent = 'correlation'
        chart_type = 'scatter'
        requires_chart = True

    elif any(k in q for k in ['distribution', 'spread', 'scale', 'breakdown', 'share', 'proportion']):
        intent = 'distribution'
        chart_type = 'donut'
        requires_chart = True

    elif any(k in q for k in ['sunday', 'proxy', 'anomal', 'fraud', 'overflow']):
        intent = 'anomaly'
        chart_type = 'horizontal_bar'
        requires_chart = True

    elif detected_school_id:
        intent = 'lookup'
        chart_type = 'bar' if requires_chart else 'metric'

    return {
        'original_query': user_query,
        'intent': intent,
        'requires_chart': requires_chart,
        'chart_type': chart_type,
        'entities': {
            'district': detected_district,
            'subject': detected_subject,
            'school_id': detected_school_id
        }
    }
