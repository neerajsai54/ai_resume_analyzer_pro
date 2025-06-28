import streamlit as st
import sys
from pathlib import Path
import json

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from ui_components import load_custom_css, create_alert
from resume_builder import resume_builder
from analytics import analytics_manager

# Configure page
st.set_page_config(
    page_title="Resume Builder - AI Resume Analyzer Pro",
    page_icon="📝",
    layout="wide"
)

# Load custom CSS
load_custom_css()

def main():
    """Resume Builder main function"""

    # Log page visit
    analytics_manager.log_usage("Resume Builder", "page_visit")

    # Header
    st.markdown("# 📝 **AI Resume Builder**")
    st.markdown("Create professional resumes with AI-powered content generation and modern templates")

    # Sidebar template selection
    with st.sidebar:
        st.markdown("### 🎨 **Template Selection**")

        template_options = {
            "modern_professional": "🏢 Modern Professional",
            "creative_designer": "🎨 Creative Designer", 
            "technical_engineer": "⚙️ Technical Engineer"
        }

        selected_template = st.selectbox(
            "Choose a template",
            options=list(template_options.keys()),
            format_func=lambda x: template_options[x],
            index=0
        )

        # Template preview
        if st.button("👀 Preview Template", use_container_width=True):
            with st.spinner("Generating preview..."):
                preview_html = resume_builder.get_template_preview(selected_template)
                st.components.v1.html(preview_html, height=400, scrolling=True)

        st.markdown("### 🤖 **AI Assistance**")
        st.markdown("""
        - ✨ **Auto-generate** professional summaries
        - 🎯 **Optimize** experience descriptions  
        - 📝 **Suggest** relevant keywords
        - 🔧 **Improve** content quality
        """)

    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📋 **Enter Information**", "🤖 **AI Enhancement**", "📄 **Generated Resume**"])

    with tab1:
        st.markdown("## 📋 **Personal Information**")

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Full Name*", placeholder="John Doe")
            email = st.text_input("Email Address*", placeholder="john.doe@email.com")
            phone = st.text_input("Phone Number", placeholder="(555) 123-4567")

        with col2:
            location = st.text_input("Location", placeholder="New York, NY")
            linkedin = st.text_input("LinkedIn Profile", placeholder="linkedin.com/in/johndoe")
            website = st.text_input("Website/Portfolio", placeholder="www.johndoe.com")

        # Professional Summary
        st.markdown("## 📝 **Professional Summary**")
        summary = st.text_area(
            "Professional Summary",
            height=100,
            placeholder="Brief summary of your professional background, key skills, and career objectives..."
        )

        # Work Experience
        st.markdown("## 💼 **Work Experience**")

        if 'experience_entries' not in st.session_state:
            st.session_state.experience_entries = [{}]

        experience_data = []
        for i, entry in enumerate(st.session_state.experience_entries):
            with st.expander(f"Position {i+1}", expanded=(i == 0)):
                col1, col2 = st.columns(2)

                with col1:
                    job_title = st.text_input(f"Job Title", key=f"job_title_{i}", 
                                            value=entry.get('title', ''))
                    company = st.text_input(f"Company", key=f"company_{i}", 
                                          value=entry.get('company', ''))

                with col2:
                    start_date = st.text_input(f"Start Date", key=f"start_date_{i}", 
                                             placeholder="Jan 2020", value=entry.get('start_date', ''))
                    end_date = st.text_input(f"End Date", key=f"end_date_{i}", 
                                           placeholder="Present", value=entry.get('end_date', ''))

                description = st.text_area(f"Job Description", key=f"description_{i}", 
                                         height=100, value=entry.get('description', ''),
                                         placeholder="• Describe your key responsibilities and achievements\n• Use bullet points for better readability\n• Include quantifiable results where possible")

                if job_title or company:
                    duration = f"{start_date} - {end_date}" if start_date and end_date else ""
                    experience_data.append({
                        'title': job_title,
                        'company': company,
                        'duration': duration,
                        'description': description
                    })

        col_add, col_remove = st.columns(2)
        with col_add:
            if st.button("➕ Add Experience", use_container_width=True):
                st.session_state.experience_entries.append({})
                st.rerun()

        with col_remove:
            if len(st.session_state.experience_entries) > 1:
                if st.button("➖ Remove Last", use_container_width=True):
                    st.session_state.experience_entries.pop()
                    st.rerun()

        # Education
        st.markdown("## 🎓 **Education**")

        if 'education_entries' not in st.session_state:
            st.session_state.education_entries = [{}]

        education_data = []
        for i, entry in enumerate(st.session_state.education_entries):
            with st.expander(f"Education {i+1}", expanded=(i == 0)):
                col1, col2 = st.columns(2)

                with col1:
                    degree = st.text_input(f"Degree", key=f"degree_{i}", 
                                         value=entry.get('degree', ''))
                    institution = st.text_input(f"Institution", key=f"institution_{i}", 
                                              value=entry.get('institution', ''))

                with col2:
                    graduation_year = st.text_input(f"Graduation Year", key=f"grad_year_{i}", 
                                                  placeholder="2020", value=entry.get('year', ''))
                    gpa = st.text_input(f"GPA (Optional)", key=f"gpa_{i}", 
                                      placeholder="3.8", value=entry.get('gpa', ''))

                if degree or institution:
                    education_data.append({
                        'degree': degree,
                        'institution': institution,
                        'year': graduation_year,
                        'gpa': gpa if gpa else None
                    })

        col_add_edu, col_remove_edu = st.columns(2)
        with col_add_edu:
            if st.button("➕ Add Education", use_container_width=True):
                st.session_state.education_entries.append({})
                st.rerun()

        with col_remove_edu:
            if len(st.session_state.education_entries) > 1:
                if st.button("➖ Remove Last Education", use_container_width=True):
                    st.session_state.education_entries.pop()
                    st.rerun()

        # Skills
        st.markdown("## 🛠️ **Skills**")
        skills_input = st.text_area(
            "Skills (one per line or comma-separated)",
            height=100,
            placeholder="Python\nJavaScript\nProject Management\nData Analysis\nTeam Leadership"
        )

        # Parse skills
        skills_data = []
        if skills_input:
            # Try comma-separated first, then newline-separated
            if ',' in skills_input:
                skills_data = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
            else:
                skills_data = [skill.strip() for skill in skills_input.split('\n') if skill.strip()]

        # Compile all data
        resume_data = {
            "personal_info": {
                "name": name,
                "email": email,
                "phone": phone,
                "location": location,
                "linkedin": linkedin,
                "website": website
            },
            "summary": summary,
            "experience": experience_data,
            "education": education_data,
            "skills": skills_data
        }

        # Store in session state
        st.session_state.resume_data = resume_data

    with tab2:
        st.markdown("## 🤖 **AI-Powered Enhancement**")

        if 'resume_data' not in st.session_state:
            create_alert("Please fill in your information in the first tab before using AI enhancement", "warning", "⚠️")
        else:
            col1, col2 = st.columns([2, 1])

            with col1:
                target_role = st.text_input(
                    "Target Role (Optional)",
                    placeholder="Software Engineer, Marketing Manager, Data Scientist...",
                    help="Specify the role you're targeting for better AI optimization"
                )

            with col2:
                if st.button("✨ **Enhance with AI**", type="primary", use_container_width=True):
                    with st.spinner("🤖 AI is enhancing your resume content..."):
                        enhanced_data = resume_builder.generate_resume_content(
                            st.session_state.resume_data, target_role
                        )
                        st.session_state.enhanced_resume_data = enhanced_data

                        # Log enhancement
                        analytics_manager.log_usage("Resume Builder", "ai_enhancement")

                    st.success("✅ AI enhancement completed!")
                    st.rerun()

            # Show enhancements if available
            if 'enhanced_resume_data' in st.session_state:
                st.markdown("### 📝 **AI-Enhanced Content**")

                enhanced = st.session_state.enhanced_resume_data
                original = st.session_state.resume_data

                # Compare summary
                if enhanced.get('summary') != original.get('summary'):
                    st.markdown("#### Professional Summary")
                    st.markdown("**Original:**")
                    st.info(original.get('summary', 'No summary provided'))
                    st.markdown("**AI-Enhanced:**")
                    st.success(enhanced.get('summary', 'No enhanced summary'))

                # Compare experience
                if enhanced.get('experience') != original.get('experience'):
                    st.markdown("#### Experience Descriptions")
                    for i, (orig, enh) in enumerate(zip(original.get('experience', []), enhanced.get('experience', []))):
                        if orig.get('description') != enh.get('description'):
                            st.markdown(f"**{enh.get('title', 'Position')} at {enh.get('company', 'Company')}**")

                            col_orig, col_enh = st.columns(2)
                            with col_orig:
                                st.markdown("*Original:*")
                                st.text_area("", value=orig.get('description', ''), height=100, key=f"orig_{i}", disabled=True)

                            with col_enh:
                                st.markdown("*AI-Enhanced:*")
                                st.text_area("", value=enh.get('description', ''), height=100, key=f"enh_{i}", disabled=True)

                # Apply enhancements
                if st.button("✅ **Apply AI Enhancements**", use_container_width=True):
                    st.session_state.resume_data = st.session_state.enhanced_resume_data
                    st.success("AI enhancements applied to your resume!")
                    analytics_manager.log_usage("Resume Builder", "enhancements_applied")
                    st.rerun()

    with tab3:
        st.markdown("## 📄 **Generated Resume**")

        if 'resume_data' not in st.session_state:
            create_alert("Please fill in your information in the first tab to generate a resume", "warning", "⚠️")
        else:
            # Validate data
            validation = resume_builder.validate_resume_data(st.session_state.resume_data)

            if not validation["is_valid"]:
                st.error("❌ **Please complete the following required fields:**")
                for field in validation["missing_fields"]:
                    st.markdown(f"• {field}")
                return

            # Show warnings
            if validation["warnings"]:
                st.warning("⚠️ **Suggestions:**")
                for warning in validation["warnings"]:
                    st.markdown(f"• {warning}")

            # Generate resume
            col1, col2 = st.columns([3, 1])

            with col2:
                if st.button("🔄 **Regenerate Resume**", use_container_width=True):
                    st.rerun()

                # Download options
                st.markdown("### 💾 **Download Options**")

                if st.button("📄 **Download HTML**", use_container_width=True):
                    html_content = resume_builder.build_html_resume(
                        st.session_state.resume_data, selected_template
                    )

                    download_link = resume_builder.create_download_link(
                        html_content, f"{st.session_state.resume_data['personal_info']['name']}_Resume.html"
                    )

                    st.markdown(download_link, unsafe_allow_html=True)
                    analytics_manager.log_usage("Resume Builder", "html_download")

                # Note about PDF
                st.info("💡 **PDF download** will be available in the next update")

            with col1:
                # Generate and display resume
                with st.spinner("📝 Generating your resume..."):
                    html_content = resume_builder.build_html_resume(
                        st.session_state.resume_data, selected_template
                    )

                # Display resume
                st.components.v1.html(html_content, height=800, scrolling=True)

                # Log resume generation
                analytics_manager.log_usage("Resume Builder", "resume_generated")

if __name__ == "__main__":
    main()
