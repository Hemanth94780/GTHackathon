"""
Schema Detection Module - Extracts metadata from CSV/JSON files
"""
import pandas as pd
import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SchemaDetector:
    """Detects and extracts schema metadata from data files"""
    
    def detect_schema(self, df: pd.DataFrame, file_path: str = "") -> Dict[str, Any]:
        """
        Extract schema metadata from DataFrame
        
        Args:
            df: Pandas DataFrame
            file_path: Original file path for reference
            
        Returns:
            Schema metadata dictionary
        """
        try:
            schema = {
                "file_path": file_path,
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": list(df.columns),
                "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "sample_rows": df.head(5).to_dict('records'),
                "numeric_columns": list(df.select_dtypes(include=['number']).columns),
                "categorical_columns": list(df.select_dtypes(include=['object']).columns),
                "null_counts": df.isnull().sum().to_dict()
            }
            
            logger.info(f"Schema detected: {len(df)} rows, {len(df.columns)} columns")
            return schema
            
        except Exception as e:
            logger.error(f"Schema detection failed: {str(e)}")
            raise