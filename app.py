"""
Enhanced Resume Analyzer Pro - Main Application
A comprehensive AI-powered resume analysis platform built with Streamlit.
"""

import streamlit as st
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.ui_components import (
    load_custom_css, create_feature_card, create_alert,
    initialize_session_state, create_sidebar_navigation
)
from utils.gemini_client import get_gemini_client
from utils.resume_parser import parse_uploaded_resume

# Page configuration
st.set_page_config(
    page_title="Resume Analyzer Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function."""

    # Load custom CSS and initialize session state
    load_custom_css()
    initialize_session_state()

    # Create sidebar navigation
    create_sidebar_navigation()

    # Main page content
    st.title("🎯 AI-Powered Resume Analyzer Pro")
    st.markdown("### Transform your resume with intelligent analysis and optimization")

    # Check AI availability
    gemini_client = get_gemini_client()
    if not gemini_client.is_available():
        create_alert(
            "⚠️ AI features are currently unavailable. Please configure your Google API key in Streamlit secrets to enable full functionality.",
            "warning"
        )
        st.info("💡 You can still use basic resume parsing and analysis features.")

    # Hero section with feature overview
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        create_feature_card(
            "📊 ATS Score Checker",
            "Get comprehensive ATS compatibility scores with detailed recommendations for improvement.",
            "📊"
        )

    with col2:
        create_feature_card(
            "🎯 Job Matcher", 
            "Match your resume against job descriptions and identify skill gaps with precision.",
            "🎯"
        )

    with col3:
        create_feature_card(
            "📈 Analytics Dashboard",
            "Track your resume improvement over time with detailed analytics and insights.",
            "📈"
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        create_feature_card(
            "📝 Resume Builder",
            "Create professional resumes using AI-powered templates and optimization.",
            "📝"
        )

    with col5:
        create_feature_card(
            "💬 Feedback System",
            "Provide feedback to help us improve the platform and your experience.",
            "💬"
        )

    with col6:
        create_feature_card(
            "🚀 Quick Analysis",
            "Upload your resume below for instant analysis and get started immediately.",
            "🚀"
        )

    # Quick Analysis Section
    st.markdown("---")
    st.header("🚀 Quick Resume Analysis")
    st.markdown("Upload your resume to get started with instant analysis")

    # File upload
    uploaded_file = st.file_uploader(
        "Choose your resume file",
        type=['pdf', 'docx', 'txt'],
        help="Supported formats: PDF, DOCX, TXT (Max size: 10MB)"
    )

    if uploaded_file is not None:
        # Parse the resume
        with st.spinner("📄 Processing your resume..."):
            text_content, metadata, basic_info = parse_uploaded_resume(uploaded_file)

        if text_content:
            # Store in session state
            st.session_state['current_resume_text'] = text_content
            st.session_state['current_resume_metadata'] = metadata
            st.session_state['current_resume_basic_info'] = basic_info

            # Display success message
            create_alert("✅ Resume processed successfully! You can now use all analysis features.", "success")

            # Show basic information
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📄 File Information")
                if metadata:
                    st.write(f"**Filename:** {metadata['filename']}")
                    st.write(f"**File Size:** {metadata['file_size']:,} bytes")
                    st.write(f"**File Type:** {metadata['file_type'].upper()}")
                    st.write(f"**Word Count:** {metadata.get('word_count', 'N/A'):,}")

            with col2:
                st.subheader("👤 Detected Information")
                if basic_info:
                    if basic_info['emails']:
                        st.write(f"**Email:** {basic_info['emails'][0]}")
                    if basic_info['phones']:
                        st.write(f"**Phone:** {basic_info['phones'][0]}")
                    if basic_info['name_candidates']:
                        st.write(f"**Possible Name:** {basic_info['name_candidates'][0]}")
                    if basic_info['urls']:
                        st.write(f"**URLs Found:** {len(basic_info['urls'])}")

            # Preview text content
            with st.expander("📖 Preview Resume Content"):
                preview_text = text_content[:1000] + "..." if len(text_content) > 1000 else text_content
                st.text_area("Resume Content Preview", preview_text, height=200, disabled=True)

            # Quick AI Analysis (if available)
            if gemini_client.is_available():
                st.markdown("---")
                st.subheader("🤖 Quick AI Analysis")

                if st.button("🔍 Analyze with AI", type="primary"):
                    with st.spinner("🤖 AI is analyzing your resume..."):
                        analysis_result = gemini_client.analyze_resume(text_content)

                    if analysis_result:
                        st.success("✅ AI analysis completed!")

                        # Store analysis result
                        st.session_state['current_resume_data'] = analysis_result

                        # Display key insights
                        col1, col2 = st.columns(2)

                        with col1:
                            if analysis_result.get('skills'):
                                st.write("**🔧 Skills Found:**")
                                skills_text = ", ".join(analysis_result['skills'][:10])
                                if len(analysis_result['skills']) > 10:
                                    skills_text += f" (+{len(analysis_result['skills']) - 10} more)"
                                st.write(skills_text)

                            if analysis_result.get('experience'):
                                st.write(f"**💼 Experience Entries:** {len(analysis_result['experience'])}")

                        with col2:
                            if analysis_result.get('education'):
                                st.write(f"**🎓 Education Entries:** {len(analysis_result['education'])}")

                            if analysis_result.get('certifications'):
                                st.write(f"**📜 Certifications:** {len(analysis_result['certifications'])}")

                        # Show navigation options
                        st.markdown("---")
                        st.subheader("🧭 Next Steps")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            if st.button("📊 Get ATS Score", type="secondary"):
                                st.switch_page("pages/1_📊_ATS_Score_Checker.py")

                        with col2:
                            if st.button("🎯 Match Jobs", type="secondary"):
                                st.switch_page("pages/2_🎯_Job_Matcher.py")

                        with col3:
                            if st.button("📈 View Analytics", type="secondary"):
                                st.switch_page("pages/3_📈_Analytics_Dashboard.py")

            else:
                st.info("🤖 AI analysis unavailable. Please configure Google API key for full features.")

                # Show basic navigation options
                st.markdown("---")
                st.subheader("🧭 Available Features")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("📊 Basic ATS Check", type="secondary"):
                        st.switch_page("pages/1_📊_ATS_Score_Checker.py")

                with col2:
                    if st.button("📈 View Analytics", type="secondary"):
                        st.switch_page("pages/3_📈_Analytics_Dashboard.py")

    else:
        # Show getting started information
        st.markdown("---")
        st.subheader("🚀 Getting Started")

        getting_started_info = """
        ### How to Use Resume Analyzer Pro

        1. **Upload Your Resume** 📄
           - Supported formats: PDF, DOCX, TXT
           - Maximum file size: 10MB
           - Ensure your resume is clearly formatted

        2. **Get Instant Analysis** ⚡
           - Basic information extraction
           - Text parsing and validation
           - File metadata analysis

        3. **AI-Powered Insights** 🤖
           - Detailed resume structure analysis
           - Skills and experience extraction
           - Professional recommendations

        4. **Advanced Features** 🎯
           - ATS compatibility scoring
           - Job description matching
           - Resume improvement suggestions
           - Performance analytics

        5. **Track Progress** 📈
           - Monitor improvement over time
           - Compare different versions
           - Export analysis results
        """

        st.markdown(getting_started_info)

    # Footer
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns(3)

    with footer_col1:
        st.caption("🎯 **Resume Analyzer Pro**")
        st.caption("AI-powered career optimization")

    with footer_col2:
        st.caption("🔧 **Features**")
        st.caption("ATS scoring, job matching, analytics")

    with footer_col3:
        st.caption("🚀 **Get Started**")
        st.caption("Upload your resume above")

if __name__ == "__main__":
    main()
