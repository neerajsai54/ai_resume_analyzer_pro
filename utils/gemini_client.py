"""
Gemini AI Client for Streamlit Applications
This module provides a secure and robust interface to Google's Gemini API
optimized for Streamlit Cloud deployment.
"""

import streamlit as st
import google.generativeai as genai
from typing import Optional, Dict, Any, List
import time
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiClient:
    """
    A robust Gemini AI client for Streamlit applications.
    Handles API key management, rate limiting, and error handling.
    """

    def __init__(self):
        self.model = None
        self.api_key = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Gemini client with API key from Streamlit secrets."""
        try:
            # Try to get API key from Streamlit secrets first
            if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
                self.api_key = st.secrets['GOOGLE_API_KEY']
            else:
                # Fallback to environment variable for local development
                import os
                self.api_key = os.getenv('GOOGLE_API_KEY')

            if not self.api_key:
                st.error("⚠️ Google API Key not found. Please add it to Streamlit secrets.")
                st.info("Go to Streamlit Cloud settings and add GOOGLE_API_KEY to secrets.")
                return

            # Configure Gemini
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')

            logger.info("Gemini client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            st.error(f"Failed to initialize AI client: {str(e)}")

    def _rate_limit(func):
        """Decorator to implement rate limiting."""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, '_last_request_time'):
                self._last_request_time = 0

            # Ensure at least 1 second between requests
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            if time_since_last < 1.0:
                time.sleep(1.0 - time_since_last)

            self._last_request_time = time.time()
            return func(self, *args, **kwargs)
        return wrapper

    @_rate_limit
    def generate_content(self, prompt: str, context: str = "") -> Optional[str]:
        """
        Generate content using Gemini AI with error handling and rate limiting.

        Args:
            prompt: The main prompt for generation
            context: Additional context to include

        Returns:
            Generated text or None if failed
        """
        if not self.model:
            st.error("AI client not initialized. Please check your API key.")
            return None

        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt

            with st.spinner("🤖 AI is analyzing..."):
                response = self.model.generate_content(full_prompt)

                if response and response.text:
                    return response.text.strip()
                else:
                    st.warning("AI returned empty response. Please try again.")
                    return None

        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower():
                st.error("🚫 API quota exceeded. Please try again later or upgrade your API plan.")
            elif "api_key" in error_msg.lower():
                st.error("🔑 API key error. Please check your configuration.")
            else:
                st.error(f"❌ AI processing failed: {error_msg}")

            logger.error(f"Gemini API error: {error_msg}")
            return None

    def analyze_resume(self, resume_text: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a resume and extract structured information.

        Args:
            resume_text: The text content of the resume

        Returns:
            Dictionary with analyzed resume data or None if failed
        """
        prompt = f"""Analyze the following resume text and extract key information in JSON format.

        Resume Text:
        {resume_text}

        Please extract and return the following information as a valid JSON object:
        {{
            "personal_info": {{
                "name": "extracted name or null",
                "email": "extracted email or null", 
                "phone": "extracted phone or null",
                "location": "extracted location or null"
            }},
            "summary": "professional summary or null",
            "skills": ["list", "of", "skills"],
            "experience": [
                {{
                    "company": "company name",
                    "position": "job title", 
                    "duration": "time period",
                    "description": "job description"
                }}
            ],
            "education": [
                {{
                    "institution": "school name",
                    "degree": "degree type",
                    "field": "field of study",
                    "year": "graduation year"
                }}
            ],
            "achievements": ["list", "of", "achievements"],
            "certifications": ["list", "of", "certifications"]
        }}

        Only return the valid JSON object, no additional text."""

        response = self.generate_content(prompt)
        if response:
            try:
                # Clean the response to extract JSON
                import json
                import re

                # Find JSON content between curly braces
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    return json.loads(json_str)
                else:
                    # Fallback: try to parse the entire response
                    return json.loads(response)

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                st.error("Failed to parse AI response. Please try again.")
                return None

        return None

    def improve_resume_content(self, content: str, job_description: str = "") -> Optional[str]:
        """Generate improved resume content suggestions."""
        context = f"Job Description: {job_description}\n\n" if job_description else ""

        prompt = f"""Improve the following resume content to make it more compelling and ATS-friendly:

        Current Content:
        {content}

        Please provide:
        1. Rewritten content with stronger action verbs
        2. Quantified achievements where possible
        3. Keywords optimized for ATS systems
        4. Professional formatting suggestions

        Focus on impact and measurable results."""

        return self.generate_content(prompt, context)

    def check_ats_compatibility(self, resume_text: str) -> Optional[Dict[str, Any]]:
        """Check ATS compatibility and provide recommendations."""
        prompt = f"""Analyze the following resume for ATS (Applicant Tracking System) compatibility.

        Resume Text:
        {resume_text}

        Provide analysis in JSON format:
        {{
            "ats_score": 85,
            "issues": [
                {{
                    "category": "formatting",
                    "issue": "description of issue",
                    "severity": "high|medium|low",
                    "fix": "how to fix this issue"
                }}
            ],
            "recommendations": ["specific recommendation 1", "specific recommendation 2"],
            "keywords_found": ["keyword1", "keyword2"],
            "missing_sections": ["section1", "section2"],
            "strengths": ["strength1", "strength2"]
        }}

        Only return valid JSON."""

        response = self.generate_content(prompt)
        if response:
            try:
                import json
                import re

                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return json.loads(response)

            except json.JSONDecodeError:
                return None

        return None

    def is_available(self) -> bool:
        """Check if the Gemini client is available and configured."""
        return self.model is not None and self.api_key is not None

# Global client instance
_gemini_client = None

def get_gemini_client() -> GeminiClient:
    """Get or create a global Gemini client instance."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
