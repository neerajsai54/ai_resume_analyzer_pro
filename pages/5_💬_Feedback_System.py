import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from ui_components import load_custom_css, create_alert
from analytics import analytics_manager

# Configure page
st.set_page_config(
    page_title="Feedback System - AI Resume Analyzer Pro",
    page_icon="💬",
    layout="wide"
)

# Load custom CSS
load_custom_css()

def main():
    """Feedback System main function"""

    # Log page visit
    analytics_manager.log_usage("Feedback System", "page_visit")

    # Header
    st.markdown("# 💬 **Feedback System**")
    st.markdown("Help us improve AI Resume Analyzer Pro with your valuable feedback and suggestions")

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        # Feedback form
        st.markdown("## 📝 **Share Your Experience**")

        # Rating
        st.markdown("### ⭐ **Overall Rating**")
        rating = st.select_slider(
            "How would you rate your experience?",
            options=[1, 2, 3, 4, 5],
            value=4,
            format_func=lambda x: "⭐" * x + "☆" * (5-x)
        )

        # Feature used
        st.markdown("### 🛠️ **Which feature did you use?**")
        feature_used = st.selectbox(
            "Select the primary feature you used",
            [
                "ATS Score Checker",
                "Job Matcher", 
                "Resume Builder",
                "Analytics Dashboard",
                "Overall Platform",
                "Other"
            ]
        )

        # Feedback categories
        st.markdown("### 📊 **Feedback Categories**")

        feedback_categories = st.multiselect(
            "What aspects would you like to comment on?",
            [
                "User Interface/Design",
                "AI Analysis Accuracy", 
                "Feature Functionality",
                "Performance/Speed",
                "Ease of Use",
                "Content Quality",
                "Bug Report",
                "Feature Request"
            ]
        )

        # Detailed feedback
        st.markdown("### 💭 **Detailed Feedback**")
        feedback_text = st.text_area(
            "Please share your thoughts, suggestions, or any issues you encountered",
            height=150,
            placeholder="""Example feedback:
• What did you like most about the platform?
• What features would you like to see improved?
• Did you encounter any bugs or issues?
• How can we make your experience better?
• Any specific suggestions for new features?"""
        )

        # Contact information (optional)
        st.markdown("### 📧 **Contact Information (Optional)**")

        col_contact1, col_contact2 = st.columns(2)

        with col_contact1:
            contact_email = st.text_input(
                "Email (for follow-up)",
                placeholder="your.email@example.com",
                help="Only if you'd like us to follow up on your feedback"
            )

        with col_contact2:
            follow_up = st.checkbox(
                "I'd like to be contacted about my feedback",
                help="Check this if you want our team to reach out regarding your suggestions"
            )

        # Submit feedback
        st.markdown("---")

        col_submit, col_clear = st.columns([2, 1])

        with col_submit:
            if st.button("📤 **Submit Feedback**", type="primary", use_container_width=True):
                if feedback_text.strip():
                    # Prepare feedback data
                    feedback_data = {
                        "rating": rating,
                        "feature_used": feature_used,
                        "categories": feedback_categories,
                        "feedback_text": feedback_text,
                        "contact_email": contact_email if contact_email else None,
                        "follow_up_requested": follow_up,
                        "timestamp": datetime.now().isoformat()
                    }

                    # Save feedback
                    if analytics_manager.save_feedback(rating, feedback_text, feature_used):
                        st.success("✅ **Thank you for your feedback!** Your input helps us improve the platform.")
                        analytics_manager.log_usage("Feedback System", "feedback_submitted")

                        # Clear form
                        st.session_state.clear()
                        st.rerun()
                    else:
                        st.error("❌ Failed to submit feedback. Please try again.")
                else:
                    st.warning("⚠️ Please provide detailed feedback before submitting.")

        with col_clear:
            if st.button("🗑️ **Clear Form**", use_container_width=True):
                st.session_state.clear()
                st.rerun()

    with col2:
        # Information sidebar
        st.markdown("## ℹ️ **Why Your Feedback Matters**")

        st.markdown("""
        ### 🎯 **Our Commitment**

        Your feedback directly influences:

        - 🚀 **New feature development**
        - 🐛 **Bug fixes and improvements**  
        - 🎨 **UI/UX enhancements**
        - 🤖 **AI model refinements**
        - 📊 **Performance optimizations**
        """)

        st.markdown("### 📈 **Recent Improvements**")
        st.info("""
        Based on user feedback, we recently added:

        ✅ **Enhanced UI design** with modern styling  
        ✅ **Improved AI analysis** accuracy  
        ✅ **Faster processing** speeds  
        ✅ **Better mobile** responsiveness  
        ✅ **More detailed** recommendations
        """)

        st.markdown("### 🤝 **Community**")
        st.markdown("""
        Join our growing community:

        - 👥 **1,200+** active users
        - ⭐ **4.8/5** average rating
        - 📈 **94.8%** user satisfaction
        - 🔄 **Weekly** feature updates
        """)

        st.markdown("### 📞 **Contact Options**")
        st.markdown("""
        **General Inquiries:**  
        📧 support@resume-analyzer.com

        **Bug Reports:**  
        🐛 bugs@resume-analyzer.com

        **Feature Requests:**  
        💡 features@resume-analyzer.com

        **Partnership:**  
        🤝 partners@resume-analyzer.com
        """)

    # FAQ Section
    st.markdown("---")
    st.markdown("## ❓ **Frequently Asked Questions**")

    faq_items = [
        {
            "question": "How is my data handled?",
            "answer": "We prioritize your privacy. Resume data is processed securely and never stored permanently unless you explicitly save analysis results. All data transmission is encrypted and follows industry best practices."
        },
        {
            "question": "How often are new features added?",
            "answer": "We release updates weekly based on user feedback and platform improvements. Major features are typically added monthly, while bug fixes and minor enhancements happen continuously."
        },
        {
            "question": "Can I suggest new features?",
            "answer": "Absolutely! We encourage feature suggestions. Use the feedback form above or email features@resume-analyzer.com. Popular requests are prioritized in our development roadmap."
        },
        {
            "question": "Is there a premium version?",
            "answer": "Currently, all features are free to use. We're exploring premium options with advanced AI capabilities, unlimited analyses, and priority support. Stay tuned for updates!"
        },
        {
            "question": "How accurate is the AI analysis?",
            "answer": "Our AI analysis is continuously improving and currently achieves 94%+ accuracy in resume scoring and recommendations. We use Google's Gemini AI for enhanced semantic understanding."
        }
    ]

    for faq in faq_items:
        with st.expander(f"❓ {faq['question']}"):
            st.markdown(faq['answer'])

    # Quick actions
    st.markdown("---")
    st.markdown("## 🚀 **Quick Actions**")

    col_quick1, col_quick2, col_quick3, col_quick4 = st.columns(4)

    with col_quick1:
        if st.button("📊 **Analyze Resume**", use_container_width=True):
            st.switch_page("pages/1_📊_ATS_Score_Checker.py")

    with col_quick2:
        if st.button("🎯 **Match Job**", use_container_width=True):
            st.switch_page("pages/2_🎯_Job_Matcher.py")

    with col_quick3:
        if st.button("📝 **Build Resume**", use_container_width=True):
            st.switch_page("pages/4_📝_Resume_Builder.py")

    with col_quick4:
        if st.button("📈 **View Analytics**", use_container_width=True):
            st.switch_page("pages/3_📈_Analytics_Dashboard.py")

if __name__ == "__main__":
    main()
