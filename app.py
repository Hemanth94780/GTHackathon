import streamlit as st
import os
import sys
sys.path.append('src')

from src.main import AutomatedInsightEngine
import pandas as pd

st.set_page_config(page_title="Automated Insight Engine", page_icon="📊", layout="wide")

st.title("🚀 Automated Insight Engine")
st.markdown("Upload your CSV/JSON files and generate AI-powered reports automatically!")

# Sidebar for configuration
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Google API Key", type="password", help="Enter your Google Gemini API key")
output_format = st.sidebar.selectbox("Output Format", ["PowerPoint (.pptx)", "PDF (.pdf)"], help="Choose report format")

# File upload
st.header("📁 Upload Data Files")
uploaded_files = st.file_uploader("Choose CSV or JSON files", accept_multiple_files=True, type=['csv', 'json'])

if uploaded_files and api_key:
    # Save uploaded files temporarily
    temp_files = []
    for uploaded_file in uploaded_files:
        temp_path = f"data/{uploaded_file.name}"
        os.makedirs("data", exist_ok=True)
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        temp_files.append(temp_path)
        
        # Show preview
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(temp_path)
        elif uploaded_file.name.endswith('.json'):
            import json
            with open(temp_path, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data) if isinstance(data, list) else pd.json_normalize(data)
        
        st.subheader(f"Preview: {uploaded_file.name}")
        st.dataframe(df.head())
    
    # Generate report button
    if st.button("🎯 Generate Report", type="primary"):
        try:
            with st.spinner("Processing data and generating insights..."):
                # Initialize engine
                engine = AutomatedInsightEngine(api_key)
                
                # Generate report
                if "PDF" in output_format:
                    report_path = engine.process_and_generate_report(temp_files, "automated_report.pdf", format_type="pdf")
                    file_ext = "pdf"
                    mime_type = "application/pdf"
                else:
                    report_path = engine.process_and_generate_report(temp_files, "automated_report.pptx", format_type="pptx")
                    file_ext = "pptx"
                    mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                
                st.success("✅ Report generated successfully!")
                
                # Download button
                with open(report_path, "rb") as file:
                    st.download_button(
                        label=f"📥 Download {output_format.split()[0]} Report",
                        data=file.read(),
                        file_name=f"automated_report.{file_ext}",
                        mime=mime_type
                    )
                    
        except Exception as e:
            st.error(f"❌ Error generating report: {str(e)}")
            
        finally:
            # Cleanup temp files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

elif not api_key:
    st.warning("⚠️ Please enter your Google API key in the sidebar")
elif not uploaded_files:
    st.info("📤 Please upload CSV or JSON files to get started")

# Instructions
st.header("📋 How to Use")
st.markdown("""
1. **Enter API Key**: Add your Google Gemini API key in the sidebar
2. **Upload Files**: Upload one or more CSV/JSON files with your data
3. **Generate Report**: Click the generate button to create your automated report
4. **Download**: Download the generated PowerPoint presentation

**Sample Data Format:**
Your CSV/JSON files should contain columns like:
- `date`, `footfall`, `ad_clicks`, `impressions`, `sales`, `weather_temp`, etc.
""")

# Footer
st.markdown("---")
st.markdown("Built for GroundTruth AI Hackathon | Automated Insight Engine v1.0")