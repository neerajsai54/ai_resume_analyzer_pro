import streamlit as st
from typing import Dict, Any, List
import json
import base64
from jinja2 import Template
from datetime import datetime
from gemini_client import gemini_client

class ResumeBuilder:
    """AI-powered resume builder with multiple templates"""

    def __init__(self):
        self.templates = {
            "modern_professional": {
                "name": "Modern Professional",
                "description": "Clean, modern design perfect for corporate roles",
                "color_scheme": "#2C3E50",
                "font_family": "Inter, sans-serif"
            },
            "creative_designer": {
                "name": "Creative Designer",
                "description": "Eye-catching design for creative professionals",
                "color_scheme": "#9B59B6",
                "font_family": "Roboto, sans-serif"
            },
            "technical_engineer": {
                "name": "Technical Engineer",
                "description": "Structured layout ideal for technical roles",
                "color_scheme": "#2980B9",
                "font_family": "Source Code Pro, monospace"
            }
        }

    def generate_resume_content(self, user_data: Dict[str, Any], target_role: str = "") -> Dict[str, Any]:
        """Generate enhanced resume content using AI"""

        if gemini_client.model:
            ai_improvements = gemini_client.improve_resume_content(
                json.dumps(user_data), target_role
            )

            if ai_improvements:
                return self._merge_ai_improvements(user_data, ai_improvements)

        # Fallback to template-based generation
        return self._template_based_generation(user_data)

    def _merge_ai_improvements(self, user_data: Dict[str, Any], ai_improvements: Dict[str, Any]) -> Dict[str, Any]:
        """Merge AI improvements with user data"""

        enhanced_data = user_data.copy()

        # Enhance professional summary
        if ai_improvements.get("improved_summary"):
            enhanced_data["summary"] = ai_improvements["improved_summary"]

        # Enhance experience descriptions
        if ai_improvements.get("improved_experience"):
            for i, improvement in enumerate(ai_improvements["improved_experience"]):
                if i < len(enhanced_data.get("experience", [])):
                    enhanced_data["experience"][i]["description"] = improvement.get("improved", 
                        enhanced_data["experience"][i].get("description", ""))

        # Add suggested keywords
        if ai_improvements.get("additional_keywords"):
            existing_skills = enhanced_data.get("skills", [])
            new_skills = ai_improvements["additional_keywords"]
            enhanced_data["skills"] = list(set(existing_skills + new_skills))

        return enhanced_data

    def _template_based_generation(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using templates when AI is unavailable"""

        enhanced_data = user_data.copy()

        # Generate professional summary if missing
        if not enhanced_data.get("summary"):
            enhanced_data["summary"] = self._generate_template_summary(user_data)

        # Enhance experience descriptions
        if enhanced_data.get("experience"):
            for experience in enhanced_data["experience"]:
                if not experience.get("description") or len(experience["description"]) < 50:
                    experience["description"] = self._generate_template_experience(experience)

        return enhanced_data

    def _generate_template_summary(self, user_data: Dict[str, Any]) -> str:
        """Generate a professional summary using templates"""

        name = user_data.get("personal_info", {}).get("name", "Professional")
        skills = user_data.get("skills", [])
        experience = user_data.get("experience", [])

        years_experience = len(experience)
        primary_skills = ", ".join(skills[:3]) if skills else "various technologies"

        templates = [
            f"Experienced professional with {years_experience}+ years in {primary_skills}. "
            f"Proven track record of delivering high-quality results and driving innovation.",

            f"Results-driven {name} specializing in {primary_skills}. "
            f"Strong background in problem-solving and team collaboration.",

            f"Dedicated professional with expertise in {primary_skills}. "
            f"Committed to continuous learning and delivering excellent outcomes."
        ]

        return templates[0]  # Return first template

    def _generate_template_experience(self, experience: Dict[str, str]) -> str:
        """Generate experience description using templates"""

        title = experience.get("title", "Professional")
        company = experience.get("company", "Company")

        templates = [
            f"Contributed to team success at {company} in the role of {title}. "
            f"Responsible for key projects and maintaining high standards of work quality.",

            f"Worked as {title} at {company}, focusing on delivering results and "
            f"collaborating effectively with cross-functional teams.",

            f"Served as {title} at {company}, taking on responsibilities that "
            f"contributed to organizational goals and professional growth."
        ]

        return templates[0]

    def build_html_resume(self, resume_data: Dict[str, Any], template_name: str) -> str:
        """Build HTML resume using specified template"""

        template_info = self.templates.get(template_name, self.templates["modern_professional"])

        if template_name == "modern_professional":
            return self._build_modern_professional(resume_data, template_info)
        elif template_name == "creative_designer":
            return self._build_creative_designer(resume_data, template_info)
        elif template_name == "technical_engineer":
            return self._build_technical_engineer(resume_data, template_info)
        else:
            return self._build_modern_professional(resume_data, template_info)

    def _build_modern_professional(self, data: Dict[str, Any], template_info: Dict) -> str:
        """Build modern professional template"""

        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ name }} - Resume</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }

                body {
                    font-family: {{ font_family }};
                    line-height: 1.6;
                    color: #333;
                    background: #fff;
                }

                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 40px 20px;
                }

                .header {
                    text-align: center;
                    margin-bottom: 40px;
                    padding-bottom: 20px;
                    border-bottom: 3px solid {{ color_scheme }};
                }

                .name {
                    font-size: 2.5em;
                    font-weight: 700;
                    color: {{ color_scheme }};
                    margin-bottom: 10px;
                }

                .contact-info {
                    font-size: 1.1em;
                    color: #666;
                }

                .section {
                    margin-bottom: 30px;
                }

                .section-title {
                    font-size: 1.4em;
                    font-weight: 600;
                    color: {{ color_scheme }};
                    margin-bottom: 15px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }

                .summary {
                    font-size: 1.1em;
                    line-height: 1.7;
                    color: #555;
                }

                .experience-item, .education-item {
                    margin-bottom: 20px;
                    padding-left: 20px;
                    border-left: 2px solid {{ color_scheme }};
                }

                .job-title, .degree-title {
                    font-size: 1.2em;
                    font-weight: 600;
                    color: {{ color_scheme }};
                }

                .company, .institution {
                    font-weight: 500;
                    color: #666;
                    margin-bottom: 5px;
                }

                .duration {
                    font-style: italic;
                    color: #888;
                    margin-bottom: 10px;
                }

                .description {
                    color: #555;
                    line-height: 1.6;
                }

                .skills {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                }

                .skill-tag {
                    background: {{ color_scheme }};
                    color: white;
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 0.9em;
                    font-weight: 500;
                }

                @media (max-width: 600px) {
                    .container {
                        padding: 20px 15px;
                    }

                    .name {
                        font-size: 2em;
                    }

                    .skills {
                        justify-content: center;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 class="name">{{ name }}</h1>
                    <div class="contact-info">
                        {% if email %}{{ email }}{% endif %}
                        {% if phone %} | {{ phone }}{% endif %}
                        {% if location %} | {{ location }}{% endif %}
                    </div>
                </div>

                {% if summary %}
                <div class="section">
                    <h2 class="section-title">Professional Summary</h2>
                    <p class="summary">{{ summary }}</p>
                </div>
                {% endif %}

                {% if experience %}
                <div class="section">
                    <h2 class="section-title">Experience</h2>
                    {% for exp in experience %}
                    <div class="experience-item">
                        <div class="job-title">{{ exp.title }}</div>
                        <div class="company">{{ exp.company }}</div>
                        {% if exp.duration %}<div class="duration">{{ exp.duration }}</div>{% endif %}
                        {% if exp.description %}<div class="description">{{ exp.description }}</div>{% endif %}
                    </div>
                    {% endfor %}
                </div>
                {% endif %}

                {% if education %}
                <div class="section">
                    <h2 class="section-title">Education</h2>
                    {% for edu in education %}
                    <div class="education-item">
                        <div class="degree-title">{{ edu.degree }}</div>
                        <div class="institution">{{ edu.institution }}</div>
                        {% if edu.year %}<div class="duration">{{ edu.year }}</div>{% endif %}
                    </div>
                    {% endfor %}
                </div>
                {% endif %}

                {% if skills %}
                <div class="section">
                    <h2 class="section-title">Skills</h2>
                    <div class="skills">
                        {% for skill in skills %}
                        <span class="skill-tag">{{ skill }}</span>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}
            </div>
        </body>
        </html>
        """

        template = Template(html_template)
        personal_info = data.get("personal_info", {})

        return template.render(
            name=personal_info.get("name", "Your Name"),
            email=personal_info.get("email", ""),
            phone=personal_info.get("phone", ""),
            location=personal_info.get("location", ""),
            summary=data.get("summary", ""),
            experience=data.get("experience", []),
            education=data.get("education", []),
            skills=data.get("skills", []),
            color_scheme=template_info["color_scheme"],
            font_family=template_info["font_family"]
        )

    def _build_creative_designer(self, data: Dict[str, Any], template_info: Dict) -> str:
        """Build creative designer template"""
        # Similar structure but with creative styling
        # For brevity, using modern professional template with different colors
        return self._build_modern_professional(data, template_info)

    def _build_technical_engineer(self, data: Dict[str, Any], template_info: Dict) -> str:
        """Build technical engineer template"""
        # Similar structure but with technical styling
        # For brevity, using modern professional template with different colors
        return self._build_modern_professional(data, template_info)

    def generate_pdf(self, html_content: str) -> bytes:
        """Generate PDF from HTML content"""
        try:
            # For production, you would use a library like pdfkit or weasyprint
            # For now, return placeholder
            return b"PDF generation would be implemented here"
        except Exception as e:
            st.error(f"PDF generation error: {e}")
            return b""

    def create_download_link(self, content: str, filename: str, file_type: str = "html") -> str:
        """Create download link for generated resume"""

        if file_type == "html":
            content_bytes = content.encode('utf-8')
            mime_type = "text/html"
        else:
            content_bytes = content
            mime_type = "application/pdf"

        b64 = base64.b64encode(content_bytes).decode()

        return f'<a href="data:{mime_type};base64,{b64}" download="{filename}" class="download-link">Download {filename}</a>'

    def validate_resume_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate resume data for completeness"""

        validation = {
            "is_valid": True,
            "missing_fields": [],
            "warnings": []
        }

        # Check required fields
        required_fields = {
            "personal_info.name": "Name",
            "personal_info.email": "Email",
            "summary": "Professional Summary",
            "experience": "Work Experience",
            "skills": "Skills"
        }

        for field_path, field_name in required_fields.items():
            if "." in field_path:
                section, field = field_path.split(".", 1)
                if not data.get(section, {}).get(field):
                    validation["missing_fields"].append(field_name)
                    validation["is_valid"] = False
            else:
                if not data.get(field_path):
                    validation["missing_fields"].append(field_name)
                    validation["is_valid"] = False

        # Check for warnings
        if not data.get("education"):
            validation["warnings"].append("Education section is empty")

        if len(data.get("skills", [])) < 3:
            validation["warnings"].append("Consider adding more skills")

        experience = data.get("experience", [])
        if len(experience) == 0:
            validation["warnings"].append("No work experience provided")
        elif len(experience) < 2:
            validation["warnings"].append("Consider adding more work experience")

        return validation

    def get_template_preview(self, template_name: str) -> str:
        """Get preview of template"""

        sample_data = {
            "personal_info": {
                "name": "John Doe",
                "email": "john.doe@email.com",
                "phone": "(555) 123-4567",
                "location": "New York, NY"
            },
            "summary": "Experienced professional with 5+ years in software development. Proven track record of delivering high-quality solutions.",
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Company",
                    "duration": "2020 - Present",
                    "description": "Developed and maintained web applications using modern technologies."
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "University Name",
                    "year": "2020"
                }
            ],
            "skills": ["Python", "JavaScript", "React", "SQL", "AWS"]
        }

        return self.build_html_resume(sample_data, template_name)

# Global resume builder instance
resume_builder = ResumeBuilder()
