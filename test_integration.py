"""
Test script to verify AI integration and unique file naming
"""
import os
import sys
sys.path.append('src')

from main import AutomatedInsightEngine
from dotenv import load_dotenv

load_dotenv()

def test_ai_integration():
    """Test the complete AI-driven pipeline"""
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == 'your-api-key-here':
        print("❌ Please set GOOGLE_API_KEY in .env file")
        return
    
    # Initialize engine
    engine = AutomatedInsightEngine(api_key)
    
    # Test with sample data files
    test_files = [
        "data/sample_data.csv"  # Add your test files here
    ]
    
    print("🚀 Testing AI-driven analysis pipeline...")
    
    try:
        # Run pipeline
        report_path = engine.process_and_generate_report(test_files, format_type="pptx")
        print(f"✅ Success! Report generated: {report_path}")
        
        # Check if charts were created with unique names
        charts_dir = "charts"
        if os.path.exists(charts_dir):
            chart_files = os.listdir(charts_dir)
            print(f"📊 Charts created: {len(chart_files)}")
            for chart in chart_files:
                print(f"   - {chart}")
        
        # Test PDF generation
        pdf_path = engine.process_and_generate_report(test_files, format_type="pdf")
        print(f"✅ PDF generated: {pdf_path}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_integration()