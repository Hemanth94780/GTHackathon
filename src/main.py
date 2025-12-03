import os
import sys
from dotenv import load_dotenv
from data_processor import DataProcessor
from insight_generator import InsightGenerator
from report_generator import ReportGenerator
import pandas as pd

# Load environment variables from .env file
load_dotenv()

class AutomatedInsightEngine:
    def __init__(self, openai_api_key: str):
        self.data_processor = DataProcessor()
        self.insight_generator = InsightGenerator(openai_api_key)
        self.report_generator = ReportGenerator()
    
    def process_and_generate_report(self, csv_files: list, output_filename: str = "weekly_report.pptx", format_type: str = "pptx"):
        """Main pipeline: ingest -> process -> analyze -> generate report"""
        
        print("🔄 Processing data files...")
        # Step 1: Ingest and clean data
        data = self.data_processor.ingest_csv_files(csv_files)
        print(f"✅ Processed {len(data)} records from {len(csv_files)} files")
        
        # Step 2: Calculate KPIs
        kpis = self.data_processor.calculate_kpis(data)
        print(f"📊 Generated {len(kpis)} KPIs")
        
        # Step 3: Generate data summary
        data_summary = f"Dataset contains {len(data)} records with {len(data.columns)} columns. "
        data_summary += f"Date range: {data.index[0]} to {data.index[-1]}. " if 'date' in data.columns else ""
        
        print("🤖 Generating AI insights...")
        # Step 4: Generate insights
        insights = self.insight_generator.generate_insights(kpis, data_summary)
        
        print(f"📄 Creating {format_type.upper()} report...")
        # Step 5: Generate report
        output_path = f"../output/{output_filename}"
        if format_type == "pdf":
            self.report_generator.create_pdf_report(kpis, insights, data, output_path)
        else:
            self.report_generator.create_powerpoint_report(kpis, insights, data, output_path)
        
        print(f"✅ Report generated: {output_path}")
        return output_path

def main():
    # Configuration
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'your-api-key-here')
    
    if GOOGLE_API_KEY == 'your-api-key-here':
        print("⚠️  Please set your GOOGLE_API_KEY environment variable")
        print("   Example: set GOOGLE_API_KEY=your-key-here")
        return
    
    # Initialize engine
    engine = AutomatedInsightEngine(GOOGLE_API_KEY)
    
    # Sample data files (you can modify this)
    csv_files = [
        "../data/sample_data.csv"  # Add your CSV files here
    ]
    
    # Check if sample data exists, create if not
    if not os.path.exists("../data/sample_data.csv"):
        create_sample_data()
    
    try:
        # Run the pipeline
        report_path = engine.process_and_generate_report(csv_files)
        print(f"\n🎉 Success! Report saved to: {report_path}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def create_sample_data():
    """Create sample data for demonstration"""
    import numpy as np
    from datetime import datetime, timedelta
    
    # Create sample footfall and ad data
    dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
    
    sample_data = pd.DataFrame({
        'date': dates,
        'footfall': np.random.randint(100, 500, 30),
        'ad_clicks': np.random.randint(50, 200, 30),
        'impressions': np.random.randint(1000, 5000, 30),
        'weather_temp': np.random.randint(15, 35, 30),
        'sales': np.random.randint(1000, 10000, 30)
    })
    
    os.makedirs("../data", exist_ok=True)
    sample_data.to_csv("../data/sample_data.csv", index=False)
    print("📝 Created sample data file")

if __name__ == "__main__":
    main()