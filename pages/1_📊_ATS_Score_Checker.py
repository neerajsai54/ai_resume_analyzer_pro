import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from ui_components import load_custom_css, create_alert, create_progress_bar
from resume_parser import resume_parser
from ats_checker import ats_checker
from scoring_system import scoring_system
from analytics import analytics_manager

# Configure page
st.set_page_config(
    page_title="ATS Score Checker - AI Resume Analyzer Pro",
    page_icon="📊",
    layout="wide"
)

# Load custom CSS
load_custom_css()

def main():
    """ATS Score Checker main function"""

    # Log page visit
    analytics_manager.log_usage("ATS Score Checker", "page_visit")

    # Header
    st.markdown("# 📊 **ATS Score Checker**")
    st.markdown("Get detailed ATS compatibility analysis with actionable recommendations")

    # Sidebar instructions
    with st.sidebar:
        st.markdown("### 📋 **How it works**")
        st.markdown("""
        1. **Upload** your resume (PDF, DOCX, or TXT)
        2. **Analyze** ATS compatibility automatically
        3. **Review** detailed score breakdown
        4. **Implement** recommended improvements
        """)

        st.markdown("### ✅ **What we check**")
        st.markdown("""
        - Format compatibility
        - Keyword optimization
        - Contact information
        - Section organization
        - Length optimization
        - Readability score
        """)

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        # File upload section
        st.markdown("## 📁 **Upload Your Resume**")

        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT (Max size: 10MB)"
        )

        if uploaded_file is not None:
            # Parse the resume
            with st.spinner("🔍 Parsing your resume..."):
                parsed_data = resume_parser.parse_file(uploaded_file)

            if "error" in parsed_data:
                st.error(f"❌ **Error parsing file:** {parsed_data['error']}")
                return

            # Display file info
            file_stats = resume_parser.get_file_stats(parsed_data)

            with col2:
                st.markdown("## 📈 **File Information**")
                st.info(f"""
                **File:** {file_stats.get('file_name', 'Unknown')}  
                **Type:** {file_stats.get('file_type', 'Unknown').upper()}  
                **Words:** {file_stats.get('word_count', 0):,}  
                **Characters:** {file_stats.get('character_count', 0):,}
                """)

            # Analyze ATS compatibility
            st.markdown("---")
            st.markdown("## 🎯 **ATS Compatibility Analysis**")

            with st.spinner("🤖 Analyzing ATS compatibility..."):
                # Check if user wants AI analysis
                use_ai = st.checkbox("Use AI-powered analysis", value=True, 
                                   help="Enhanced analysis using Google Gemini AI")

                ats_analysis = ats_checker.analyze_ats_compatibility(
                    parsed_data["raw_text"], use_ai=use_ai
                )

                # Log analysis
                analytics_manager.log_usage("ATS Checker", "analysis_completed")

            # Display overall score
            overall_score = ats_analysis.get("ats_score", 0)

            # Score display with color coding
            if overall_score >= 80:
                score_color = "success"
                score_emoji = "🟢"
            elif overall_score >= 60:
                score_color = "warning"
                score_emoji = "🟡"
            else:
                score_color = "error"
                score_emoji = "🔴"

            st.markdown(f"""
            <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #FF9A8B, #A8E6CF); border-radius: 1rem; margin: 1rem 0;">
                <h2 style="color: white; margin: 0;">ATS Compatibility Score</h2>
                <h1 style="color: white; font-size: 4rem; margin: 0.5rem 0;">{score_emoji} {overall_score}/100</h1>
                <p style="color: white; margin: 0; font-size: 1.2rem;">
                    {_get_score_description(overall_score)}
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Detailed category breakdown
            st.markdown("## 📋 **Detailed Category Analysis**")

            categories = ats_analysis.get("categories", {})

            if categories:
                for i, (category, data) in enumerate(categories.items()):
                    with st.expander(f"📊 {category.replace('_', ' ').title()}", expanded=(i < 2)):
                        col_score, col_feedback = st.columns([1, 2])

                        with col_score:
                            score = data.get("score", 0)
                            create_progress_bar(score, 100, f"Score: {score}/100")

                        with col_feedback:
                            feedback = data.get("feedback", "No feedback available")
                            st.markdown(f"**Feedback:** {feedback}")

            # Recommendations section
            recommendations = ats_analysis.get("recommendations", [])
            if recommendations:
                st.markdown("## 💡 **Improvement Recommendations**")

                for i, recommendation in enumerate(recommendations, 1):
                    st.markdown(f"**{i}.** {recommendation}")

            # Critical issues
            critical_issues = ats_analysis.get("critical_issues", [])
            if critical_issues:
                st.markdown("## ⚠️ **Critical Issues**")
                for issue in critical_issues:
                    create_alert(issue, "error", "❌")

            # Strengths
            strengths = ats_analysis.get("strengths", [])
            if strengths:
                st.markdown("## ✅ **Resume Strengths**")
                for strength in strengths:
                    create_alert(strength, "success", "✅")

            # Action buttons
            st.markdown("---")
            col_action1, col_action2, col_action3 = st.columns(3)

            with col_action1:
                if st.button("🔄 **Analyze Again**", use_container_width=True):
                    st.rerun()

            with col_action2:
                if st.button("🎯 **Check Job Match**", use_container_width=True):
                    st.switch_page("pages/2_🎯_Job_Matcher.py")

            with col_action3:
                if st.button("📈 **View Analytics**", use_container_width=True):
                    st.switch_page("pages/3_📈_Analytics_Dashboard.py")

            # Save analysis to database
            if st.button("💾 **Save Analysis**", use_container_width=True):
                analysis_data = {
                    "ats_analysis": ats_analysis,
                    "overall_score": overall_score,
                    "category_scores": {cat: data.get("score", 0) for cat, data in categories.items()}
                }

                if analytics_manager.save_analysis(analysis_data, file_stats):
                    st.success("✅ Analysis saved successfully!")
                    analytics_manager.log_usage("ATS Checker", "analysis_saved")
                else:
                    st.error("❌ Failed to save analysis")

        else:
            # Instructions when no file uploaded
            st.markdown("""
            ### 🚀 **Get Started**

            Upload your resume to receive:

            - ✅ **Comprehensive ATS score** (0-100)
            - 📊 **Category-wise breakdown** 
            - 💡 **Actionable recommendations**
            - ⚡ **Instant results** with AI analysis

            ### 📝 **Supported Formats**

            - **PDF** - Best for formatted resumes
            - **DOCX** - Microsoft Word documents  
            - **TXT** - Plain text files

            ### 🔒 **Privacy Notice**

            Your resume is processed securely and never stored permanently. 
            Analysis data is only saved if you explicitly choose to save it.
            """)

def _get_score_description(score: int) -> str:
    """Get description based on ATS score"""
    if score >= 90:
        return "Excellent ATS compatibility!"
    elif score >= 80:
        return "Very good ATS compatibility"
    elif score >= 70:
        return "Good ATS compatibility with room for improvement"
    elif score >= 60:
        return "Fair ATS compatibility - needs optimization"
    else:
        return "Poor ATS compatibility - requires significant improvement"

if __name__ == "__main__":
    main()
