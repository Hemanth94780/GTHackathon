"""
LLM-driven Dataset Classification and Analysis Planning
"""
import google.generativeai as genai
import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class LLMPlanner:
    """LLM-driven analysis planner"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def create_analysis_plan(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate analysis plan based on schema metadata
        
        Args:
            schema: Schema metadata from SchemaDetector
            
        Returns:
            Analysis plan dictionary
        """
        try:
            prompt = self._build_planning_prompt(schema)
            response = self.model.generate_content(prompt)
            
            if response.text:
                plan = self._parse_llm_response(response.text)
                logger.info(f"Analysis plan created: {plan['dataset_type']}")
                return plan
            else:
                return self._fallback_plan()
                
        except Exception as e:
            logger.error(f"LLM planning failed: {str(e)}")
            return self._fallback_plan()
    
    def _build_planning_prompt(self, schema: Dict[str, Any]) -> str:
        """Build prompt for LLM analysis planning"""
        return f"""
        Analyze this dataset schema and return ONLY valid JSON (no markdown, no explanations):

        SCHEMA:
        Columns: {schema['columns']}
        Data Types: {schema['data_types']}
        Sample Data: {schema['sample_rows'][:2]}
        Row Count: {schema['row_count']}

        Return JSON with this EXACT structure:
        {{
            "dataset_type": "<one of: ad_performance, sales_data, survey_feedback, financial_records, operations_metrics, generic_tabular>",
            "kpis": ["list", "of", "relevant", "kpis"],
            "charts": ["list", "of", "chart", "types"],
            "dimensions": {{
                "date": "<date_column_name_or_null>",
                "category": "<category_column_name_or_null>"
            }}
        }}

        Chart types: line_trend, bar_comparison, pie_distribution, scatter_correlation
        """
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate LLM JSON response"""
        try:
            # Clean response text
            clean_text = response_text.strip()
            if clean_text.startswith('```'):
                clean_text = clean_text.split('```')[1]
                if clean_text.startswith('json'):
                    clean_text = clean_text[4:]
            
            plan = json.loads(clean_text)
            
            # Validate required fields
            required_fields = ['dataset_type', 'kpis', 'charts', 'dimensions']
            if all(field in plan for field in required_fields):
                return plan
            else:
                logger.warning("Invalid LLM response structure, using fallback")
                return self._fallback_plan()
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM JSON response, using fallback")
            return self._fallback_plan()
    
    def _fallback_plan(self) -> Dict[str, Any]:
        """Fallback analysis plan when LLM fails"""
        return {
            "dataset_type": "generic_tabular",
            "kpis": ["row_count", "column_summary", "data_completeness"],
            "charts": ["bar_comparison"],
            "dimensions": {
                "date": None,
                "category": None
            }
        }