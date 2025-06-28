import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from ui_components import load_custom_css, create_alert, create_progress_bar
from resume_parser import resume_parser
from job_matcher import job_matcher
from analytics import analytics_manager

# Configure page
st.set_page_config(
    page_title="Job Matcher - AI Resume Analyzer Pro",
    page_icon="🎯",
    layout="wide"
)

# Load custom CSS
load_custom_css()

def main():
    """Job Matcher main function"""

    # Log page visit
    analytics_manager.log_usage("Job Matcher", "page_visit")

    # Header
    st.markdown("# 🎯 **Job Matcher**")
    st.markdown("Match your resume to job descriptions with AI-powered semantic analysis")

    # Sidebar instructions
    with st.sidebar:
        st.markdown("### 📋 **How it works**")
        st.markdown("""
        1. **Upload** your resume
        2. **Paste** job description
        3. **Analyze** compatibility match
        4. **Review** gaps and recommendations
        """)

        st.markdown("### 🔍 **What we analyze**")
        st.markdown("""
        - Keyword matches
        - Skill compatibility
        - Experience alignment
        - Industry knowledge
        - Missing requirements
        """)

        st.markdown("### 💡 **Pro Tips**")
        st.markdown("""
        - Copy full job description
        - Include requirements section
        - Check multiple job postings
        - Use insights to tailor resume
        """)

    # Main content
    # Step 1: Resume upload
    st.markdown("## 📁 **Step 1: Upload Your Resume**")

    uploaded_file = st.file_uploader(
        "Choose your resume file",
        type=['pdf', 'docx', 'txt'],
        help="Upload your current resume to match against job descriptions"
    )

    resume_text = ""
    if uploaded_file is not None:
        with st.spinner("📄 Parsing your resume..."):
            parsed_data = resume_parser.parse_file(uploaded_file)

        if "error" in parsed_data:
            st.error(f"❌ **Error parsing file:** {parsed_data['error']}")
            return

        resume_text = parsed_data["raw_text"]
        file_stats = resume_parser.get_file_stats(parsed_data)

        st.success(f"✅ Resume uploaded successfully! ({file_stats.get('word_count', 0)} words)")

    # Step 2: Job description input
    st.markdown("---")
    st.markdown("## 📝 **Step 2: Enter Job Description**")

    col1, col2 = st.columns([3, 1])

    with col1:
        job_description = st.text_area(
            "Paste the complete job description here",
            height=300,
            placeholder="""Job Title: Software Engineer

Company: Tech Company Inc.

Requirements:
- Bachelor's degree in Computer Science
- 3+ years of Python development experience
- Experience with React and JavaScript
- Knowledge of AWS cloud services
- Strong problem-solving skills

Responsibilities:
- Develop and maintain web applications
- Collaborate with cross-functional teams
- Write clean, efficient code
- Participate in code reviews

Preferred Qualifications:
- Master's degree preferred
- Experience with Docker and Kubernetes
- Familiarity with machine learning concepts"""
        )

    with col2:
        st.markdown("### 📊 **Job Info**")
        if job_description:
            job_word_count = len(job_description.split())
            st.info(f"""
            **Words:** {job_word_count:,}  
            **Characters:** {len(job_description):,}  
            **Status:** {"✅ Ready" if job_word_count > 50 else "⚠️ Too short"}
            """)
        else:
            st.info("Waiting for job description...")

    # Step 3: Analysis
    if resume_text and job_description and len(job_description.split()) > 20:
        st.markdown("---")
        st.markdown("## 🤖 **Step 3: AI-Powered Analysis**")

        # Analysis options
        col_ai, col_analyze = st.columns([2, 1])

        with col_ai:
            use_ai = st.checkbox(
                "Use AI-powered semantic analysis", 
                value=True,
                help="Enhanced analysis using Google Gemini AI for better accuracy"
            )

        with col_analyze:
            if st.button("🎯 **Analyze Match**", type="primary", use_container_width=True):

                with st.spinner("🔍 Analyzing job compatibility..."):
                    # Perform job matching analysis
                    match_analysis = job_matcher.match_resume_to_job(
                        resume_text, job_description, use_ai=use_ai
                    )

                    # Log analysis
                    analytics_manager.log_usage("Job Matcher", "analysis_completed")

                # Display results
                _display_match_results(match_analysis, job_description)

    elif uploaded_file is not None and not job_description:
        create_alert("Please enter a job description to continue with the analysis", "warning", "⚠️")

    elif job_description and not uploaded_file:
        create_alert("Please upload your resume to continue with the analysis", "warning", "⚠️")

    else:
        # Instructions when nothing uploaded
        st.markdown("""
        ### 🚀 **Get Started with Job Matching**

        Our AI-powered job matcher helps you:

        - 📊 **Calculate compatibility score** (0-100%)
        - 🔍 **Identify keyword matches** and gaps
        - 💪 **Highlight your strengths** for the role
        - 🎯 **Get specific recommendations** for improvement
        - 📈 **Track different compatibility areas**

        ### 🎯 **Best Practices**

        1. **Use complete job descriptions** including requirements and responsibilities
        2. **Copy from official job postings** for accurate analysis
        3. **Compare multiple similar roles** to identify patterns
        4. **Focus on high-priority missing skills** from recommendations
        5. **Update your resume** based on insights and re-analyze
        """)

def _display_match_results(analysis: dict, job_description: str):
    """Display comprehensive job matching results"""

    # Overall match score
    match_score = analysis.get("match_score", 0)

    # Score display with visual indicator
    if match_score >= 80:
        score_color = "#2ECC71"  # Green
        score_emoji = "🟢"
        score_message = "Excellent match!"
    elif match_score >= 60:
        score_color = "#F39C12"  # Orange
        score_emoji = "🟡"
        score_message = "Good match with improvements needed"
    else:
        score_color = "#E74C3C"  # Red
        score_emoji = "🔴"
        score_message = "Needs significant improvement"

    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, {score_color}22, {score_color}11); border-radius: 1rem; margin: 1rem 0; border: 2px solid {score_color};">
        <h2 style="color: {score_color}; margin: 0;">Job Compatibility Score</h2>
        <h1 style="color: {score_color}; font-size: 4rem; margin: 0.5rem 0;">{score_emoji} {match_score}%</h1>
        <p style="color: {score_color}; margin: 0; font-size: 1.2rem; font-weight: 600;">
            {score_message}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Detailed analysis sections
    col1, col2 = st.columns(2)

    with col1:
        # Keyword matches
        st.markdown("### 🔑 **Keyword Analysis**")
        keyword_matches = analysis.get("keyword_matches", [])

        if keyword_matches:
            for keyword_data in keyword_matches[:10]:  # Show top 10
                keyword = keyword_data.get("keyword", "")
                found = keyword_data.get("found", False)
                importance = keyword_data.get("importance", "low")

                # Color coding based on importance and found status
                if found:
                    if importance == "high":
                        badge_color = "#2ECC71"  # Green
                        icon = "✅"
                    elif importance == "medium":
                        badge_color = "#3498DB"  # Blue
                        icon = "✅"
                    else:
                        badge_color = "#95A5A6"  # Gray
                        icon = "✅"
                else:
                    if importance == "high":
                        badge_color = "#E74C3C"  # Red
                        icon = "❌"
                    elif importance == "medium":
                        badge_color = "#F39C12"  # Orange
                        icon = "⚠️"
                    else:
                        badge_color = "#BDC3C7"  # Light Gray
                        icon = "➖"

                st.markdown(f"""
                <div style="display: inline-block; background: {badge_color}22; border: 1px solid {badge_color}; 
                            border-radius: 15px; padding: 5px 12px; margin: 2px; font-size: 0.9em;">
                    {icon} <strong>{keyword}</strong> <em>({importance})</em>
                </div>
                """, unsafe_allow_html=True)

        # Strengths
        strengths = analysis.get("strengths", [])
        if strengths:
            st.markdown("### 💪 **Your Strengths**")
            for strength in strengths:
                create_alert(strength, "success", "✅")

    with col2:
        # Skill gaps
        st.markdown("### 🎯 **Skill Gaps to Address**")
        skill_gaps = analysis.get("skill_gaps", [])

        if skill_gaps:
            for gap in skill_gaps:
                create_alert(f"Consider developing: **{gap}**", "warning", "📈")
        else:
            st.success("🎉 No major skill gaps identified!")

        # Compatibility areas
        st.markdown("### 📊 **Compatibility Breakdown**")
        compatibility_areas = analysis.get("compatibility_areas", {})

        for area, score in compatibility_areas.items():
            area_name = area.replace("_", " ").title()
            create_progress_bar(score, 100, f"{area_name}: {score}%")

    # Recommendations
    st.markdown("---")
    st.markdown("### 💡 **Personalized Recommendations**")

    recommendations = analysis.get("recommendations", [])
    if recommendations:
        for i, recommendation in enumerate(recommendations, 1):
            st.markdown(f"**{i}.** {recommendation}")
    else:
        st.info("Great job! No major recommendations at this time.")

    # Action buttons
    st.markdown("---")
    col_action1, col_action2, col_action3, col_action4 = st.columns(4)

    with col_action1:
        if st.button("🔄 **Analyze Another Job**", use_container_width=True):
            st.rerun()

    with col_action2:
        if st.button("📊 **Check ATS Score**", use_container_width=True):
            st.switch_page("pages/1_📊_ATS_Score_Checker.py")

    with col_action3:
        if st.button("📝 **Build Resume**", use_container_width=True):
            st.switch_page("pages/4_📝_Resume_Builder.py")

    with col_action4:
        if st.button("📈 **View Analytics**", use_container_width=True):
            st.switch_page("pages/3_📈_Analytics_Dashboard.py")

    # Save analysis option
    if st.button("💾 **Save Match Analysis**", use_container_width=True):
        analysis_data = {
            "job_match_analysis": analysis,
            "match_score": match_score,
            "job_description_length": len(job_description.split())
        }

        file_info = {"file_name": "job_match_analysis", "file_type": "analysis"}

        if analytics_manager.save_analysis(analysis_data, file_info):
            st.success("✅ Match analysis saved successfully!")
            analytics_manager.log_usage("Job Matcher", "analysis_saved")
        else:
            st.error("❌ Failed to save analysis")

if __name__ == "__main__":
    main()
