import streamlit as st
import google.generativeai as genai
import os
import json
import time
from typing import Dict, List, Optional, Any
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiClient:
    """Enhanced Google Gemini AI client with rate limiting and error handling"""

    def __init__(self):
        self.api_key = self._get_api_key()
        self.model = None
        self.request_count = 0
        self.last_request_time = 0
        self.rate_limit_delay = 4  # 4 seconds between requests (15 per minute)

        if self.api_key:
            self._initialize_client()

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment variables or Streamlit secrets"""
        # Try environment variable first
        api_key = os.getenv('GOOGLE_API_KEY')

        # Try Streamlit secrets if environment variable not found
        if not api_key:
            try:
                api_key = st.secrets.get("GOOGLE_API_KEY")
            except:
                pass

        if not api_key:
            st.error("""
            🔑 **Google Gemini API Key Required**

            Please add your Google Gemini API key in one of these ways:
            1. Set environment variable: `GOOGLE_API_KEY=your_key_here`
            2. Add to Streamlit secrets: Create `.streamlit/secrets.toml` with:
               ```
               GOOGLE_API_KEY = "your_key_here"
               ```

            Get your API key from: https://makersuite.google.com/app/apikey
            """)

        return api_key

    def _initialize_client(self):
        """Initialize the Gemini client"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            st.error(f"Failed to initialize AI client: {e}")

    def _rate_limit(func):
        """Decorator to enforce rate limiting"""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            current_time = time.time()
            time_since_last = current_time - self.last_request_time

            if time_since_last < self.rate_limit_delay:
                sleep_time = self.rate_limit_delay - time_since_last
                logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)

            self.last_request_time = time.time()
            self.request_count += 1

            return func(self, *args, **kwargs)
        return wrapper

    @_rate_limit
    def _make_request(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Make a request to Gemini with retry logic"""
        if not self.model:
            return None

        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                if response and response.text:
                    return response.text
                else:
                    logger.warning(f"Empty response from Gemini on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"Gemini request failed on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    st.error(f"AI service temporarily unavailable: {e}")

        return None

    def analyze_resume_content(self, resume_text: str) -> Dict[str, Any]:
        """Analyze resume content and extract structured information"""
        prompt = f"""
        Analyze the following resume and provide a comprehensive evaluation in JSON format:

        Resume Text:
        {resume_text}

        Please analyze and return a JSON object with the following structure:
        {{
            "personal_info": {{
                "name": "extracted name",
                "email": "extracted email",
                "phone": "extracted phone",
                "location": "extracted location"
            }},
            "summary": "professional summary or objective",
            "experience": [
                {{
                    "title": "job title",
                    "company": "company name",
                    "duration": "employment duration",
                    "description": "role description"
                }}
            ],
            "education": [
                {{
                    "degree": "degree name",
                    "institution": "school name",
                    "year": "graduation year"
                }}
            ],
            "skills": ["skill1", "skill2", "skill3"],
            "content_quality": {{
                "grammar_score": 85,
                "clarity_score": 90,
                "impact_score": 75,
                "overall_score": 83
            }},
            "recommendations": [
                "specific improvement suggestion 1",
                "specific improvement suggestion 2"
            ]
        }}

        Ensure the JSON is valid and complete.
        """

        response = self._make_request(prompt)
        if response:
            try:
                # Clean the response to extract JSON
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                return self._fallback_analysis()

        return self._fallback_analysis()

    def check_ats_compatibility(self, resume_text: str) -> Dict[str, Any]:
        """Check ATS compatibility and provide detailed scoring"""
        prompt = f"""
        Evaluate the following resume for ATS (Applicant Tracking System) compatibility.
        Provide a detailed analysis in JSON format:

        Resume Text:
        {resume_text}

        Analyze and return JSON with this structure:
        {{
            "ats_score": 78,
            "categories": {{
                "format_compatibility": {{
                    "score": 85,
                    "feedback": "Good use of standard headings and formatting"
                }},
                "keyword_optimization": {{
                    "score": 70,
                    "feedback": "Could include more industry-specific keywords"
                }},
                "contact_information": {{
                    "score": 95,
                    "feedback": "Complete and properly formatted contact details"
                }},
                "section_organization": {{
                    "score": 80,
                    "feedback": "Well-organized sections with clear hierarchy"
                }},
                "length_optimization": {{
                    "score": 75,
                    "feedback": "Appropriate length for experience level"
                }},
                "readability": {{
                    "score": 88,
                    "feedback": "Clear and easy to parse content"
                }}
            }},
            "recommendations": [
                "Add more quantified achievements",
                "Include relevant industry keywords",
                "Optimize section headers for ATS scanning"
            ],
            "critical_issues": [],
            "strengths": [
                "Clear formatting",
                "Complete contact information"
            ]
        }}
        """

        response = self._make_request(prompt)
        if response:
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse ATS analysis JSON: {e}")

        return self._fallback_ats_analysis()

    def match_job_description(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Match resume to job description and provide compatibility analysis"""
        prompt = f"""
        Compare the following resume with the job description and provide a detailed matching analysis:

        Resume:
        {resume_text}

        Job Description:
        {job_description}

        Provide analysis in JSON format:
        {{
            "match_score": 82,
            "keyword_matches": [
                {{"keyword": "Python", "found": true, "importance": "high"}},
                {{"keyword": "Machine Learning", "found": true, "importance": "high"}},
                {{"keyword": "AWS", "found": false, "importance": "medium"}}
            ],
            "skill_gaps": [
                "AWS cloud services",
                "Docker containerization"
            ],
            "strengths": [
                "Strong Python programming background",
                "Relevant machine learning experience"
            ],
            "recommendations": [
                "Highlight Python projects more prominently",
                "Add AWS certification or experience",
                "Include specific ML algorithms used"
            ],
            "compatibility_areas": {{
                "technical_skills": 85,
                "experience_level": 80,
                "industry_knowledge": 75,
                "soft_skills": 70
            }}
        }}
        """

        response = self._make_request(prompt)
        if response:
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse job matching JSON: {e}")

        return self._fallback_job_match()

    def improve_resume_content(self, resume_text: str, target_role: str = "") -> Dict[str, Any]:
        """Generate improved resume content suggestions"""
        prompt = f"""
        Improve the following resume content for better impact and ATS optimization.
        {"Target role: " + target_role if target_role else ""}

        Current Resume:
        {resume_text}

        Provide improvements in JSON format:
        {{
            "improved_summary": "Enhanced professional summary",
            "improved_experience": [
                {{
                    "original": "Worked on projects",
                    "improved": "Led cross-functional team of 5 to deliver 3 high-impact projects, resulting in 25% efficiency improvement"
                }}
            ],
            "additional_keywords": ["keyword1", "keyword2"],
            "quantification_suggestions": [
                "Add specific metrics to achievement statements",
                "Include percentage improvements where possible"
            ],
            "action_items": [
                "Replace weak verbs with strong action verbs",
                "Add industry-specific terminology"
            ]
        }}
        """

        response = self._make_request(prompt)
        if response:
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse improvement JSON: {e}")

        return self._fallback_improvement()

    def _fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when AI is unavailable"""
        return {
            "personal_info": {"name": "", "email": "", "phone": "", "location": ""},
            "summary": "AI analysis temporarily unavailable",
            "experience": [],
            "education": [],
            "skills": [],
            "content_quality": {
                "grammar_score": 0,
                "clarity_score": 0,
                "impact_score": 0,
                "overall_score": 0
            },
            "recommendations": ["AI service temporarily unavailable. Please try again later."]
        }

    def _fallback_ats_analysis(self) -> Dict[str, Any]:
        """Fallback ATS analysis when AI is unavailable"""
        return {
            "ats_score": 0,
            "categories": {
                "format_compatibility": {"score": 0, "feedback": "Analysis unavailable"},
                "keyword_optimization": {"score": 0, "feedback": "Analysis unavailable"},
                "contact_information": {"score": 0, "feedback": "Analysis unavailable"},
                "section_organization": {"score": 0, "feedback": "Analysis unavailable"},
                "length_optimization": {"score": 0, "feedback": "Analysis unavailable"},
                "readability": {"score": 0, "feedback": "Analysis unavailable"}
            },
            "recommendations": ["AI service temporarily unavailable"],
            "critical_issues": [],
            "strengths": []
        }

    def _fallback_job_match(self) -> Dict[str, Any]:
        """Fallback job matching when AI is unavailable"""
        return {
            "match_score": 0,
            "keyword_matches": [],
            "skill_gaps": [],
            "strengths": [],
            "recommendations": ["AI service temporarily unavailable"],
            "compatibility_areas": {
                "technical_skills": 0,
                "experience_level": 0,
                "industry_knowledge": 0,
                "soft_skills": 0
            }
        }

    def _fallback_improvement(self) -> Dict[str, Any]:
        """Fallback improvement suggestions when AI is unavailable"""
        return {
            "improved_summary": "AI improvement service temporarily unavailable",
            "improved_experience": [],
            "additional_keywords": [],
            "quantification_suggestions": [],
            "action_items": ["AI service temporarily unavailable"]
        }

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return {
            "requests_made": self.request_count,
            "rate_limit_delay": self.rate_limit_delay,
            "api_connected": self.model is not None
        }

# Global instance
gemini_client = GeminiClient()
