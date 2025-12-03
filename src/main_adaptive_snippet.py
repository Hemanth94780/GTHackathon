"""
MODIFIED SNIPPET FOR main.py - Integration of Adaptive Analysis Engine

Replace the KPI calculation section (Step 2) in your existing main.py with this:
"""

# Add these imports at the top of main.py
from schema import SchemaDetector
from llm_planner import LLMPlanner
from analysis_modules import AnalysisRouter

class AutomatedInsightEngine:
    def __init__(self, openai_api_key: str):
        self.data_processor = DataProcessor()
        self.insight_generator = InsightGenerator(openai_api_key)
        self.report_generator = ReportGenerator()
        
        # ADD THESE NEW COMPONENTS
        self.schema_detector = SchemaDetector()
        self.llm_planner = LLMPlanner(openai_api_key)
        self.analysis_router = AnalysisRouter()
    
    def process_and_generate_report(self, data_files: list, output_filename: str = None, format_type: str = "pptx"):
        """Main pipeline with adaptive analysis"""
        
        print("🔄 Processing data files...")
        # Step 1: Ingest and clean data from multiple formats
        data = self._ingest_mixed_files(data_files)
        print(f"✅ Processed {len(data)} records from {len(data_files)} files")
        print(f"📊 Data columns: {list(data.columns)}")
        
        # Generate filename based on input if not provided
        if output_filename is None:
            output_filename = self._generate_filename(data_files, data, format_type)
        
        # REPLACE STEP 2 WITH ADAPTIVE ANALYSIS:
        print("🔍 Detecting data schema...")
        schema = self.schema_detector.detect_schema(data, data_files[0] if data_files else "")
        
        print("🤖 Creating analysis plan...")
        analysis_plan = self.llm_planner.create_analysis_plan(schema)
        print(f"📋 Dataset classified as: {analysis_plan['dataset_type']}")
        print(f"📊 Planned KPIs: {analysis_plan['kpis']}")
        
        print("⚙️ Executing adaptive analysis...")
        kpis = self.analysis_router.execute_analysis(data, analysis_plan)
        print(f"✅ Generated {len(kpis)} KPIs: {list(kpis.keys())}")
        
        # Step 3: Generate data summary (UNCHANGED)
        data_summary = f"Dataset contains {len(data)} records with {len(data.columns)} columns. "
        data_summary += f"Date range: {data.index[0]} to {data.index[-1]}. " if 'date' in data.columns else ""
        
        # REST OF THE PIPELINE REMAINS UNCHANGED...
        print("🤖 Generating AI insights...")
        insights = self.insight_generator.generate_insights(kpis, data_summary, data.head(5) if len(data) > 0 else None)
        
        print(f"📄 Creating {format_type.upper()} report...")
        os.makedirs("output", exist_ok=True)
        output_path = f"output/{output_filename}"
        if format_type == "pdf":
            self.report_generator.create_pdf_report(kpis, insights, data, output_path)
        else:
            self.report_generator.create_powerpoint_report(kpis, insights, data, output_path)
        
        print(f"✅ Report generated: {output_path}")
        
        # Display API usage statistics
        usage_stats = self.insight_generator.get_usage_stats()
        print("\n📈 API Usage Summary:")
        print(f"   Total Requests: {usage_stats['total_requests']}")
        print(f"   Input Tokens: {usage_stats['total_input_tokens']:,}")
        print(f"   Output Tokens: {usage_stats['total_output_tokens']:,}")
        print(f"   Total Tokens: {usage_stats['total_tokens']:,}")
        
        return output_path