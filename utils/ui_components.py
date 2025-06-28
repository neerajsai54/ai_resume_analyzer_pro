"""
UI Components for Enhanced Resume Analyzer
Provides reusable, styled Streamlit components with consistent theming.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional
import base64
from datetime import datetime

def load_custom_css():
    """Load custom CSS for enhanced UI styling."""
    css = """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }

    /* Custom Components */
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }

    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    }

    .score-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1.1rem;
        text-align: center;
        margin: 0.5rem 0;
    }

    .score-excellent {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    .score-good {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }

    .score-average {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
    }

    .score-poor {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
    }

    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .alert-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .alert-info {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .progress-container {
        background-color: #e9ecef;
        border-radius: 25px;
        padding: 3px;
        margin: 1rem 0;
    }

    .progress-bar {
        height: 25px;
        border-radius: 25px;
        text-align: center;
        line-height: 25px;
        color: white;
        font-weight: 600;
        font-size: 0.9rem;
        transition: width 0.6s ease;
    }

    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }

    .recommendation-item {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #28a745;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .fade-in {
        animation: fadeIn 0.5s ease-in-out;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .feature-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }

        .metric-card {
            padding: 1rem;
        }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def create_feature_card(title: str, description: str, icon: str = "⭐") -> None:
    """Create a styled feature card."""
    card_html = f"""
    <div class="feature-card fade-in">
        <h3>{icon} {title}</h3>
        <p>{description}</p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def create_score_badge(score: float, label: str = "Score") -> None:
    """Create a styled score badge with color coding."""
    if score >= 85:
        css_class = "score-excellent"
    elif score >= 70:
        css_class = "score-good"
    elif score >= 50:
        css_class = "score-average"
    else:
        css_class = "score-poor"

    badge_html = f"""
    <div class="score-badge {css_class}">
        {label}: {score:.0f}/100
    </div>
    """
    st.markdown(badge_html, unsafe_allow_html=True)

def create_alert(message: str, alert_type: str = "info") -> None:
    """
    Create styled alert boxes.

    Args:
        message: Alert message
        alert_type: Type of alert (success, warning, error, info)
    """
    alert_html = f"""
    <div class="alert-{alert_type}">
        {message}
    </div>
    """
    st.markdown(alert_html, unsafe_allow_html=True)

def create_progress_bar(value: float, max_value: float = 100, 
                       label: str = "", color: str = "#667eea") -> None:
    """Create an animated progress bar."""
    percentage = (value / max_value) * 100

    progress_html = f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {percentage}%; background: {color};">
            {label} {percentage:.0f}%
        </div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)

def create_metric_card(title: str, value: str, delta: str = "", 
                      delta_color: str = "normal") -> None:
    """Create a styled metric card."""
    delta_style = ""
    if delta:
        if delta_color == "positive":
            delta_style = "color: #28a745;"
        elif delta_color == "negative":
            delta_style = "color: #dc3545;"

    card_html = f"""
    <div class="metric-card fade-in">
        <h4 style="margin: 0; color: #495057;">{title}</h4>
        <h2 style="margin: 0.5rem 0; color: #212529;">{value}</h2>
        {f'<p style="margin: 0; {delta_style}">{delta}</p>' if delta else ''}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def create_recommendation_list(recommendations: List[str], 
                             title: str = "Recommendations") -> None:
    """Create a styled list of recommendations."""
    st.subheader(title)

    for i, recommendation in enumerate(recommendations, 1):
        rec_html = f"""
        <div class="recommendation-item fade-in">
            <strong>{i}.</strong> {recommendation}
        </div>
        """
        st.markdown(rec_html, unsafe_allow_html=True)

def create_two_column_layout(left_content, right_content):
    """Create a responsive two-column layout."""
    col1, col2 = st.columns(2)

    with col1:
        left_content()

    with col2:
        right_content()

def create_tabs_container(tabs_config: Dict[str, callable]):
    """
    Create a tabbed interface with custom content.

    Args:
        tabs_config: Dictionary with tab names as keys and functions as values
    """
    tabs = st.tabs(list(tabs_config.keys()))

    for tab, (tab_name, content_func) in zip(tabs, tabs_config.items()):
        with tab:
            content_func()

def display_file_info(file_info: Dict[str, Any]) -> None:
    """Display file information in a styled card."""
    if not file_info:
        return

    info_html = f"""
    <div class="metric-card">
        <h4>📄 File Information</h4>
        <p><strong>Name:</strong> {file_info.get('name', 'N/A')}</p>
        <p><strong>Size:</strong> {file_info.get('size', 0):,} bytes</p>
        <p><strong>Type:</strong> {file_info.get('extension', 'unknown').upper()}</p>
    </div>
    """
    st.markdown(info_html, unsafe_allow_html=True)

def create_radar_chart(data: Dict[str, float], title: str = "Skills Assessment"):
    """Create a radar chart for skills or scores visualization."""
    categories = list(data.keys())
    values = list(data.values())

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Score',
        line_color='#667eea',
        fillcolor='rgba(102, 126, 234, 0.25)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title=title,
        font=dict(family="Inter, sans-serif")
    )

    return fig

def create_score_distribution_chart(scores: Dict[str, float]):
    """Create a horizontal bar chart for score distribution."""
    categories = list(scores.keys())
    values = list(scores.values())

    # Color code based on score ranges
    colors = []
    for score in values:
        if score >= 85:
            colors.append('#28a745')  # Green
        elif score >= 70:
            colors.append('#17a2b8')  # Blue
        elif score >= 50:
            colors.append('#ffc107')  # Yellow
        else:
            colors.append('#dc3545')  # Red

    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation='h',
        marker_color=colors,
        text=[f'{v:.0f}' for v in values],
        textposition='inside'
    ))

    fig.update_layout(
        title="Score Breakdown",
        xaxis_title="Score",
        yaxis_title="Category",
        font=dict(family="Inter, sans-serif"),
        showlegend=False
    )

    return fig

def create_timeline_chart(data: List[Dict], title: str = "Career Timeline"):
    """Create a timeline visualization for career progression."""
    if not data:
        return None

    dates = [item.get('date', '') for item in data]
    events = [item.get('event', '') for item in data]
    descriptions = [item.get('description', '') for item in data]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=list(range(len(dates))),
        mode='markers+lines+text',
        text=events,
        textposition='top center',
        marker=dict(size=10, color='#667eea'),
        line=dict(color='#667eea', width=2),
        hovertext=descriptions,
        hoverinfo='text'
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Timeline",
        yaxis=dict(showticklabels=False),
        font=dict(family="Inter, sans-serif")
    )

    return fig

def show_loading_spinner(message: str = "Processing..."):
    """Show a loading spinner with custom message."""
    return st.spinner(f"🔄 {message}")

def create_download_button(data: str, filename: str, label: str = "Download"):
    """Create a styled download button."""
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:text/plain;base64,{b64}" download="{filename}">{label}</a>'
    st.markdown(href, unsafe_allow_html=True)

def display_success_message(message: str):
    """Display a success message with animation."""
    create_alert(f"✅ {message}", "success")

def display_warning_message(message: str):
    """Display a warning message."""
    create_alert(f"⚠️ {message}", "warning")

def display_error_message(message: str):
    """Display an error message."""
    create_alert(f"❌ {message}", "error")

def display_info_message(message: str):
    """Display an info message."""
    create_alert(f"ℹ️ {message}", "info")

def create_sidebar_navigation():
    """Create enhanced sidebar navigation."""
    st.sidebar.title("🎯 Resume Analyzer Pro")
    st.sidebar.markdown("---")

    # Add navigation info
    nav_info = """
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1rem; border-radius: 8px; color: white; margin-bottom: 1rem;">
        <h4 style="margin: 0;">Navigation Guide</h4>
        <p style="margin: 0.5rem 0;">Use the pages above to access different features:</p>
        <ul style="margin: 0; padding-left: 1rem;">
            <li>📊 ATS Score Checker</li>
            <li>🎯 Job Matcher</li>
            <li>📈 Analytics Dashboard</li>
            <li>📝 Resume Builder</li>
            <li>💬 Feedback System</li>
        </ul>
    </div>
    """
    st.sidebar.markdown(nav_info, unsafe_allow_html=True)

    # Add current time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.sidebar.caption(f"Last updated: {current_time}")

def initialize_session_state():
    """Initialize session state variables for the application."""
    default_values = {
        'analyzed_resumes': [],
        'analysis_history': [],
        'current_resume_text': None,
        'current_resume_data': None,
        'user_feedback': [],
        'app_settings': {
            'theme': 'default',
            'ai_enabled': True,
            'advanced_features': True
        }
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

def clear_session_data():
    """Clear session data with user confirmation."""
    if st.button("🗑️ Clear All Data", type="secondary"):
        if st.checkbox("I confirm I want to clear all data"):
            for key in st.session_state.keys():
                if key.startswith(('analyzed_', 'current_', 'user_')):
                    del st.session_state[key]
            st.success("✅ All data cleared successfully!")
            st.rerun()
