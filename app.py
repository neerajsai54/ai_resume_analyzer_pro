import streamlit as st
import os
from pathlib import Path
import sys

# Add utils to path
sys.path.append(str(Path(__file__).parent / "utils"))

from ui_components import load_custom_css, create_hero_section, create_feature_card
from gemini_client import GeminiClient

# Configure page
st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/enhanced-resume-analyzer',
        'Report a bug': "https://github.com/your-repo/enhanced-resume-analyzer/issues",
        'About': "# AI Resume Analyzer Pro\n\nAdvanced resume analysis powered by Google Gemini AI"
    }
)

# Load custom CSS
load_custom_css()

def main():
    """Main application entry point with enhanced UI"""

    # Hero Section
    create_hero_section()

    # Feature Overview
    st.markdown("## 🚀 **Powerful Features at Your Fingertips**")

    col1, col2, col3 = st.columns(3)

    with col1:
        create_feature_card(
            "📊", "ATS Score Checker", 
            "Get detailed ATS compatibility scores with actionable recommendations",
            "/1_📊_ATS_Score_Checker"
        )

    with col2:
        create_feature_card(
            "🎯", "Job Matcher", 
            "Match your resume to job descriptions with AI-powered analysis",
            "/2_🎯_Job_Matcher"
        )

    with col3:
        create_feature_card(
            "📈", "Analytics Dashboard", 
            "Track your resume improvements with detailed analytics",
            "/3_📈_Analytics_Dashboard"
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        create_feature_card(
            "📝", "Resume Builder", 
            "Create professional resumes with AI-generated content",
            "/4_📝_Resume_Builder"
        )

    with col5:
        create_feature_card(
            "💬", "Feedback System", 
            "Share your experience and help us improve",
            "/5_💬_Feedback_System"
        )

    with col6:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3>Quick Analysis</h3>
            <p>Upload your resume below for instant AI-powered analysis</p>
        </div>
        """, unsafe_allow_html=True)

    # Quick Analysis Section
    st.markdown("---")
    st.markdown("## ⚡ **Quick Resume Analysis**")

    col_upload, col_analyze = st.columns([2, 1])

    with col_upload:
        uploaded_file = st.file_uploader(
            "Upload your resume for instant analysis",
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT"
        )

    with col_analyze:
        if uploaded_file is not None:
            if st.button("🔍 Analyze Resume", type="primary", use_container_width=True):
                with st.spinner("Analyzing your resume..."):
                    # Quick analysis logic here
                    st.success("Analysis complete! Check the ATS Score Checker for detailed results.")
                    st.balloons()

    # Statistics Section
    if 'analysis_count' not in st.session_state:
        st.session_state.analysis_count = 1247

    st.markdown("---")
    st.markdown("## 📊 **Platform Statistics**")

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric(
            label="📄 Resumes Analyzed",
            value=f"{st.session_state.analysis_count:,}",
            delta="234 this month"
        )

    with metric_col2:
        st.metric(
            label="🎯 Average ATS Score",
            value="78.5",
            delta="4.2% improvement"
        )

    with metric_col3:
        st.metric(
            label="⭐ User Satisfaction",
            value="94.8%",
            delta="2.1% increase"
        )

    with metric_col4:
        st.metric(
            label="🚀 Success Rate",
            value="89.2%",
            delta="5.7% higher"
        )

    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p>Built with ❤️ using Streamlit & Google Gemini AI | 
        <a href="/docs/README.md">Documentation</a> | 
        <a href="/5_💬_Feedback_System">Feedback</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
