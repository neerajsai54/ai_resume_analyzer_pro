"""
Resume Parser Module
Handles parsing of various resume formats (PDF, DOCX, TXT)
Optimized for Streamlit applications.
"""

import streamlit as st
import pdfplumber
import docx
from typing import Optional, Dict, Any, Tuple
import re
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

class ResumeParser:
    """
    A comprehensive resume parser that handles multiple file formats
    and extracts text content for analysis.
    """

    SUPPORTED_FORMATS = ['pdf', 'docx', 'txt']

    def __init__(self):
        self.supported_extensions = self.SUPPORTED_FORMATS

    def parse_resume(self, uploaded_file) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Parse uploaded resume file and extract text content.

        Args:
            uploaded_file: Streamlit uploaded file object

        Returns:
            Tuple of (extracted_text, metadata) or (None, None) if failed
        """
        if not uploaded_file:
            return None, None

        try:
            # Get file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()

            if file_extension not in self.supported_extensions:
                st.error(f"❌ Unsupported file format: {file_extension}")
                st.info(f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}")
                return None, None

            # Create metadata
            metadata = {
                'filename': uploaded_file.name,
                'file_size': uploaded_file.size,
                'file_type': file_extension,
                'mime_type': uploaded_file.type
            }

            # Extract text based on file type
            text_content = None

            if file_extension == 'pdf':
                text_content = self._parse_pdf(uploaded_file)
            elif file_extension == 'docx':
                text_content = self._parse_docx(uploaded_file)
            elif file_extension == 'txt':
                text_content = self._parse_txt(uploaded_file)

            if text_content:
                # Clean and normalize text
                text_content = self._clean_text(text_content)
                metadata['character_count'] = len(text_content)
                metadata['word_count'] = len(text_content.split())

                return text_content, metadata
            else:
                st.error("❌ Failed to extract text from the uploaded file.")
                return None, None

        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            st.error(f"❌ Error processing file: {str(e)}")
            return None, None

    def _parse_pdf(self, uploaded_file) -> Optional[str]:
        """Extract text from PDF file using pdfplumber."""
        try:
            text_content = ""

            with pdfplumber.open(BytesIO(uploaded_file.getvalue())) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                        else:
                            # If no text found, try extracting from images (OCR-like)
                            st.warning(f"⚠️ Page {page_num + 1} may contain images or non-standard text.")
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num + 1}: {str(e)}")
                        continue

            return text_content.strip() if text_content.strip() else None

        except Exception as e:
            logger.error(f"PDF parsing error: {str(e)}")
            st.error("❌ Failed to parse PDF. File may be corrupted or password-protected.")
            return None

    def _parse_docx(self, uploaded_file) -> Optional[str]:
        """Extract text from DOCX file using python-docx."""
        try:
            doc = docx.Document(BytesIO(uploaded_file.getvalue()))
            text_content = ""

            # Extract text from paragraphs
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content += paragraph.text + "\n"

            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            text_content += cell.text + " "
                    text_content += "\n"

            return text_content.strip() if text_content.strip() else None

        except Exception as e:
            logger.error(f"DOCX parsing error: {str(e)}")
            st.error("❌ Failed to parse DOCX file. File may be corrupted.")
            return None

    def _parse_txt(self, uploaded_file) -> Optional[str]:
        """Extract text from TXT file."""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

            for encoding in encodings:
                try:
                    text_content = uploaded_file.getvalue().decode(encoding)
                    return text_content.strip()
                except UnicodeDecodeError:
                    continue

            st.error("❌ Could not decode text file. Please ensure it's in a supported encoding.")
            return None

        except Exception as e:
            logger.error(f"TXT parsing error: {str(e)}")
            st.error("❌ Failed to parse text file.")
            return None

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters that might interfere with processing
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)

        # Normalize line breaks
        text = re.sub(r'\n+', '\n', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    def extract_basic_info(self, text: str) -> Dict[str, Any]:
        """
        Extract basic information from resume text using regex patterns.
        This is a fallback method when AI analysis is not available.
        """
        info = {
            'emails': [],
            'phones': [],
            'urls': [],
            'name_candidates': []
        }

        if not text:
            return info

        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        info['emails'] = list(set(re.findall(email_pattern, text)))

        # Phone number extraction (various formats)
        phone_patterns = [
            r'\b(?:\+?1[-\s]?)?\(?[0-9]{3}\)?[-\s]?[0-9]{3}[-\s]?[0-9]{4}\b',
            r'\b[0-9]{3}[-\.]?[0-9]{3}[-\.]?[0-9]{4}\b',
            r'\b\([0-9]{3}\)\s?[0-9]{3}[-\s]?[0-9]{4}\b'
        ]

        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        info['phones'] = list(set(phones))

        # URL extraction
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        info['urls'] = list(set(re.findall(url_pattern, text)))

        # Name candidates (first few lines, capitalized words)
        lines = text.split('\n')[:5]  # Check first 5 lines
        for line in lines:
            # Look for properly capitalized names (2-4 words, each capitalized)
            name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b'
            matches = re.findall(name_pattern, line.strip())
            info['name_candidates'].extend(matches)

        # Remove duplicates and sort
        info['name_candidates'] = list(set(info['name_candidates']))

        return info

    def validate_file(self, uploaded_file) -> Tuple[bool, str]:
        """
        Validate uploaded file before processing.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not uploaded_file:
            return False, "No file uploaded"

        # Check file size (limit to 10MB)
        if uploaded_file.size > 10 * 1024 * 1024:
            return False, "File size exceeds 10MB limit"

        # Check file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in self.SUPPORTED_FORMATS:
            return False, f"Unsupported file format: {file_extension}"

        # Check filename
        if not uploaded_file.name or len(uploaded_file.name) < 1:
            return False, "Invalid filename"

        return True, "File is valid"

    def get_file_info(self, uploaded_file) -> Dict[str, Any]:
        """Get basic information about the uploaded file."""
        if not uploaded_file:
            return {}

        return {
            'name': uploaded_file.name,
            'size': uploaded_file.size,
            'type': uploaded_file.type,
            'extension': uploaded_file.name.split('.')[-1].lower() if '.' in uploaded_file.name else 'unknown'
        }

# Utility function for easy import
def parse_uploaded_resume(uploaded_file):
    """
    Convenience function to parse an uploaded resume file.

    Args:
        uploaded_file: Streamlit uploaded file object

    Returns:
        Tuple of (text_content, metadata, basic_info)
    """
    parser = ResumeParser()

    # Validate file first
    is_valid, error_msg = parser.validate_file(uploaded_file)
    if not is_valid:
        st.error(f"❌ {error_msg}")
        return None, None, None

    # Parse the file
    text_content, metadata = parser.parse_resume(uploaded_file)

    if text_content:
        # Extract basic info as fallback
        basic_info = parser.extract_basic_info(text_content)
        return text_content, metadata, basic_info

    return None, None, None
