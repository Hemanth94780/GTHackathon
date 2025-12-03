from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict, Any
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class ReportGenerator:
    def __init__(self):
        self.prs = Presentation()
        
    def create_powerpoint_report(self, kpis: Dict[str, Any], insights: Dict[str, str], 
                                data: pd.DataFrame, output_path: str):
        """Generate complete PowerPoint report"""
        
        # Title slide
        self._add_title_slide("Weekly Performance Report", "Automated Insight Engine")
        
        # Executive summary
        self._add_text_slide("Executive Summary", insights.get('summary', 'Analysis completed'))
        
        # Key findings
        self._add_bullet_slide("Key Findings", insights.get('key_findings', 'No findings available'))
        
        # KPIs slide
        self._add_kpi_slide(kpis)
        
        # Charts slide
        chart_path = self._create_charts(data)
        if chart_path:
            self._add_chart_slide("Performance Trends", chart_path)
        
        # Recommendations
        self._add_bullet_slide("Recommendations", insights.get('recommendations', 'Continue monitoring'))
        
        self.prs.save(output_path)
        
        # Cleanup
        if chart_path and os.path.exists(chart_path):
            os.remove(chart_path)
    
    def _add_title_slide(self, title: str, subtitle: str):
        """Add title slide"""
        slide_layout = self.prs.slide_layouts[0]
        slide = self.prs.slides.add_slide(slide_layout)
        
        title_shape = slide.shapes.title
        subtitle_shape = slide.placeholders[1]
        
        title_shape.text = title
        subtitle_shape.text = subtitle
    
    def _add_text_slide(self, title: str, content: str):
        """Add text content slide"""
        slide_layout = self.prs.slide_layouts[1]
        slide = self.prs.slides.add_slide(slide_layout)
        
        title_shape = slide.shapes.title
        content_shape = slide.placeholders[1]
        
        title_shape.text = title
        content_shape.text = content
    
    def _add_bullet_slide(self, title: str, content: str):
        """Add bullet point slide"""
        slide_layout = self.prs.slide_layouts[1]
        slide = self.prs.slides.add_slide(slide_layout)
        
        title_shape = slide.shapes.title
        content_shape = slide.placeholders[1]
        
        title_shape.text = title
        
        # Format as bullet points
        text_frame = content_shape.text_frame
        text_frame.clear()
        
        for line in content.split('\n'):
            if line.strip():
                p = text_frame.add_paragraph()
                p.text = line.strip()
                p.level = 0
    
    def _add_kpi_slide(self, kpis: Dict[str, Any]):
        """Add KPI summary slide"""
        slide_layout = self.prs.slide_layouts[1]
        slide = self.prs.slides.add_slide(slide_layout)
        
        title_shape = slide.shapes.title
        title_shape.text = "Key Performance Indicators"
        
        content_shape = slide.placeholders[1]
        text_frame = content_shape.text_frame
        text_frame.clear()
        
        for key, value in list(kpis.items())[:6]:  # Limit to 6 KPIs
            p = text_frame.add_paragraph()
            p.text = f"{key.replace('_', ' ').title()}: {value:.2f}" if isinstance(value, float) else f"{key.replace('_', ' ').title()}: {value}"
            p.level = 0
    
    def _create_charts(self, data: pd.DataFrame) -> str:
        """Create visualization charts"""
        try:
            numeric_cols = data.select_dtypes(include=['number']).columns[:3]  # Max 3 charts
            
            if len(numeric_cols) == 0:
                return None
                
            fig, axes = plt.subplots(1, len(numeric_cols), figsize=(15, 5))
            if len(numeric_cols) == 1:
                axes = [axes]
            
            for i, col in enumerate(numeric_cols):
                axes[i].plot(data[col])
                axes[i].set_title(f'{col.replace("_", " ").title()} Trend')
                axes[i].set_xlabel('Index')
                axes[i].set_ylabel(col)
            
            plt.tight_layout()
            chart_path = 'temp_chart.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            return None
    
    def _add_chart_slide(self, title: str, chart_path: str):
        """Add slide with chart image"""
        slide_layout = self.prs.slide_layouts[5]  # Blank layout
        slide = self.prs.slides.add_slide(slide_layout)
        
        # Add title
        title_shape = slide.shapes.add_textbox(Inches(1), Inches(0.5), Inches(8), Inches(1))
        title_frame = title_shape.text_frame
        title_frame.text = title
        
        # Add chart
        slide.shapes.add_picture(chart_path, Inches(1), Inches(1.5), Inches(8), Inches(5))
    
    def create_pdf_report(self, kpis: Dict[str, Any], insights: Dict[str, str], 
                         data: pd.DataFrame, output_path: str):
        """Generate PDF report"""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30)
        story.append(Paragraph("Weekly Performance Report", title_style))
        story.append(Spacer(1, 12))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Paragraph(insights.get('summary', 'Analysis completed'), styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Key Findings
        story.append(Paragraph("Key Findings", styles['Heading2']))
        story.append(Paragraph(insights.get('key_findings', 'No findings available'), styles['Normal']))
        story.append(Spacer(1, 12))
        
        # KPIs
        story.append(Paragraph("Key Performance Indicators", styles['Heading2']))
        for key, value in list(kpis.items())[:6]:
            kpi_text = f"{key.replace('_', ' ').title()}: {value:.2f}" if isinstance(value, float) else f"{key.replace('_', ' ').title()}: {value}"
            story.append(Paragraph(f"• {kpi_text}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Chart
        chart_path = self._create_charts(data)
        if chart_path and os.path.exists(chart_path):
            story.append(Paragraph("Performance Trends", styles['Heading2']))
            story.append(Image(chart_path, width=6*inch, height=2*inch))
            story.append(Spacer(1, 12))
            os.remove(chart_path)
        
        # Recommendations
        story.append(Paragraph("Recommendations", styles['Heading2']))
        story.append(Paragraph(insights.get('recommendations', 'Continue monitoring'), styles['Normal']))
        
        doc.build(story)