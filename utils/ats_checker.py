import streamlit as st
import re
from typing import Dict, List, Any
from gemini_client import gemini_client

class ATSChecker:
    """Advanced ATS (Applicant Tracking System) compatibility checker"""

    def __init__(self):
        self.scoring_categories = {
            "format_compatibility": 0.20,  # 20% weight
            "keyword_optimization": 0.25,   # 25% weight
            "contact_information": 0.15,    # 15% weight
            "section_organization": 0.20,   # 20% weight
            "length_optimization": 0.10,    # 10% weight
            "readability": 0.10             # 10% weight
        }

    def analyze_ats_compatibility(self, resume_text: str, use_ai: bool = True) -> Dict[str, Any]:
        """Comprehensive ATS compatibility analysis"""

        if use_ai and gemini_client.model:
            # Use AI for detailed analysis
            ai_analysis = gemini_client.check_ats_compatibility(resume_text)
            if ai_analysis.get("ats_score", 0) > 0:
                return ai_analysis

        # Fallback to rule-based analysis
        return self._rule_based_analysis(resume_text)

    def _rule_based_analysis(self, resume_text: str) -> Dict[str, Any]:
        """Rule-based ATS analysis when AI is unavailable"""

        scores = {}
        feedback = {}
        recommendations = []
        critical_issues = []
        strengths = []

        # Format Compatibility Analysis
        format_score, format_feedback = self._check_format_compatibility(resume_text)
        scores["format_compatibility"] = {"score": format_score, "feedback": format_feedback}

        # Keyword Optimization Analysis
        keyword_score, keyword_feedback = self._check_keyword_optimization(resume_text)
        scores["keyword_optimization"] = {"score": keyword_score, "feedback": keyword_feedback}

        # Contact Information Analysis
        contact_score, contact_feedback = self._check_contact_information(resume_text)
        scores["contact_information"] = {"score": contact_score, "feedback": contact_feedback}

        # Section Organization Analysis
        section_score, section_feedback = self._check_section_organization(resume_text)
        scores["section_organization"] = {"score": section_score, "feedback": section_feedback}

        # Length Optimization Analysis
        length_score, length_feedback = self._check_length_optimization(resume_text)
        scores["length_optimization"] = {"score": length_score, "feedback": length_feedback}

        # Readability Analysis
        readability_score, readability_feedback = self._check_readability(resume_text)
        scores["readability"] = {"score": readability_score, "feedback": readability_feedback}

        # Calculate overall ATS score
        overall_score = self._calculate_overall_score(scores)

        # Generate recommendations
        recommendations = self._generate_recommendations(scores)

        # Identify critical issues
        critical_issues = self._identify_critical_issues(scores)

        # Identify strengths
        strengths = self._identify_strengths(scores)

        return {
            "ats_score": overall_score,
            "categories": scores,
            "recommendations": recommendations,
            "critical_issues": critical_issues,
            "strengths": strengths
        }

    def _check_format_compatibility(self, text: str) -> tuple:
        """Check format compatibility with ATS systems"""
        score = 100
        issues = []

        # Check for complex formatting that ATS might struggle with
        if len(re.findall(r'[│┌┐└┘├┤┬┴┼]', text)) > 0:
            score -= 20
            issues.append("Contains table borders/special characters")

        # Check for excessive punctuation
        special_chars = len(re.findall(r'[★☆●○■□▪▫]', text))
        if special_chars > 5:
            score -= 15
            issues.append("Too many special characters/symbols")

        # Check for proper text structure
        lines = text.split('\n')
        if len([line for line in lines if line.strip()]) < 10:
            score -= 10
            issues.append("Very short content")

        feedback = f"Format compatibility: {score}/100"
        if issues:
            feedback += f". Issues: {', '.join(issues)}"
        else:
            feedback += ". Clean, ATS-friendly format detected."

        return score, feedback

    def _check_keyword_optimization(self, text: str) -> tuple:
        """Check keyword optimization and density"""
        score = 100
        issues = []

        # Common professional keywords
        professional_keywords = [
            'experience', 'skills', 'management', 'development', 'analysis',
            'project', 'team', 'leadership', 'strategy', 'implementation'
        ]

        text_lower = text.lower()
        keyword_count = sum(1 for keyword in professional_keywords if keyword in text_lower)

        if keyword_count < 3:
            score -= 30
            issues.append("Insufficient professional keywords")
        elif keyword_count < 5:
            score -= 15
            issues.append("Could use more industry keywords")

        # Check for action verbs
        action_verbs = [
            'managed', 'developed', 'implemented', 'created', 'led', 'improved',
            'achieved', 'increased', 'decreased', 'optimized', 'analyzed'
        ]

        action_verb_count = sum(1 for verb in action_verbs if verb in text_lower)
        if action_verb_count < 3:
            score -= 20
            issues.append("Needs more strong action verbs")

        feedback = f"Keyword optimization: {score}/100"
        if issues:
            feedback += f". Issues: {', '.join(issues)}"
        else:
            feedback += ". Good keyword usage detected."

        return score, feedback

    def _check_contact_information(self, text: str) -> tuple:
        """Check completeness of contact information"""
        score = 100
        issues = []

        # Email check
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.search(email_pattern, text):
            score -= 40
            issues.append("Missing email address")

        # Phone check
        phone_patterns = [
            r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            r'\b[0-9]{3}-[0-9]{3}-[0-9]{4}\b'
        ]

        has_phone = any(re.search(pattern, text) for pattern in phone_patterns)
        if not has_phone:
            score -= 30
            issues.append("Missing phone number")

        # LinkedIn check
        if 'linkedin' not in text.lower():
            score -= 15
            issues.append("Consider adding LinkedIn profile")

        # Location check
        location_indicators = ['city', 'state', 'address', ',']
        has_location = any(indicator in text.lower() for indicator in location_indicators)
        if not has_location:
            score -= 15
            issues.append("Consider adding location information")

        feedback = f"Contact information: {score}/100"
        if issues:
            feedback += f". Issues: {', '.join(issues)}"
        else:
            feedback += ". Complete contact information provided."

        return score, feedback

    def _check_section_organization(self, text: str) -> tuple:
        """Check section organization and structure"""
        score = 100
        issues = []

        # Common section headers
        required_sections = ['experience', 'education', 'skills']
        optional_sections = ['summary', 'objective', 'certifications', 'projects']

        text_lower = text.lower()

        missing_required = []
        for section in required_sections:
            if section not in text_lower:
                missing_required.append(section)

        if missing_required:
            score -= len(missing_required) * 25
            issues.append(f"Missing sections: {', '.join(missing_required)}")

        # Check for proper header formatting
        headers = re.findall(r'^[A-Z][A-Z\s]+$', text, re.MULTILINE)
        if len(headers) < 2:
            score -= 20
            issues.append("Unclear section headers")

        feedback = f"Section organization: {score}/100"
        if issues:
            feedback += f". Issues: {', '.join(issues)}"
        else:
            feedback += ". Well-organized sections detected."

        return score, feedback

    def _check_length_optimization(self, text: str) -> tuple:
        """Check resume length optimization"""
        score = 100
        issues = []

        word_count = len(text.split())

        if word_count < 200:
            score -= 40
            issues.append(f"Too short ({word_count} words)")
        elif word_count > 800:
            score -= 20
            issues.append(f"Too long ({word_count} words)")
        elif word_count > 600:
            score -= 10
            issues.append("Consider condensing")

        # Check for bullet point usage
        bullet_indicators = ['•', '●', '-', '*']
        has_bullets = any(indicator in text for indicator in bullet_indicators)
        if not has_bullets:
            score -= 15
            issues.append("Consider using bullet points")

        feedback = f"Length optimization: {score}/100"
        if issues:
            feedback += f". Issues: {', '.join(issues)}"
        else:
            feedback += ". Appropriate length and formatting."

        return score, feedback

    def _check_readability(self, text: str) -> tuple:
        """Check readability and clarity"""
        score = 100
        issues = []

        # Check for excessive jargon or complex words
        sentences = re.split(r'[.!?]+', text)
        long_sentences = [s for s in sentences if len(s.split()) > 25]

        if len(long_sentences) > len(sentences) * 0.3:
            score -= 20
            issues.append("Some sentences are too long")

        # Check for repetitive words
        words = text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1

        overused_words = [word for word, count in word_freq.items() if count > 5]
        if overused_words:
            score -= 10
            issues.append("Some words are overused")

        # Check for variety in sentence starters
        sentence_starters = []
        for sentence in sentences:
            words = sentence.strip().split()
            if words:
                sentence_starters.append(words[0].lower())

        starter_variety = len(set(sentence_starters)) / max(len(sentence_starters), 1)
        if starter_variety < 0.5:
            score -= 15
            issues.append("Sentence structure could be more varied")

        feedback = f"Readability: {score}/100"
        if issues:
            feedback += f". Issues: {', '.join(issues)}"
        else:
            feedback += ". Clear and readable content."

        return score, feedback

    def _calculate_overall_score(self, scores: Dict) -> int:
        """Calculate weighted overall ATS score"""
        total_score = 0
        for category, weight in self.scoring_categories.items():
            category_score = scores.get(category, {}).get("score", 0)
            total_score += category_score * weight

        return round(total_score)

    def _generate_recommendations(self, scores: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        for category, data in scores.items():
            score = data.get("score", 0)
            if score < 80:
                if category == "format_compatibility":
                    recommendations.append("Use standard fonts and avoid complex formatting")
                elif category == "keyword_optimization":
                    recommendations.append("Include more industry-specific keywords and action verbs")
                elif category == "contact_information":
                    recommendations.append("Ensure all contact information is complete and visible")
                elif category == "section_organization":
                    recommendations.append("Use clear section headers and logical organization")
                elif category == "length_optimization":
                    recommendations.append("Optimize resume length (aim for 400-600 words)")
                elif category == "readability":
                    recommendations.append("Improve clarity and vary sentence structure")

        return recommendations

    def _identify_critical_issues(self, scores: Dict) -> List[str]:
        """Identify critical issues that must be addressed"""
        critical_issues = []

        for category, data in scores.items():
            score = data.get("score", 0)
            if score < 60:
                critical_issues.append(f"Critical: {category.replace('_', ' ').title()}")

        return critical_issues

    def _identify_strengths(self, scores: Dict) -> List[str]:
        """Identify resume strengths"""
        strengths = []

        for category, data in scores.items():
            score = data.get("score", 0)
            if score >= 90:
                strengths.append(f"Excellent {category.replace('_', ' ')}")

        return strengths

# Global ATS checker instance
ats_checker = ATSChecker()
