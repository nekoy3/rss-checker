#!/usr/bin/env python3
"""
AI Suggester for Blog Content Generation
Uses Google's Gemini API to suggest blog topics and outlines
"""

import google.generativeai as genai
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


class AISuggester:
    """AI-powered blog content suggester using Gemini API"""
    
    def __init__(self, api_key: str):
        """
        Initialize AI Suggester
        
        Args:
            api_key: Google Gemini API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config={
                "temperature": 0.9,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        logger.info("✓ AI Suggester initialized with Gemini 2.5 Flash")
