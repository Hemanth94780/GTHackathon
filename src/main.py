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
    
    def process_and_generate_report(self, data_files: list, output_filename: str = None, format_type: str = "pptx"):
        """Main pipeline: ingest -> process -> analyze -> generate report"""
        
        print("🔄 Processing data files...")
        # Step 1: Ingest and clean data from multiple formats
        data = self._ingest_mixed_files(data_files)
        print(f"✅ Processed {len(data)} records from {len(data_files)} files")
        print(f"📊 Data columns: {list(data.columns)}")
        
        # Generate filename based on input if not provided
        if output_filename is None:
            output_filename = self._generate_filename(data_files, data, format_type)
        
        # Step 2: Calculate KPIs
        kpis = self.data_processor.calculate_kpis(data)
        print(f"📊 Generated {len(kpis)} KPIs: {list(kpis.keys())}")
        if len(kpis) == 0:
            print("⚠️ Warning: No KPIs generated - check your data format")
        
        # Step 3: Generate data summary
        data_summary = f"Dataset contains {len(data)} records with {len(data.columns)} columns. "
        data_summary += f"Date range: {data.index[0]} to {data.index[-1]}. " if 'date' in data.columns else ""
        
        print("🤖 Generating AI insights...")
        # Step 4: Generate insights with data sample
        insights = self.insight_generator.generate_insights(kpis, data_summary, data.head(5) if len(data) > 0 else None)
        
        print(f"📄 Creating {format_type.upper()} report...")
        # Step 5: Generate report
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
    
    def _ingest_mixed_files(self, file_paths: list) -> pd.DataFrame:
        """Ingest files of different formats (CSV, JSON)"""
        dataframes = []
        
        for file_path in file_paths:
            try:
                if file_path.lower().endswith('.json'):
                    print(f"📄 Processing JSON file: {file_path}")
                    df = self.data_processor.ingest_json_files([file_path])
                elif file_path.lower().endswith('.csv'):
                    print(f"📄 Processing CSV file: {file_path}")
                    df = self.data_processor.ingest_csv_files([file_path])
                else:
                    print(f"⚠️ Unsupported file format: {file_path}")
                    continue
                
                if not df.empty:
                    dataframes.append(df)
                    print(f"✅ Successfully loaded {len(df)} records from {file_path}")
                else:
                    print(f"⚠️ No data found in {file_path}")
                    
            except Exception as e:
                print(f"❌ Error processing {file_path}: {str(e)}")
                continue
        
        if dataframes:
            combined_df = pd.concat(dataframes, ignore_index=True)
            print(f"🔄 Combined {len(dataframes)} files into {len(combined_df)} total records")
            return combined_df
        else:
            print("❌ No valid data files found, creating sample data")
            return self._create_sample_dataframe()
    
    def _generate_filename(self, file_paths: list, data: pd.DataFrame, format_type: str) -> str:
        """Generate filename: {input_name}_report_{date}.{format}"""
        from datetime import datetime
        
        if not file_paths:
            base_name = "data"
        else:
            # Get base name from first file
            first_file = os.path.basename(file_paths[0])
            base_name = os.path.splitext(first_file)[0]
        
        # Clean base name
        clean_base = base_name.replace('_', '-').replace(' ', '-').lower()
        
        # Generate date string
        date_str = datetime.now().strftime('%Y%m%d')
        
        # Format: {input_name}_report_{date}.{format}
        filename = f"{clean_base}_report_{date_str}.{format_type}"
        
        print(f"📝 Generated filename: {filename}")
        return filename
    
    def _create_sample_dataframe(self) -> pd.DataFrame:
        """Create sample data when no valid files are found"""
        import numpy as np
        from datetime import datetime, timedelta
        
        dates = [datetime.now() - timedelta(days=x) for x in range(10, 0, -1)]
        
        return pd.DataFrame({
            'date': dates,
            'revenue': np.random.randint(1000, 5000, 10),
            'customers': np.random.randint(50, 200, 10),
            'orders': np.random.randint(20, 100, 10)
        })

def main():
    # Configuration
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'your-api-key-here')
    
    if GOOGLE_API_KEY == 'your-api-key-here':
        print("⚠️  Please set your GOOGLE_API_KEY environment variable")
        print("   Example: set GOOGLE_API_KEY=your-key-here")
        return
    
    # Initialize engine
    engine = AutomatedInsightEngine(GOOGLE_API_KEY)
    
    # Sample data files (supports CSV and JSON)
    data_files = [
        "../data/sample_data.csv",  # CSV files
        "../data/sample_data.json"  # JSON files
    ]
    
    # Check if sample data exists, create if not
    if not os.path.exists("../data/sample_data.csv"):
        create_sample_data()
    
    try:
        # Run the pipeline
        report_path = engine.process_and_generate_report(data_files)
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