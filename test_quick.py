"""
Quick test of the separated AI system
"""
import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

# Load environment variables
load_dotenv()

def test_quick():
    """Quick test of the main pipeline"""
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ No GOOGLE_API_KEY found")
        return
    
    print("🧪 Quick Test - Separated AI Analysis")
    print("=" * 40)
    
    # Create simple test data
    test_data = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'revenue': [1000, 1200, 1100],
        'customers': [50, 60, 55]
    })
    
    try:
        # Test the main pipeline
        from main import AutomatedInsightEngine
        
        engine = AutomatedInsightEngine(api_key)
        
        # Create test CSV file
        os.makedirs('data', exist_ok=True)
        test_data.to_csv('data/test.csv', index=False)
        
        # Run pipeline
        report_path = engine.process_and_generate_report(['data/test.csv'], format_type="pptx")
        
        print(f"✅ Test completed! Report: {report_path}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_quick()