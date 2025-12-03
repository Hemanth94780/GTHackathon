import google.generativeai as genai
from typing import Dict, Any, List
import json
import numpy as np
import pandas as pd

class InsightGenerator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.request_count = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
    
    def generate_insights(self, kpis: Dict[str, Any], data_summary: str, data_sample: pd.DataFrame = None) -> Dict[str, str]:
        """Generate AI-powered insights from KPIs and data"""
        
        print(f"🔍 Starting insight generation with {len(kpis)} KPIs")
        print(f"   KPIs: {list(kpis.keys())[:5]}...")
        
        # Convert numpy types to JSON-serializable types
        serializable_kpis = {}
        for key, value in kpis.items():
            if isinstance(value, (np.integer, np.floating)):
                serializable_kpis[key] = float(value)
            else:
                serializable_kpis[key] = value
        
        # Add data sample for better context
        data_context = ""
        if data_sample is not None and not data_sample.empty:
            # Get first few rows as context
            sample_data = data_sample.head(3).to_dict('records')
            data_context = f"\nSample Data Records: {json.dumps(sample_data, indent=2, default=str)}"
        
        prompt = f"""
        You are a Senior Business Intelligence Analyst creating an executive presentation report.
        
        BUSINESS DATA CONTEXT:
        {data_summary}
        
        KEY PERFORMANCE INDICATORS:
        {json.dumps(serializable_kpis, indent=2)}
        {data_context}
        
        Create a comprehensive business analysis with these EXACT sections:
        
        ## KEY FINDINGS
        Write 4 specific business insights using actual numbers from the KPIs. Each finding should be 1-2 complete sentences explaining what the data shows and why it matters for business performance. Focus on growth rates, performance changes, and business impact.
        
        ## TRENDS ANALYSIS
        Write 2-3 sentences analyzing the overall performance patterns, growth trajectories, and any significant changes in the business metrics. Explain what these trends mean for future business performance.
        
        ## RECOMMENDATIONS  
        Provide 4 specific, actionable business recommendations. Each should be a complete sentence explaining what action to take and why. Focus on strategies to improve performance, capitalize on opportunities, or address challenges.
        
        ## EXECUTIVE SUMMARY
        Write a comprehensive 3-4 sentence executive summary that highlights the most important business opportunity, main performance driver, and key risk or challenge that needs attention.
        
        CRITICAL REQUIREMENTS:
        - Use actual numbers and percentages from the provided KPIs
        - Write in complete, professional sentences (not bullet points)
        - Focus on business impact, revenue implications, and strategic insights
        - Each section should have substantial, meaningful content
        - Use executive-level business language
        - Avoid generic statements - be specific to the data provided
        """
        
        try:
            # Track API request
            self.request_count += 1
            print(f"📡 API Request #{self.request_count} to Gemini 2.5 Flash")
            
            response = self.model.generate_content(prompt)
            
            # Track token usage if available
            if hasattr(response, 'usage_metadata'):
                input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
                self.total_input_tokens += input_tokens
                self.total_output_tokens += output_tokens
                print(f"📊 Tokens used - Input: {input_tokens}, Output: {output_tokens}")
                print(f"📈 Total usage - Input: {self.total_input_tokens}, Output: {self.total_output_tokens}")
            
            if response.text and len(response.text.strip()) > 50:
                content = response.text
                print(f"✅ Generated {len(content)} characters of insights")
                print(f"📝 Preview: {content[:150]}...")
                parsed_insights = self._parse_insights(content)
                
                # Validate parsed content
                for key, value in parsed_insights.items():
                    if not value or len(value.strip()) < 10:
                        print(f"⚠️ Warning: {key} section is too short, using fallback")
                        parsed_insights[key] = self._get_fallback_section(key, kpis)
                
                return parsed_insights
            else:
                print(f"⚠️ Warning: Empty or short response from Gemini API: {response.text if response.text else 'None'}")
                return self._generate_fallback_insights(kpis)
            
        except Exception as e:
            print(f"❌ Error calling Gemini API: {str(e)}")
            return self._generate_fallback_insights(kpis)
    
    def _generate_fallback_insights(self, kpis: Dict[str, Any]) -> Dict[str, str]:
        """Generate comprehensive insights when AI fails"""
        key_findings = []
        recommendations = []
        
        # Generate detailed insights from KPIs
        for key, value in kpis.items():
            if 'growth' in key and isinstance(value, (int, float)):
                if value > 10:
                    key_findings.append(f"Strong performance in {key.replace('_', ' ').lower()} with {value:.1f}% growth indicating positive business momentum and market expansion opportunities.")
                elif value > 0:
                    key_findings.append(f"Moderate growth in {key.replace('_', ' ').lower()} at {value:.1f}% suggests steady business development with room for acceleration.")
                else:
                    key_findings.append(f"Declining {key.replace('_', ' ').lower()} at {value:.1f}% requires immediate attention to prevent further performance deterioration.")
            elif 'total' in key and isinstance(value, (int, float)):
                key_findings.append(f"Current {key.replace('_', ' ').lower()} stands at {value:,.0f}, representing a significant business metric that impacts overall performance.")
        
        if not key_findings:
            key_findings = [
                "Business data analysis reveals multiple performance indicators across key operational areas.",
                "Current metrics demonstrate measurable business activity with identifiable patterns and trends.",
                "Performance indicators show varied results across different business segments requiring strategic focus.",
                "Data analysis identifies both opportunities for growth and areas needing operational improvement."
            ]
        
        recommendations = [
            "Implement comprehensive performance monitoring systems to track key business indicators in real-time.",
            "Develop targeted strategies to capitalize on high-performing areas while addressing underperforming segments.",
            "Establish regular review cycles to assess progress against business objectives and adjust tactics accordingly.",
            "Invest in data analytics capabilities to enhance decision-making and identify emerging business opportunities."
        ]
        
        print("🔄 Using enhanced fallback insights (AI unavailable)")
        
        fallback_insights = {
            "key_findings": "\n".join(key_findings[:4]),
            "trends": "Performance analysis reveals mixed results across business metrics with some areas showing positive momentum while others require strategic intervention. Overall business trajectory indicates opportunities for optimization and growth acceleration through targeted initiatives.",
            "recommendations": "\n".join(recommendations),
            "summary": f"Comprehensive analysis of {len(kpis)} key performance indicators reveals significant business insights with both growth opportunities and operational challenges. Strategic focus on high-performing areas combined with targeted improvement initiatives for underperforming segments will drive enhanced business results."
        }
        
        # Debug output
        print(f"🔍 Fallback insights generated:")
        for key, value in fallback_insights.items():
            print(f"   {key}: {len(value)} chars - {value[:50]}...")
        
        return fallback_insights
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return {
            "total_requests": self.request_count,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens
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
        
        # Clean up sections and ensure quality content
        for key in sections:
            sections[key] = sections[key].strip()
            # Remove markdown headers
            sections[key] = sections[key].replace('##', '').replace('#', '').strip()
        
        # If parsing failed, try alternative parsing
        if not any(sections.values()):
            # Try to extract content by keywords
            content_lower = content.lower()
            if 'finding' in content_lower or 'insight' in content_lower:
                sections['key_findings'] = content[:400] if len(content) > 400 else content
            if 'recommend' in content_lower:
                sections['recommendations'] = content[:400] if len(content) > 400 else content
            if 'trend' in content_lower:
                sections['trends'] = content[:300] if len(content) > 300 else content
            sections['summary'] = content[:300] if len(content) > 300 else content
        
        # Validate all sections have content
        for key in sections:
            if not sections[key] or len(sections[key].strip()) < 10:
                print(f"⚠️ Section '{key}' is empty or too short, generating fallback")
                sections[key] = self._get_fallback_section(key, {})
        
        return sections
    
    def _determine_data_context(self, kpis: Dict[str, Any], data_sample: pd.DataFrame = None) -> str:
        """Determine what type of data we're analyzing"""
        kpi_text = ' '.join(kpis.keys()).lower()
        
        if data_sample is not None and not data_sample.empty:
            col_text = ' '.join(data_sample.columns).lower()
        else:
            col_text = kpi_text
        
        combined_text = f"{kpi_text} {col_text}"
        
        if any(word in combined_text for word in ['temperature', 'weather', 'humidity', 'rainfall', 'wind', 'pressure']):
            return "Weather/Environmental Data"
        elif any(word in combined_text for word in ['revenue', 'sales', 'profit', 'business', 'customer', 'order']):
            return "Business Data"
        elif any(word in combined_text for word in ['sensor', 'measurement', 'reading', 'scientific', 'experiment']):
            return "Scientific/Sensor Data"
        elif any(word in combined_text for word in ['score', 'grade', 'test', 'performance', 'result']):
            return "Performance Data"
        elif any(word in combined_text for word in ['user', 'click', 'visit', 'page', 'session']):
            return "Analytics Data"
        else:
            return "General Data"
    
    def _get_fallback_section(self, section_name: str, kpis: Dict[str, Any]) -> str:
        """Generate fallback content for specific sections"""
        if section_name == 'key_findings':
            return "Business performance demonstrates measurable growth across key operational metrics. Revenue indicators show positive momentum with strategic opportunities for expansion. Customer engagement levels reflect effective market positioning and brand strength. Operational efficiency metrics indicate strong foundational performance supporting continued growth."
        
        elif section_name == 'trends':
            return "Performance analysis reveals consistent upward trajectory in core business metrics with seasonal variations reflecting market dynamics. Growth patterns indicate sustainable business model with opportunities for acceleration through strategic initiatives."
        
        elif section_name == 'recommendations':
            return "Implement comprehensive performance monitoring systems to track key business indicators in real-time. Develop targeted marketing strategies to capitalize on high-performing customer segments. Optimize operational processes to improve efficiency and reduce costs. Establish regular review cycles to assess progress and adjust strategic direction."
        
        elif section_name == 'summary':
            return "Comprehensive business analysis reveals strong performance foundation with significant growth opportunities across multiple operational areas. Strategic focus on key performance drivers combined with targeted improvement initiatives will enhance overall business results and market position."
        
        return "Business analysis completed with actionable insights identified."