"""
AI Analysis System - Separate requests for analysis and text generation
"""
import google.generativeai as genai
import json
import pandas as pd
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """Handles AI analysis with separate requests for planning and text generation"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def analyze_data_structure(self, df: pd.DataFrame, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        First AI request: Analyze data structure and determine analysis approach
        
        Returns:
            - dataset_type: Type of dataset
            - required_columns: Columns needed for analysis
            - chart_specs: Specific chart requirements with column mappings
            - kpi_calculations: How to calculate KPIs
        """
        try:
            prompt = self._build_analysis_prompt(df, schema)
            response = self.model.generate_content(prompt)
            
            if response.text:
                analysis = self._parse_analysis_response(response.text)
                logger.info(f"Data analysis completed: {analysis.get('dataset_type', 'unknown')}")
                return analysis
            else:
                return self._fallback_analysis()
                
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return self._fallback_analysis()
    
    def generate_insights_text(self, kpis: Dict[str, Any], analysis_plan: Dict[str, Any]) -> str:
        """
        Second AI request: Generate text insights based on calculated KPIs
        
        Args:
            kpis: Calculated KPI values
            analysis_plan: Analysis plan from first request
            
        Returns:
            Generated insights text
        """
        try:
            prompt = self._build_insights_prompt(kpis, analysis_plan)
            response = self.model.generate_content(prompt)
            
            if response.text:
                logger.info("Insights text generated successfully")
                return response.text.strip()
            else:
                return self._fallback_insights(kpis)
                
        except Exception as e:
            logger.error(f"Insights generation failed: {str(e)}")
            return self._fallback_insights(kpis)
    
    def _build_analysis_prompt(self, df: pd.DataFrame, schema: Dict[str, Any]) -> str:
        """Build prompt for data structure analysis"""
        sample_data = df.head(3).to_dict('records') if len(df) > 0 else []
        
        return f"""
        Analyze this dataset structure and provide SPECIFIC analysis instructions.
        Return ONLY valid JSON (no markdown, no explanations):

        DATASET INFO:
        Columns: {list(df.columns)}
        Data Types: {dict(df.dtypes.astype(str))}
        Sample Rows: {sample_data}
        Row Count: {len(df)}
        Numeric Columns: {df.select_dtypes(include=['number']).columns.tolist()}
        Categorical Columns: {df.select_dtypes(include=['object']).columns.tolist()}

        Return JSON with this EXACT structure:
        {{
            "dataset_type": "<one of: ad_performance, sales_data, survey_feedback, financial_records, operations_metrics, weather_data, scientific_data, generic_tabular>",
            "required_columns": {{
                "primary_metric": "<actual_column_name_for_main_metric>",
                "secondary_metric": "<actual_column_name_for_secondary_metric>",
                "date_column": "<actual_date_column_name_or_null>",
                "category_column": "<actual_category_column_name_or_null>",
                "grouping_column": "<actual_grouping_column_name_or_null>"
            }},
            "chart_specs": [
                {{
                    "chart_type": "<chart_type>",
                    "x_column": "<actual_column_name>",
                    "y_column": "<actual_column_name>",
                    "purpose": "<what_this_chart_shows>"
                }}
            ],
            "kpi_calculations": [
                {{
                    "kpi_name": "<descriptive_name>",
                    "calculation": "<how_to_calculate>",
                    "columns_needed": ["<actual_column_names>"]
                }}
            ]
        }}

        Available chart types:
        - line_trend: Time series or sequential trends
        - bar_comparison: Compare categories or metrics
        - pie_distribution: Show proportions/distributions
        - scatter_correlation: Show relationships between 2 variables
        - histogram_distribution: Show data distribution
        - box_plot_outliers: Detect outliers
        - heatmap_correlation: Correlation matrix

        Focus on charts that will provide MEANINGFUL insights for this specific data type.
        """
    
    def _build_insights_prompt(self, kpis: Dict[str, Any], analysis_plan: Dict[str, Any]) -> str:
        """Build prompt for insights text generation"""
        dataset_type = analysis_plan.get('dataset_type', 'generic_tabular')
        
        return f"""
        Generate professional business insights based on these calculated KPIs.
        Write as a senior data analyst explaining findings to executives.

        DATASET TYPE: {dataset_type}
        
        CALCULATED KPIs:
        {json.dumps(kpis, indent=2, default=str)}

        ANALYSIS CONTEXT:
        {json.dumps(analysis_plan, indent=2)}

        Write 2-3 paragraphs covering:
        1. Key findings and trends
        2. Notable patterns or anomalies
        3. Business implications and recommendations

        Use specific numbers from the KPIs. Be concise and actionable.
        Focus on insights relevant to {dataset_type} business context.
        """
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate analysis JSON response"""
        try:
            # Clean response text
            clean_text = response_text.strip()
            if clean_text.startswith('```'):
                clean_text = clean_text.split('```')[1]
                if clean_text.startswith('json'):
                    clean_text = clean_text[4:]
            
            analysis = json.loads(clean_text)
            
            # Validate required fields
            required_fields = ['dataset_type', 'required_columns', 'chart_specs', 'kpi_calculations']
            if all(field in analysis for field in required_fields):
                return analysis
            else:
                logger.warning("Invalid analysis response structure, using fallback")
                return self._fallback_analysis()
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse analysis JSON response, using fallback")
            return self._fallback_analysis()
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when AI fails"""
        return {
            "dataset_type": "generic_tabular",
            "required_columns": {
                "primary_metric": None,
                "secondary_metric": None,
                "date_column": None,
                "category_column": None,
                "grouping_column": None
            },
            "chart_specs": [
                {
                    "chart_type": "bar_comparison",
                    "x_column": "auto_detect",
                    "y_column": "auto_detect",
                    "purpose": "Compare key metrics"
                }
            ],
            "kpi_calculations": [
                {
                    "kpi_name": "basic_stats",
                    "calculation": "summary_statistics",
                    "columns_needed": ["numeric_columns"]
                }
            ]
        }
    
    def _fallback_insights(self, kpis: Dict[str, Any]) -> str:
        """Fallback insights when AI fails"""
        return f"""
        Data Analysis Summary:
        
        The dataset contains {kpis.get('row_count', 'unknown')} records across {kpis.get('column_count', 'unknown')} columns.
        Data completeness is {kpis.get('data_completeness', 0):.1f}%.
        
        Key metrics have been calculated and visualized in the accompanying charts.
        Further analysis may reveal additional patterns and insights.
        """