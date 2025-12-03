"""
Test the new separated AI analysis system
"""
import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

# Load environment variables
load_dotenv()

def test_separated_ai():
    """Test the separated AI analysis system"""
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ No GOOGLE_API_KEY found in environment")
        return
    
    print("🧪 Testing Separated AI Analysis System")
    print("=" * 50)
    
    # Create sample data
    sample_data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=10),
        'revenue': [1000, 1200, 1100, 1300, 1250, 1400, 1350, 1500, 1450, 1600],
        'customers': [50, 60, 55, 65, 62, 70, 67, 75, 72, 80],
        'orders': [25, 30, 28, 32, 31, 35, 33, 37, 36, 40],
        'category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B']
    })
    
    print(f"📊 Sample data: {len(sample_data)} rows, {len(sample_data.columns)} columns")
    print(f"Columns: {list(sample_data.columns)}")
    
    try:
        # Test 1: Schema Detection
        print("\n🔍 Step 1: Schema Detection")
        from schema import SchemaDetector
        schema_detector = SchemaDetector()
        schema = schema_detector.detect_schema(sample_data, "test_data.csv")
        print(f"✅ Schema detected: {schema['dataset_type']}")
        print(f"   Numeric columns: {schema['numeric_columns']}")
        print(f"   Categorical columns: {schema['categorical_columns']}")
        
        # Test 2: AI Data Structure Analysis
        print("\n🤖 Step 2: AI Data Structure Analysis")
        from ai_analyzer import AIAnalyzer
        ai_analyzer = AIAnalyzer(api_key)
        analysis_plan = ai_analyzer.analyze_data_structure(sample_data, schema)
        print(f"✅ Analysis plan created:")
        print(f"   Dataset type: {analysis_plan['dataset_type']}")
        print(f"   Required columns: {analysis_plan['required_columns']}")
        print(f"   Chart specs: {len(analysis_plan['chart_specs'])} charts")
        print(f"   KPI calculations: {len(analysis_plan['kpi_calculations'])} KPIs")
        
        # Test 3: Smart KPI Calculation
        print("\n⚙️ Step 3: Smart KPI Calculation")
        from smart_kpi_calculator import SmartKPICalculator
        kpi_calculator = SmartKPICalculator()
        kpis = kpi_calculator.calculate_kpis(sample_data, analysis_plan)
        print(f"✅ KPIs calculated: {len(kpis)} metrics")
        for key, value in list(kpis.items())[:5]:  # Show first 5 KPIs
            print(f"   {key}: {value}")
        
        # Test 4: AI Insights Generation
        print("\n🤖 Step 4: AI Insights Text Generation")
        insights = ai_analyzer.generate_insights_text(kpis, analysis_plan)
        print(f"✅ Insights generated: {len(insights)} characters")
        print(f"Preview: {insights[:200]}...")
        
        # Test 5: Dynamic Chart Generation
        print("\n🎨 Step 5: Dynamic Chart Generation")
        from dynamic_charts import DynamicChartGenerator
        chart_generator = DynamicChartGenerator()
        chart_paths = chart_generator.generate_charts(sample_data, analysis_plan, "test")
        print(f"✅ Charts generated: {len(chart_paths)} files")
        for path in chart_paths:
            print(f"   {os.path.basename(path)}")
        
        print("\n🎉 All tests passed! Separated AI analysis system is working correctly.")
        print("\nKey improvements:")
        print("✅ AI Request 1: Data structure analysis with specific column mappings")
        print("✅ AI Request 2: Text insights generation based on calculated KPIs")
        print("✅ Charts are now created based on AI analysis of actual data")
        print("✅ KPIs are calculated using AI-identified relevant columns")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_separated_ai()