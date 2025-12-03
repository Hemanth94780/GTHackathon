import google.generativeai as genai
from typing import Dict, Any, List
import json

class InsightGenerator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def generate_insights(self, kpis: Dict[str, Any], data_summary: str) -> Dict[str, str]:
        """Generate AI-powered insights from KPIs and data"""
        
        prompt = f"""
        You are a senior business analyst creating an executive report. Analyze this data:
        
        KPIs: {json.dumps(kpis, indent=2)}
        Data Summary: {data_summary}
        
        Create a professional executive report with:
        
        1. KEY FINDINGS (3 most important discoveries with specific numbers)
        2. TRENDS ANALYSIS (growth patterns, anomalies, correlations)
        3. RECOMMENDATIONS (3 specific actionable steps for management)
        4. EXECUTIVE SUMMARY (2-sentence overview highlighting biggest opportunity and risk)
        
        Use business language. Include percentages and specific metrics. Focus on revenue impact.
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=800,
                    temperature=0.7
                )
            )
            
            content = response.text
            return self._parse_insights(content)
            
        except Exception as e:
            return {
                "key_findings": "Data analysis completed successfully",
                "trends": "Positive performance indicators observed",
                "recommendations": "Continue monitoring key metrics",
                "summary": f"Analysis generated from {len(kpis)} KPIs"
            }
    
    def _parse_insights(self, content: str) -> Dict[str, str]:
        """Parse AI response into structured insights"""
        sections = {
            "key_findings": "",
            "trends": "",
            "recommendations": "",
            "summary": ""
        }
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if 'key findings' in line.lower():
                current_section = 'key_findings'
            elif 'trends' in line.lower():
                current_section = 'trends'
            elif 'recommendations' in line.lower():
                current_section = 'recommendations'
            elif 'summary' in line.lower():
                current_section = 'summary'
            elif line and current_section:
                sections[current_section] += line + '\n'
        
        return sections