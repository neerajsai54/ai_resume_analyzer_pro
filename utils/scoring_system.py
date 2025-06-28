import streamlit as st
from typing import Dict, Any, List
import json
import statistics
from datetime import datetime

class ScoringSystem:
    """Comprehensive resume scoring system with weighted categories"""

    def __init__(self):
        self.scoring_weights = {
            "content_quality": 0.25,      # 25% - Grammar, clarity, impact
            "skills_relevance": 0.20,     # 20% - Relevant skills and expertise
            "experience_depth": 0.20,     # 20% - Work experience quality
            "formatting": 0.15,           # 15% - Visual presentation
            "ats_compatibility": 0.15,    # 15% - ATS-friendly format
            "quantified_impact": 0.05     # 5% - Measurable achievements
        }

        self.score_ranges = {
            "excellent": (90, 100),
            "very_good": (80, 89),
            "good": (70, 79),
            "fair": (60, 69),
            "needs_improvement": (0, 59)
        }

    def calculate_comprehensive_score(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive resume score with detailed breakdown"""

        scores = {}

        # Content Quality Score
        content_score = self._evaluate_content_quality(resume_data)
        scores["content_quality"] = content_score

        # Skills Relevance Score
        skills_score = self._evaluate_skills_relevance(resume_data)
        scores["skills_relevance"] = skills_score

        # Experience Depth Score
        experience_score = self._evaluate_experience_depth(resume_data)
        scores["experience_depth"] = experience_score

        # Formatting Score
        formatting_score = self._evaluate_formatting(resume_data)
        scores["formatting"] = formatting_score

        # ATS Compatibility Score
        ats_score = self._evaluate_ats_compatibility(resume_data)
        scores["ats_compatibility"] = ats_score

        # Quantified Impact Score
        impact_score = self._evaluate_quantified_impact(resume_data)
        scores["quantified_impact"] = impact_score

        # Calculate weighted overall score
        overall_score = self._calculate_weighted_score(scores)

        # Generate detailed feedback
        feedback = self._generate_detailed_feedback(scores, overall_score)

        return {
            "overall_score": overall_score,
            "category_scores": scores,
            "score_breakdown": self._create_score_breakdown(scores),
            "performance_level": self._get_performance_level(overall_score),
            "feedback": feedback,
            "improvement_suggestions": self._generate_improvement_suggestions(scores),
            "strengths": self._identify_strengths(scores),
            "timestamp": datetime.now().isoformat()
        }

    def _evaluate_content_quality(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate content quality including grammar, clarity, and impact"""

        text = resume_data.get("raw_text", "")
        ai_analysis = resume_data.get("ai_analysis", {})

        # Base score from AI analysis if available
        if ai_analysis and "content_quality" in ai_analysis:
            base_score = ai_analysis["content_quality"].get("overall_score", 70)
        else:
            base_score = self._rule_based_content_analysis(text)

        # Additional rule-based checks
        word_count = len(text.split())

        # Word count optimization
        if 300 <= word_count <= 600:
            word_score = 100
        elif 200 <= word_count < 300 or 600 < word_count <= 800:
            word_score = 85
        else:
            word_score = 70

        # Combine scores
        final_score = (base_score * 0.7) + (word_score * 0.3)

        return {
            "score": round(final_score),
            "details": {
                "grammar_clarity": base_score,
                "word_count_optimization": word_score,
                "word_count": word_count
            },
            "feedback": self._get_content_feedback(final_score, word_count)
        }

    def _evaluate_skills_relevance(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate relevance and quality of listed skills"""

        text = resume_data.get("raw_text", "").lower()
        skills = resume_data.get("extracted_skills", [])

        # Technical skills score
        technical_skills = [
            'python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'angular',
            'aws', 'azure', 'docker', 'kubernetes', 'git', 'linux', 'machine learning',
            'data analysis', 'project management', 'agile', 'scrum'
        ]

        found_technical = sum(1 for skill in technical_skills if skill in text)
        technical_score = min(100, (found_technical / 5) * 100)

        # Soft skills score
        soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem solving',
            'analytical', 'creative', 'adaptable', 'organized'
        ]

        found_soft = sum(1 for skill in soft_skills if skill in text)
        soft_score = min(100, (found_soft / 3) * 100)

        # Skills organization score
        skills_section_score = 100 if 'skills' in text else 50

        # Combined score
        final_score = (technical_score * 0.5) + (soft_score * 0.3) + (skills_section_score * 0.2)

        return {
            "score": round(final_score),
            "details": {
                "technical_skills": technical_score,
                "soft_skills": soft_score,
                "skills_organization": skills_section_score,
                "skills_count": len(skills)
            },
            "feedback": self._get_skills_feedback(final_score, found_technical, found_soft)
        }

    def _evaluate_experience_depth(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate work experience quality and depth"""

        text = resume_data.get("raw_text", "")
        experience = resume_data.get("extracted_experience", [])

        # Experience section presence
        has_experience_section = 'experience' in text.lower() or 'employment' in text.lower()
        section_score = 100 if has_experience_section else 30

        # Number of positions
        position_indicators = len(re.findall(r'\b(\d{4})\s*[-–—]\s*(\d{4}|present)', text, re.IGNORECASE))
        positions_score = min(100, (position_indicators / 3) * 100)

        # Action verbs usage
        action_verbs = [
            'managed', 'led', 'developed', 'implemented', 'created', 'improved',
            'increased', 'decreased', 'achieved', 'delivered', 'coordinated'
        ]

        found_verbs = sum(1 for verb in action_verbs if verb in text.lower())
        verbs_score = min(100, (found_verbs / 5) * 100)

        # Combined score
        final_score = (section_score * 0.4) + (positions_score * 0.3) + (verbs_score * 0.3)

        return {
            "score": round(final_score),
            "details": {
                "experience_section": section_score,
                "number_of_positions": positions_score,
                "action_verbs_usage": verbs_score,
                "positions_found": position_indicators
            },
            "feedback": self._get_experience_feedback(final_score, position_indicators)
        }

    def _evaluate_formatting(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate visual formatting and presentation"""

        text = resume_data.get("raw_text", "")
        file_type = resume_data.get("file_type", "unknown")

        # File type score
        type_scores = {"pdf": 100, "docx": 90, "txt": 60}
        file_type_score = type_scores.get(file_type, 50)

        # Structure score (sections, headers)
        sections = ['summary', 'experience', 'education', 'skills']
        found_sections = sum(1 for section in sections if section in text.lower())
        structure_score = (found_sections / len(sections)) * 100

        # Length appropriateness
        word_count = len(text.split())
        if 300 <= word_count <= 600:
            length_score = 100
        elif 200 <= word_count < 300 or 600 < word_count <= 800:
            length_score = 85
        else:
            length_score = 70

        # Combined score
        final_score = (file_type_score * 0.3) + (structure_score * 0.4) + (length_score * 0.3)

        return {
            "score": round(final_score),
            "details": {
                "file_format": file_type_score,
                "structure_organization": structure_score,
                "length_appropriateness": length_score,
                "sections_found": found_sections
            },
            "feedback": self._get_formatting_feedback(final_score, file_type, found_sections)
        }

    def _evaluate_ats_compatibility(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate ATS compatibility"""

        ats_analysis = resume_data.get("ats_analysis", {})

        if ats_analysis and "ats_score" in ats_analysis:
            ats_score = ats_analysis["ats_score"]
        else:
            # Basic ATS check
            text = resume_data.get("raw_text", "")
            ats_score = self._basic_ats_check(text)

        return {
            "score": ats_score,
            "details": ats_analysis.get("categories", {}),
            "feedback": f"ATS compatibility score: {ats_score}/100"
        }

    def _evaluate_quantified_impact(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate use of quantified achievements"""

        text = resume_data.get("raw_text", "")

        # Look for numbers and percentages
        numbers = re.findall(r'\b\d+(?:[.,]\d+)?[%]?\b', text)
        percentages = re.findall(r'\b\d+(?:[.,]\d+)?%\b', text)

        # Look for impact words with numbers
        impact_patterns = [
            r'increased?\s+(?:by\s+)?\d+[%]?',
            r'decreased?\s+(?:by\s+)?\d+[%]?',
            r'improved?\s+(?:by\s+)?\d+[%]?',
            r'saved?\s+(?:by\s+)?\$?\d+',
            r'managed?\s+(?:a\s+team\s+of\s+)?\d+'
        ]

        impact_mentions = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in impact_patterns)

        # Calculate score
        numbers_score = min(100, len(numbers) * 20)
        impact_score = min(100, impact_mentions * 30)

        final_score = (numbers_score * 0.6) + (impact_score * 0.4)

        return {
            "score": round(final_score),
            "details": {
                "quantified_achievements": impact_score,
                "numerical_data": numbers_score,
                "numbers_found": len(numbers),
                "impact_statements": impact_mentions
            },
            "feedback": self._get_impact_feedback(final_score, impact_mentions)
        }

    def _calculate_weighted_score(self, scores: Dict[str, Dict]) -> int:
        """Calculate weighted overall score"""

        total_score = 0
        for category, weight in self.scoring_weights.items():
            category_score = scores.get(category, {}).get("score", 0)
            total_score += category_score * weight

        return round(total_score)

    def _get_performance_level(self, score: int) -> str:
        """Get performance level based on score"""

        for level, (min_score, max_score) in self.score_ranges.items():
            if min_score <= score <= max_score:
                return level.replace("_", " ").title()

        return "Unknown"

    def _create_score_breakdown(self, scores: Dict[str, Dict]) -> Dict[str, int]:
        """Create simplified score breakdown for visualization"""

        breakdown = {}
        for category, data in scores.items():
            breakdown[category.replace("_", " ").title()] = data.get("score", 0)

        return breakdown

    def _generate_detailed_feedback(self, scores: Dict[str, Dict], overall_score: int) -> str:
        """Generate comprehensive feedback"""

        performance_level = self._get_performance_level(overall_score)

        feedback = f"Your resume scored {overall_score}/100, placing it in the '{performance_level}' category. "

        # Identify top performing areas
        top_scores = sorted(scores.items(), key=lambda x: x[1].get("score", 0), reverse=True)
        best_category = top_scores[0][0].replace("_", " ")
        worst_category = top_scores[-1][0].replace("_", " ")

        feedback += f"Your strongest area is {best_category} ({top_scores[0][1].get('score', 0)}/100). "
        feedback += f"Your area for improvement is {worst_category} ({top_scores[-1][1].get('score', 0)}/100)."

        return feedback

    def _generate_improvement_suggestions(self, scores: Dict[str, Dict]) -> List[str]:
        """Generate specific improvement suggestions"""

        suggestions = []

        for category, data in scores.items():
            score = data.get("score", 0)
            if score < 80:
                if category == "content_quality":
                    suggestions.append("Improve grammar and clarity of content")
                elif category == "skills_relevance":
                    suggestions.append("Add more relevant technical and soft skills")
                elif category == "experience_depth":
                    suggestions.append("Provide more detailed work experience with action verbs")
                elif category == "formatting":
                    suggestions.append("Improve resume structure and organization")
                elif category == "ats_compatibility":
                    suggestions.append("Optimize for ATS compatibility")
                elif category == "quantified_impact":
                    suggestions.append("Add more quantified achievements and metrics")

        return suggestions

    def _identify_strengths(self, scores: Dict[str, Dict]) -> List[str]:
        """Identify resume strengths"""

        strengths = []

        for category, data in scores.items():
            score = data.get("score", 0)
            if score >= 85:
                category_name = category.replace("_", " ").title()
                strengths.append(f"Excellent {category_name}")

        return strengths

    # Helper methods for specific feedback
    def _get_content_feedback(self, score: int, word_count: int) -> str:
        if score >= 85:
            return "Excellent content quality with clear, professional language"
        elif score >= 70:
            return f"Good content quality. Word count: {word_count}"
        else:
            return f"Content needs improvement. Consider professional editing. Word count: {word_count}"

    def _get_skills_feedback(self, score: int, technical: int, soft: int) -> str:
        return f"Skills assessment: {technical} technical skills, {soft} soft skills found"

    def _get_experience_feedback(self, score: int, positions: int) -> str:
        return f"Experience section analysis. {positions} positions identified"

    def _get_formatting_feedback(self, score: int, file_type: str, sections: int) -> str:
        return f"Format: {file_type.upper()}, {sections} standard sections found"

    def _get_impact_feedback(self, score: int, impact_statements: int) -> str:
        return f"Impact analysis: {impact_statements} quantified achievements found"

    def _rule_based_content_analysis(self, text: str) -> int:
        """Basic rule-based content analysis"""
        score = 70  # Base score

        # Check for professional language indicators
        professional_words = ['achieved', 'managed', 'developed', 'led', 'implemented']
        found_professional = sum(1 for word in professional_words if word in text.lower())
        score += min(20, found_professional * 4)

        return min(100, score)

    def _basic_ats_check(self, text: str) -> int:
        """Basic ATS compatibility check"""
        score = 70  # Base score

        # Check for contact info
        if '@' in text:
            score += 10

        # Check for sections
        sections = ['experience', 'education', 'skills']
        found_sections = sum(1 for section in sections if section in text.lower())
        score += (found_sections / len(sections)) * 20

        return min(100, score)

# Global scoring system instance
scoring_system = ScoringSystem()
