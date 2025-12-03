import pandas as pd
import numpy as np
from typing import List, Dict, Any
import sqlite3
from pymongo import MongoClient
import json

class DataProcessor:
    def __init__(self):
        self.processed_data = None
        
    def ingest_csv_files(self, file_paths: List[str]) -> pd.DataFrame:
        """Ingest and merge multiple CSV files"""
        dataframes = []
        for path in file_paths:
            df = pd.read_csv(path)
            df['source_file'] = path.split('/')[-1]
            dataframes.append(df)
        
        # Simple concatenation - can be enhanced with joins
        combined_df = pd.concat(dataframes, ignore_index=True)
        return self.clean_data(combined_df)
    
    def ingest_json_files(self, file_paths: List[str]) -> pd.DataFrame:
        """Ingest and merge multiple JSON files"""
        dataframes = []
        for path in file_paths:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.json_normalize(data)
            else:
                continue
                
            df['source_file'] = path.split('/')[-1]
            dataframes.append(df)
        
        if dataframes:
            combined_df = pd.concat(dataframes, ignore_index=True)
            return self.clean_data(combined_df)
        return pd.DataFrame()
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Basic data cleaning"""
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        
        # Fill categorical nulls
        categorical_cols = df.select_dtypes(include=['object']).columns
        df[categorical_cols] = df[categorical_cols].fillna('Unknown')
        
        self.processed_data = df
        return df
    
    def calculate_kpis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate key performance indicators"""
        kpis = {}
        
        # Basic statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            kpis[f'{col}_mean'] = df[col].mean()
            kpis[f'{col}_total'] = df[col].sum()
            kpis[f'{col}_growth'] = ((df[col].iloc[-1] - df[col].iloc[0]) / df[col].iloc[0] * 100) if len(df) > 1 else 0
        
        return kpis
    
    def ingest_sql_data(self, connection_string: str, query: str) -> pd.DataFrame:
        """Ingest data from SQL database"""
        try:
            conn = sqlite3.connect(connection_string)
            df = pd.read_sql_query(query, conn)
            conn.close()
            return self.clean_data(df)
        except Exception as e:
            print(f"SQL Error: {e}")
            return pd.DataFrame()
    
    def ingest_mongodb_data(self, connection_string: str, database: str, collection: str, query: dict = {}) -> pd.DataFrame:
        """Ingest data from MongoDB"""
        try:
            client = MongoClient(connection_string)
            db = client[database]
            coll = db[collection]
            data = list(coll.find(query))
            client.close()
            df = pd.DataFrame(data)
            return self.clean_data(df)
        except Exception as e:
            print(f"MongoDB Error: {e}")
            return pd.DataFrame()
    
    def ingest_mixed_sources(self, sources: List[Dict[str, Any]]) -> pd.DataFrame:
        """Ingest from multiple source types"""
        dataframes = []
        
        for source in sources:
            if source['type'] == 'csv':
                df = pd.read_csv(source['path'])
            elif source['type'] == 'json':
                df = self.ingest_json_files([source['path']])
            elif source['type'] == 'sql':
                df = self.ingest_sql_data(source['connection'], source['query'])
            elif source['type'] == 'mongodb':
                df = self.ingest_mongodb_data(source['connection'], source['database'], source['collection'], source.get('query', {}))
            else:
                continue
                
            df['source_type'] = source['type']
            dataframes.append(df)
        
        if dataframes:
            combined_df = pd.concat(dataframes, ignore_index=True)
            return self.clean_data(combined_df)
        return pd.DataFrame()