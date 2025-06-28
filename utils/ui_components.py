import streamlit as st
import base64
from pathlib import Path

def load_custom_css():
    """Load custom CSS for modern UI styling"""
    css_content = """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Root Variables - 2024 Color Palette */
    :root {
        --primary-color: #FF9A8B;  /* Peach Fuzz 2024 */
        --secondary-color: #A8E6CF;  /* Soft Mint */
        --accent-color: #88D4F7;  /* Sky Blue */
        --text-primary: #2C3E50;
        --text-secondary: #7F8C8D;
        --background: #FDFEFE;
        --surface: #FFFFFF;
        --border: #E8F4FD;
        --shadow: rgba(44, 62, 80, 0.1);
        --gradient-1: linear-gradient(135deg, #FF9A8B 0%, #FFEAA7 100%);
        --gradient-2: linear-gradient(135deg, #A8E6CF 0%, #88D4F7 100%);
    }

    /* Global Styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display: none;}
    footer {visibility: hidden;}
    .stApp > header {background: transparent;}

    /* Custom Header */
    .hero-section {
        background: var(--gradient-1);
        padding: 3rem 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px var(--shadow);
    }

    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #FFFFFF, #F8F9FA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-subtitle {
        font-size: 1.3rem;
        font-weight: 400;
        opacity: 0.9;
        max-width: 600px;
        margin: 0 auto;
    }

    /* Feature Cards */
    .feature-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 1rem;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px var(--shadow);
        text-align: center;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }

    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: var(--gradient-2);
        transition: all 0.5s ease;
        z-index: -1;
        opacity: 0;
    }

    .feature-card:hover::before {
        left: 0;
        opacity: 0.1;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 32px var(--shadow);
        border-color: var(--primary-color);
    }

    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }

    .feature-card h3 {
        color: var(--text-primary);
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }

    .feature-card p {
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 0;
    }

    /* Enhanced Buttons */
    .stButton > button {
        background: var(--gradient-1);
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(255, 154, 139, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(255, 154, 139, 0.4);
    }

    .stButton > button:focus {
        outline: 3px solid rgba(255, 154, 139, 0.3);
        outline-offset: 2px;
    }

    /* File Uploader */
    .stFileUploader > div > div {
        border: 2px dashed var(--primary-color);
        border-radius: 1rem;
        padding: 2rem;
        background: linear-gradient(135deg, rgba(255, 154, 139, 0.05), rgba(168, 230, 207, 0.05));
        transition: all 0.3s ease;
    }

    .stFileUploader > div > div:hover {
        border-color: var(--accent-color);
        background: linear-gradient(135deg, rgba(255, 154, 139, 0.1), rgba(168, 230, 207, 0.1));
    }

    /* Metrics */
    .metric-container {
        background: var(--surface);
        border-radius: 1rem;
        padding: 1.5rem;
        border: 1px solid var(--border);
        box-shadow: 0 4px 16px var(--shadow);
        transition: all 0.3s ease;
    }

    .metric-container:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px var(--shadow);
    }

    /* Sidebar */
    .css-1d391kg {
        background: var(--gradient-2);
    }

    .css-1d391kg .stSelectbox > div > div {
        background: var(--surface);
        border-radius: 0.5rem;
    }

    /* Progress Bars */
    .stProgress > div > div > div {
        background: var(--gradient-1);
        border-radius: 1rem;
    }

    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(168, 230, 207, 0.1), rgba(136, 212, 247, 0.1));
        border-left: 4px solid var(--secondary-color);
        border-radius: 0.5rem;
    }

    .stError {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(255, 154, 139, 0.1));
        border-left: 4px solid #FF6B6B;
        border-radius: 0.5rem;
    }

    .stWarning {
        background: linear-gradient(135deg, rgba(255, 234, 167, 0.1), rgba(255, 154, 139, 0.1));
        border-left: 4px solid #FFEAA7;
        border-radius: 0.5rem;
    }

    /* Footer */
    .footer {
        background: var(--surface);
        border-top: 1px solid var(--border);
        padding: 2rem;
        text-align: center;
        margin-top: 3rem;
        border-radius: 1rem 1rem 0 0;
    }

    .footer p {
        color: var(--text-secondary);
        margin: 0;
    }

    .footer a {
        color: var(--primary-color);
        text-decoration: none;
        font-weight: 500;
    }

    .footer a:hover {
        text-decoration: underline;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }

        .hero-subtitle {
            font-size: 1.1rem;
        }

        .feature-card {
            padding: 1.5rem;
        }

        .feature-icon {
            font-size: 2.5rem;
        }
    }

    /* Loading Animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    .loading {
        animation: pulse 2s infinite;
    }

    /* Focus Indicators for Accessibility */
    *:focus {
        outline: 2px solid var(--primary-color);
        outline-offset: 2px;
    }

    /* High Contrast Mode Support */
    @media (prefers-contrast: high) {
        :root {
            --primary-color: #D63384;
            --secondary-color: #198754;
            --text-primary: #000000;
            --text-secondary: #212529;
        }
    }

    /* Reduced Motion Support */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """

    st.markdown(css_content, unsafe_allow_html=True)

def create_hero_section():
    """Create the hero section with modern design"""
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🎯 AI Resume Analyzer Pro</h1>
        <p class="hero-subtitle">
            Transform your career with AI-powered resume optimization, 
            ATS compatibility checking, and personalized job matching
        </p>
    </div>
    """, unsafe_allow_html=True)

def create_feature_card(icon, title, description, link=None):
    """Create a feature card with modern styling"""
    card_html = f"""
    <div class="feature-card" {'onclick="window.location.href=\'{link}\'"' if link else ''}>
        <div class="feature-icon">{icon}</div>
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def create_metric_card(title, value, delta=None, icon="📊"):
    """Create a metric card with enhanced styling"""
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ''

    card_html = f"""
    <div class="metric-container">
        <div class="metric-icon">{icon}</div>
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def create_progress_bar(value, max_value=100, label="Progress", color="primary"):
    """Create an enhanced progress bar"""
    percentage = (value / max_value) * 100

    progress_html = f"""
    <div class="progress-container">
        <div class="progress-label">{label}</div>
        <div class="progress-bar">
            <div class="progress-fill progress-{color}" style="width: {percentage}%"></div>
        </div>
        <div class="progress-text">{value}/{max_value} ({percentage:.1f}%)</div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)

def create_alert(message, alert_type="info", icon="ℹ️"):
    """Create a modern alert component"""
    alert_html = f"""
    <div class="alert alert-{alert_type}">
        <div class="alert-icon">{icon}</div>
        <div class="alert-content">{message}</div>
    </div>
    """
    st.markdown(alert_html, unsafe_allow_html=True)

def create_sidebar_navigation():
    """Create enhanced sidebar navigation"""
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <h2>🎯 Navigation</h2>
    </div>
    """, unsafe_allow_html=True)

    pages = [
        ("🏠", "Home", "/"),
        ("📊", "ATS Checker", "/1_📊_ATS_Score_Checker"),
        ("🎯", "Job Matcher", "/2_🎯_Job_Matcher"),
        ("📈", "Analytics", "/3_📈_Analytics_Dashboard"),
        ("📝", "Resume Builder", "/4_📝_Resume_Builder"),
        ("💬", "Feedback", "/5_💬_Feedback_System")
    ]

    for icon, name, url in pages:
        if st.sidebar.button(f"{icon} {name}", key=f"nav_{name.lower()}", use_container_width=True):
            st.switch_page(url if url != "/" else "app.py")

def get_icon(name):
    """Get icon for consistent usage throughout the app"""
    icons = {
        "upload": "📁",
        "analyze": "🔍",
        "score": "📊",
        "match": "🎯",
        "build": "📝",
        "download": "⬇️",
        "share": "📤",
        "settings": "⚙️",
        "help": "❓",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️"
    }
    return icons.get(name, "📌")

def apply_theme(theme_name="modern"):
    """Apply different theme variations"""
    themes = {
        "modern": {
            "primary": "#FF9A8B",
            "secondary": "#A8E6CF",
            "accent": "#88D4F7"
        },
        "professional": {
            "primary": "#2C3E50",
            "secondary": "#3498DB",
            "accent": "#E74C3C"
        },
        "creative": {
            "primary": "#9B59B6",
            "secondary": "#F39C12",
            "accent": "#1ABC9C"
        }
    }

    if theme_name in themes:
        theme = themes[theme_name]
        st.session_state['current_theme'] = theme
        return theme
    return themes["modern"]
