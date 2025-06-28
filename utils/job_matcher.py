import streamlit as st
import re
from typing import Dict, List, Set, Any
from collections import Counter
import difflib
from gemini_client import gemini_client

class JobMatcher:
    """Advanced job description matching with semantic analysis"""

    def __init__(self):
        self.common_skills = {
            'technical': [
                'python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'node.js',
                'aws', 'azure', 'docker', 'kubernetes', 'git', 'linux', 'windows',
                'machine learning', 'data analysis', 'artificial intelligence', 'deep learning'
            ],
            'soft': [
                'leadership', 'communication', 'teamwork', 'problem solving', 'analytical',
                'project management', 'time management', 'adaptability', 'creativity'
            ],
            'business': [
                'strategy', 'planning', 'budgeting', 'forecasting', 'operations',
                'marketing', 'sales', 'customer service', 'business analysis'
            ]
        }

    def match_resume_to_job(self, resume_text: str, job_description: str, use_ai: bool = True) -> Dict[str, Any]:
        """Comprehensive job matching analysis"""

        if use_ai and gemini_client.model:
            # Use AI for semantic matching
            ai_match = gemini_client.match_job_description(resume_text, job_description)
            if ai_match.get("match_score", 0) > 0:
                return ai_match

        # Fallback to rule-based matching
        return self._rule_based_matching(resume_text, job_description)

    def _rule_based_matching(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Rule-based job matching when AI is unavailable"""

        # Extract keywords from both texts
        resume_keywords = self._extract_keywords(resume_text.lower())
        job_keywords = self._extract_keywords(job_description.lower())

        # Find matches and gaps
        matches = resume_keywords.intersection(job_keywords)
        gaps = job_keywords - resume_keywords

        # Calculate match score
        match_score = len(matches) / max(len(job_keywords), 1) * 100

        # Analyze keyword importance
        keyword_matches = self._analyze_keyword_matches(matches, gaps, job_description)

        # Identify skill gaps
        skill_gaps = self._identify_skill_gaps(gaps)

        # Find strengths
        strengths = self._find_strengths(matches, resume_text)

        # Generate recommendations
        recommendations = self._generate_matching_recommendations(gaps, matches, job_description)

        # Analyze compatibility areas
        compatibility_areas = self._analyze_compatibility_areas(resume_text, job_description)

        return {
            "match_score": round(match_score),
            "keyword_matches": keyword_matches,
            "skill_gaps": skill_gaps,
            "strengths": strengths,
            "recommendations": recommendations,
            "compatibility_areas": compatibility_areas
        }

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract relevant keywords from text"""
        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'can', 'shall', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over',
            'under', 'again', 'further', 'then', 'once'
        }

        # Extract words and phrases
        words = re.findall(r'\b[a-z]+\b', text)

        # Extract multi-word technical terms
        phrases = re.findall(r'\b[a-z]+\s+[a-z]+\b', text)
        phrases.extend(re.findall(r'\b[a-z]+\s+[a-z]+\s+[a-z]+\b', text))

        # Combine and filter
        keywords = set()

        # Add single words (length > 3, not stop words)
        for word in words:
            if len(word) > 3 and word not in stop_words:
                keywords.add(word)

        # Add phrases
        for phrase in phrases:
            if not any(stop_word in phrase.split() for stop_word in stop_words):
                keywords.add(phrase)

        # Add known skills
        for category, skills in self.common_skills.items():
            for skill in skills:
                if skill.lower() in text:
                    keywords.add(skill.lower())

        return keywords

    def _analyze_keyword_matches(self, matches: Set[str], gaps: Set[str], job_description: str) -> List[Dict]:
        """Analyze keyword matches with importance"""
        keyword_matches = []

        # Analyze matches
        for keyword in matches:
            importance = self._determine_keyword_importance(keyword, job_description)
            keyword_matches.append({
                "keyword": keyword,
                "found": True,
                "importance": importance
            })

        # Analyze gaps (important missing keywords)
        for keyword in list(gaps)[:10]:  # Limit to top 10 gaps
            importance = self._determine_keyword_importance(keyword, job_description)
            if importance in ['high', 'medium']:
                keyword_matches.append({
                    "keyword": keyword,
                    "found": False,
                    "importance": importance
                })

        return keyword_matches

    def _determine_keyword_importance(self, keyword: str, job_description: str) -> str:
        """Determine the importance of a keyword based on context"""
        job_lower = job_description.lower()
        keyword_count = job_lower.count(keyword.lower())

        # Check if it's in requirements/qualifications section
        requirements_section = re.search(r'(requirements?|qualifications?|skills?)[:\s]+(.*?)(?=\n\n|$)', 
                                       job_lower, re.DOTALL)

        is_in_requirements = False
        if requirements_section and keyword.lower() in requirements_section.group(2):
            is_in_requirements = True

        # Check if it's a technical skill
        is_technical = any(keyword.lower() in skills for skills in self.common_skills.values())

        # Determine importance
        if keyword_count >= 3 or is_in_requirements:
            return "high"
        elif keyword_count >= 2 or is_technical:
            return "medium"
        else:
            return "low"

    def _identify_skill_gaps(self, gaps: Set[str]) -> List[str]:
        """Identify critical skill gaps"""
        skill_gaps = []

        # Prioritize technical skills
        for gap in gaps:
            for category, skills in self.common_skills.items():
                if gap.lower() in [skill.lower() for skill in skills]:
                    skill_gaps.append(gap.title())
                    break

        # Add other important gaps
        other_gaps = [gap for gap in gaps if gap not in [sg.lower() for sg in skill_gaps]]
        skill_gaps.extend(list(other_gaps)[:5])  # Add up to 5 more

        return skill_gaps[:10]  # Limit to 10 total

    def _find_strengths(self, matches: Set[str], resume_text: str) -> List[str]:
        """Find key strengths based on matches"""
        strengths = []

        # Group matches by category
        for category, skills in self.common_skills.items():
            category_matches = [match for match in matches 
                              if match.lower() in [skill.lower() for skill in skills]]

            if len(category_matches) >= 2:
                if category == 'technical':
                    strengths.append(f"Strong technical background in {', '.join(category_matches[:3])}")
                elif category == 'soft':
                    strengths.append(f"Excellent soft skills including {', '.join(category_matches[:3])}")
                elif category == 'business':
                    strengths.append(f"Solid business acumen in {', '.join(category_matches[:3])}")

        # Add experience-related strengths
        if 'experience' in matches and 'years' in resume_text.lower():
            strengths.append("Relevant professional experience")

        return strengths[:5]  # Limit to 5 strengths

    def _generate_matching_recommendations(self, gaps: Set[str], matches: Set[str], 
                                         job_description: str) -> List[str]:
        """Generate recommendations for better job matching"""
        recommendations = []

        # Skill gap recommendations
        priority_gaps = [gap for gap in gaps if self._determine_keyword_importance(gap, job_description) == 'high']

        for gap in priority_gaps[:3]:
            if gap in [skill.lower() for category in self.common_skills.values() for skill in category]:
                recommendations.append(f"Consider gaining experience in {gap.title()}")
            else:
                recommendations.append(f"Highlight {gap.title()} experience if available")

        # Keyword optimization recommendations
        if len(matches) < 10:
            recommendations.append("Include more job-specific keywords in your resume")

        # Experience recommendations
        if 'senior' in job_description.lower() and 'senior' not in ' '.join(matches):
            recommendations.append("Emphasize senior-level experience and leadership")

        # Industry recommendations
        industry_keywords = self._extract_industry_keywords(job_description)
        missing_industry = [kw for kw in industry_keywords if kw not in matches]
        if missing_industry:
            recommendations.append(f"Add industry-specific terms: {', '.join(missing_industry[:3])}")

        return recommendations[:6]  # Limit to 6 recommendations

    def _extract_industry_keywords(self, job_description: str) -> List[str]:
        """Extract industry-specific keywords"""
        # Common industry indicators
        industry_patterns = {
            'technology': ['software', 'tech', 'digital', 'innovation', 'platform'],
            'finance': ['financial', 'banking', 'investment', 'portfolio', 'risk'],
            'healthcare': ['medical', 'patient', 'clinical', 'hospital', 'healthcare'],
            'retail': ['customer', 'sales', 'merchandise', 'store', 'retail'],
            'consulting': ['client', 'consulting', 'advisory', 'strategy', 'solution']
        }

        job_lower = job_description.lower()
        found_keywords = []

        for industry, keywords in industry_patterns.items():
            for keyword in keywords:
                if keyword in job_lower:
                    found_keywords.append(keyword)

        return found_keywords

    def _analyze_compatibility_areas(self, resume_text: str, job_description: str) -> Dict[str, int]:
        """Analyze compatibility in different areas"""

        resume_lower = resume_text.lower()
        job_lower = job_description.lower()

        # Technical skills compatibility
        tech_keywords = self.common_skills['technical']
        resume_tech = sum(1 for skill in tech_keywords if skill in resume_lower)
        job_tech = sum(1 for skill in tech_keywords if skill in job_lower)
        tech_score = min(100, (resume_tech / max(job_tech, 1)) * 100) if job_tech > 0 else 50

        # Experience level compatibility
        experience_indicators = ['years', 'experience', 'senior', 'junior', 'lead', 'manager']
        resume_exp = sum(1 for indicator in experience_indicators if indicator in resume_lower)
        job_exp = sum(1 for indicator in experience_indicators if indicator in job_lower)
        exp_score = min(100, (resume_exp / max(job_exp, 1)) * 100) if job_exp > 0 else 60

        # Industry knowledge compatibility
        industry_keywords = self._extract_industry_keywords(job_description)
        industry_match = sum(1 for keyword in industry_keywords if keyword in resume_lower)
        industry_score = min(100, (industry_match / max(len(industry_keywords), 1)) * 100) if industry_keywords else 70

        # Soft skills compatibility
        soft_keywords = self.common_skills['soft']
        resume_soft = sum(1 for skill in soft_keywords if skill in resume_lower)
        job_soft = sum(1 for skill in soft_keywords if skill in job_lower)
        soft_score = min(100, (resume_soft / max(job_soft, 1)) * 100) if job_soft > 0 else 65

        return {
            "technical_skills": round(tech_score),
            "experience_level": round(exp_score),
            "industry_knowledge": round(industry_score),
            "soft_skills": round(soft_score)
        }

    def extract_job_requirements(self, job_description: str) -> Dict[str, List[str]]:
        """Extract structured requirements from job description"""

        job_lower = job_description.lower()

        # Extract requirements section
        requirements_pattern = r'(requirements?|qualifications?|skills?)[:\s]+(.*?)(?=\n\s*[a-z]+:|$)'
        requirements_match = re.search(requirements_pattern, job_lower, re.DOTALL)

        requirements_text = requirements_match.group(2) if requirements_match else job_lower

        # Extract different types of requirements
        must_have = []
        nice_to_have = []
        education = []
        experience = []

        # Look for must-have vs nice-to-have
        if 'required' in requirements_text or 'must' in requirements_text:
            required_section = re.split(r'(nice to have|preferred|plus)', requirements_text)[0]
            must_have.extend(self._extract_keywords(required_section))

        # Extract education requirements
        education_pattern = r'(bachelor|master|phd|degree|diploma|certification)'
        education_matches = re.findall(education_pattern, requirements_text)
        education.extend(education_matches)

        # Extract experience requirements
        exp_pattern = r'(\d+)[+\s]*(years?|yrs?)\s+(of\s+)?experience'
        exp_matches = re.findall(exp_pattern, requirements_text)
        if exp_matches:
            experience.append(f"{exp_matches[0][0]}+ years experience")

        return {
            "must_have": list(must_have)[:10],
            "nice_to_have": list(nice_to_have)[:5],
            "education": education,
            "experience": experience
        }

# Global job matcher instance
job_matcher = JobMatcher()
