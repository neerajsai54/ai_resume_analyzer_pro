"""
ATS Score Checker Page
Comprehensive ATS compatibility analysis with detailed scoring and recommendations.
"""

import streamlit as st
import sys
import os
import json
from typing import Dict, Any, List

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.ui_components import (
    load_custom_css, create_score_badge, create_alert,
    create_progress_bar, create_recommendation_list, create_metric_card
)
from utils.gemini_client import get_gemini_client
from utils.resume_parser import parse_uploaded_resume

# Page configuration
st.set_page_config(
    page_title="ATS Score Checker",
    page_icon="📊",
    layout="wide"
)

class ATSChecker:
    """ATS compatibility checker with rule-based and AI-powered analysis."""

    def __init__(self):
        self.scoring_weights = {
            'format_compatibility': 20,
            'content_structure': 25,
            'keyword_optimization': 20,
            'readability': 15,
            'contact_information': 10,
            'professional_sections': 10
        }

    def analyze_format_compatibility(self, text: str, metadata: Dict) -> Dict[str, Any]:
        """Analyze format compatibility for ATS systems."""
        score = 100
        issues = []
        recommendations = []

        # Check text extraction quality
        if not text or len(text.strip()) < 100:
            score -= 30
            issues.append("Poor text extraction - file may have formatting issues")
            recommendations.append("Convert to a text-based PDF or DOCX format")

        # Check file type
        file_type = metadata.get('file_type', '').lower()
        if file_type not in ['pdf', 'docx']:
            score -= 20
            issues.append(f"File format ({file_type}) may not be ATS-friendly")
            recommendations.append("Use PDF or DOCX format for better ATS compatibility")

        # Check for special characters
        special_chars = len([c for c in text if ord(c) > 127])
        if special_chars > len(text) * 0.05:  # More than 5% special characters
            score -= 15
            issues.append("High number of special characters detected")
            recommendations.append("Remove or replace special characters and symbols")

        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': recommendations
        }

    def analyze_content_structure(self, text: str) -> Dict[str, Any]:
        """Analyze content structure and organization."""
        score = 100
        issues = []
        recommendations = []

        # Check for standard resume sections
        required_sections = [
            ('contact', ['email', 'phone', 'address']),
            ('experience', ['experience', 'work', 'employment', 'professional']),
            ('education', ['education', 'degree', 'university', 'college']),
            ('skills', ['skills', 'technical', 'competencies'])
        ]

        text_lower = text.lower()
        missing_sections = []

        for section_name, keywords in required_sections:
            found = any(keyword in text_lower for keyword in keywords)
            if not found:
                missing_sections.append(section_name)
                score -= 15
                issues.append(f"Missing {section_name} section")
                recommendations.append(f"Add a clear {section_name.title()} section")

        # Check text length
        word_count = len(text.split())
        if word_count < 200:
            score -= 20
            issues.append("Resume content too brief")
            recommendations.append("Expand resume content to 300-800 words")
        elif word_count > 1000:
            score -= 10
            issues.append("Resume content too lengthy")
            recommendations.append("Condense content to focus on most relevant information")

        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': recommendations,
            'missing_sections': missing_sections
        }

    def analyze_keyword_optimization(self, text: str, job_description: str = "") -> Dict[str, Any]:
        """Analyze keyword optimization and density."""
        score = 100
        issues = []
        recommendations = []
        keywords_found = []

        # Common professional keywords
        professional_keywords = [
            'managed', 'developed', 'created', 'implemented', 'improved',
            'increased', 'reduced', 'achieved', 'delivered', 'coordinated',
            'led', 'supervised', 'analyzed', 'designed', 'optimized'
        ]

        text_lower = text.lower()
        found_keywords = [kw for kw in professional_keywords if kw in text_lower]
        keywords_found.extend(found_keywords)

        if len(found_keywords) < 5:
            score -= 25
            issues.append("Insufficient action verbs and professional keywords")
            recommendations.append("Include more action verbs and industry-specific keywords")

        # Check for quantified achievements
        import re
        numbers = re.findall(r'\b\d+%|\$\d+|\d+\+|\d+ years?|\d+ months?', text)
        if len(numbers) < 3:
            score -= 20
            issues.append("Few quantified achievements found")
            recommendations.append("Add specific numbers, percentages, and metrics to achievements")

        # Job description matching (if provided)
        if job_description:
            jd_words = set(job_description.lower().split())
            resume_words = set(text_lower.split())
            common_words = jd_words.intersection(resume_words)
            match_ratio = len(common_words) / len(jd_words) if jd_words else 0

            if match_ratio < 0.3:
                score -= 15
                issues.append("Low keyword match with job description")
                recommendations.append("Tailor resume keywords to match job requirements")

        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': recommendations,
            'keywords_found': keywords_found[:10]  # Return top 10
        }

    def analyze_readability(self, text: str) -> Dict[str, Any]:
        """Analyze text readability and formatting."""
        score = 100
        issues = []
        recommendations = []

        # Check sentence length
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

        if avg_sentence_length > 25:
            score -= 15
            issues.append("Sentences too long for ATS parsing")
            recommendations.append("Use shorter, clearer sentences (15-20 words)")

        # Check for bullet points or structured formatting
        bullet_indicators = ['•', '★', '-', '*', '◦']
        has_bullets = any(indicator in text for indicator in bullet_indicators)

        if not has_bullets:
            score -= 10
            issues.append("No bullet points detected")
            recommendations.append("Use bullet points to structure information clearly")

        # Check for excessive capitalization
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        if caps_ratio > 0.15:
            score -= 15
            issues.append("Excessive use of capital letters")
            recommendations.append("Use proper capitalization (title case for headers)")

        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': recommendations
        }

    def analyze_contact_information(self, basic_info: Dict) -> Dict[str, Any]:
        """Analyze contact information completeness."""
        score = 100
        issues = []
        recommendations = []

        if not basic_info.get('emails'):
            score -= 40
            issues.append("No email address found")
            recommendations.append("Include a professional email address")

        if not basic_info.get('phones'):
            score -= 30
            issues.append("No phone number found")
            recommendations.append("Include a valid phone number")

        if not basic_info.get('name_candidates'):
            score -= 30
            issues.append("Name not clearly identified")
            recommendations.append("Ensure your full name is prominently displayed")

        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': recommendations
        }

    def calculate_overall_score(self, component_scores: Dict[str, int]) -> int:
        """Calculate weighted overall ATS score."""
        total_score = 0
        total_weight = 0

        for component, score in component_scores.items():
            weight = self.scoring_weights.get(component, 10)
            total_score += score * weight
            total_weight += weight

        return int(total_score / total_weight) if total_weight > 0 else 0

def main():
    """Main function for ATS Score Checker page."""

    # Load custom CSS
    load_custom_css()

    st.title("📊 ATS Score Checker")
    st.markdown("### Comprehensive ATS compatibility analysis with detailed recommendations")

    # Check if resume data exists in session state
    if 'current_resume_text' not in st.session_state:
        create_alert(
            "No resume data found. Please upload a resume on the main page first.",
            "warning"
        )

        if st.button("🏠 Go to Main Page"):
            st.switch_page("app.py")

        return

    # Get resume data from session state
    resume_text = st.session_state['current_resume_text']
    metadata = st.session_state.get('current_resume_metadata', {})
    basic_info = st.session_state.get('current_resume_basic_info', {})

    # Initialize ATS checker
    ats_checker = ATSChecker()

    st.markdown("---")

    # Job description input (optional)
    st.subheader("🎯 Job Description (Optional)")
    job_description = st.text_area(
        "Paste the job description here to get targeted ATS analysis:",
        height=150,
        placeholder="Paste job description here for more accurate keyword matching..."
    )

    # Analysis button
    if st.button("🔍 Analyze ATS Compatibility", type="primary"):

        with st.spinner("📊 Analyzing ATS compatibility..."):

            # Perform all analyses
            format_analysis = ats_checker.analyze_format_compatibility(resume_text, metadata)
            structure_analysis = ats_checker.analyze_content_structure(resume_text)
            keyword_analysis = ats_checker.analyze_keyword_optimization(resume_text, job_description)
            readability_analysis = ats_checker.analyze_readability(resume_text)
            contact_analysis = ats_checker.analyze_contact_information(basic_info)

            # Calculate component scores
            component_scores = {
                'format_compatibility': format_analysis['score'],
                'content_structure': structure_analysis['score'],
                'keyword_optimization': keyword_analysis['score'],
                'readability': readability_analysis['score'],
                'contact_information': contact_analysis['score']
            }

            # Calculate overall score
            overall_score = ats_checker.calculate_overall_score(component_scores)

            # AI Enhancement (if available)
            gemini_client = get_gemini_client()
            ai_analysis = None

            if gemini_client.is_available():
                with st.spinner("🤖 Getting AI insights..."):
                    ai_analysis = gemini_client.check_ats_compatibility(resume_text)

        # Display Results
        st.markdown("---")
        st.header("📊 ATS Analysis Results")

        # Overall Score
        col1, col2, col3 = st.columns(3)

        with col1:
            create_score_badge(overall_score, "Overall ATS Score")

        with col2:
            if overall_score >= 85:
                status = "Excellent ✅"
                color = "success"
            elif overall_score >= 70:
                status = "Good 👍"
                color = "info"
            elif overall_score >= 50:
                status = "Needs Improvement ⚠️"
                color = "warning"
            else:
                status = "Poor ❌"
                color = "error"

            create_alert(f"Status: {status}", color)

        with col3:
            if ai_analysis and ai_analysis.get('ats_score'):
                create_score_badge(ai_analysis['ats_score'], "AI Score")
            else:
                st.info("🤖 AI analysis unavailable")

        # Component Scores
        st.subheader("📈 Component Breakdown")

        col1, col2 = st.columns(2)

        with col1:
            create_metric_card("Format Compatibility", f"{format_analysis['score']}/100")
            create_metric_card("Content Structure", f"{structure_analysis['score']}/100")
            create_metric_card("Contact Information", f"{contact_analysis['score']}/100")

        with col2:
            create_metric_card("Keyword Optimization", f"{keyword_analysis['score']}/100")
            create_metric_card("Readability", f"{readability_analysis['score']}/100")
            if ai_analysis:
                ai_score = ai_analysis.get('ats_score', 0)
                create_metric_card("AI Assessment", f"{ai_score}/100")

        # Progress bars for visual representation
        st.subheader("🎯 Score Visualization")

        create_progress_bar(format_analysis['score'], 100, "Format Compatibility")
        create_progress_bar(structure_analysis['score'], 100, "Content Structure")
        create_progress_bar(keyword_analysis['score'], 100, "Keyword Optimization")
        create_progress_bar(readability_analysis['score'], 100, "Readability")
        create_progress_bar(contact_analysis['score'], 100, "Contact Information")

        # Detailed Issues and Recommendations
        st.markdown("---")
        st.header("🔧 Detailed Analysis & Recommendations")

        # Combine all issues and recommendations
        all_issues = []
        all_recommendations = []

        for analysis in [format_analysis, structure_analysis, keyword_analysis, 
                        readability_analysis, contact_analysis]:
            all_issues.extend(analysis.get('issues', []))
            all_recommendations.extend(analysis.get('recommendations', []))

        # Add AI insights if available
        if ai_analysis:
            if ai_analysis.get('issues'):
                all_issues.extend([issue.get('issue', '') for issue in ai_analysis['issues']])
            if ai_analysis.get('recommendations'):
                all_recommendations.extend(ai_analysis['recommendations'])

        col1, col2 = st.columns(2)

        with col1:
            if all_issues:
                st.subheader("⚠️ Issues Found")
                for i, issue in enumerate(all_issues, 1):
                    st.write(f"{i}. {issue}")
            else:
                create_alert("✅ No major issues found!", "success")

        with col2:
            if all_recommendations:
                create_recommendation_list(all_recommendations, "💡 Recommendations")

        # Keywords Found
        if keyword_analysis.get('keywords_found'):
            st.subheader("🔑 Keywords Found")
            keywords_text = ", ".join(keyword_analysis['keywords_found'])
            st.write(keywords_text)

        # AI Strengths (if available)
        if ai_analysis and ai_analysis.get('strengths'):
            st.subheader("💪 Strengths")
            for strength in ai_analysis['strengths']:
                st.write(f"✅ {strength}")

        # Save analysis to history
        analysis_result = {
            'timestamp': st.session_state.get('analysis_timestamp', ''),
            'overall_score': overall_score,
            'component_scores': component_scores,
            'issues_count': len(all_issues),
            'recommendations_count': len(all_recommendations)
        }

        if 'analysis_history' not in st.session_state:
            st.session_state['analysis_history'] = []

        st.session_state['analysis_history'].append(analysis_result)

        # Export options
        st.markdown("---")
        st.subheader("📤 Export Results")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 View Analytics"):
                st.switch_page("pages/3_📈_Analytics_Dashboard.py")

        with col2:
            if st.button("🎯 Match Jobs"):
                st.switch_page("pages/2_🎯_Job_Matcher.py")

        with col3:
            if st.button("📝 Improve Resume"):
                st.switch_page("pages/4_📝_Resume_Builder.py")

        # JSON Export
        export_data = {
            'overall_score': overall_score,
            'component_scores': component_scores,
            'issues': all_issues,
            'recommendations': all_recommendations,
            'keywords_found': keyword_analysis.get('keywords_found', []),
            'ai_analysis': ai_analysis
        }

        if st.button("💾 Export Analysis (JSON)"):
            st.download_button(
                label="Download Analysis",
                data=json.dumps(export_data, indent=2),
                file_name=f"ats_analysis_{overall_score}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()
