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
        """Ingest and merge multiple CSV files with robust error handling"""
        dataframes = []
        for path in file_paths:
            try:
                # Try different CSV parsing options
                df = pd.read_csv(path, encoding='utf-8', on_bad_lines='skip')
            except:
                try:
                    # Try with different separator
                    df = pd.read_csv(path, sep=';', encoding='utf-8', on_bad_lines='skip')
                except:
                    try:
                        # Try with tab separator
                        df = pd.read_csv(path, sep='\t', encoding='utf-8', on_bad_lines='skip')
                    except:
                        # Skip problematic files
                        print(f"Warning: Could not parse {path}, skipping...")
                        continue
            
            if not df.empty:
                df['source_file'] = path.split('/')[-1]
                dataframes.append(df)
        
        if dataframes:
            combined_df = pd.concat(dataframes, ignore_index=True)
            return self.clean_data(combined_df)
        else:
            # Return empty DataFrame with basic structure
            return pd.DataFrame({'date': [], 'value': []})
    
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
        """Calculate relevant business KPIs"""
        kpis = {}
        
        if df.empty:
            return kpis
        
        # Filter relevant numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        business_cols = self._filter_business_columns(numeric_cols)
        
        for col in business_cols:
            col_data = df[col].dropna()
            if len(col_data) == 0:
                continue
                
            # Calculate meaningful business metrics
            mean_val = col_data.mean()
            total_val = col_data.sum()
            max_val = col_data.max()
            
            # Growth calculation (if we have time series data)
            if len(col_data) > 1:
                first_val = col_data.iloc[0]
                last_val = col_data.iloc[-1]
                if first_val != 0:
                    growth_val = ((last_val - first_val) / abs(first_val)) * 100
                else:
                    growth_val = 0
            else:
                growth_val = 0
            
            # Add KPIs based on column type
            col_lower = col.lower()
            
            # Revenue/Sales metrics
            if any(word in col_lower for word in ['revenue', 'sales', 'profit']):
                kpis[f'total_{col}'] = float(total_val)
                kpis[f'avg_{col}'] = float(mean_val)
                if growth_val != 0:
                    kpis[f'{col}_growth_rate'] = float(growth_val)
            
            # Count/Volume metrics
            elif any(word in col_lower for word in ['count', 'orders', 'customers', 'visits', 'clicks']):
                kpis[f'total_{col}'] = float(total_val)
                kpis[f'peak_{col}'] = float(max_val)
                if growth_val != 0:
                    kpis[f'{col}_growth_rate'] = float(growth_val)
            
            # Rate/Percentage metrics
            elif any(word in col_lower for word in ['rate', 'conversion', 'engagement']):
                kpis[f'avg_{col}'] = float(mean_val)
                kpis[f'best_{col}'] = float(max_val)
            
            # General metrics (fallback)
            else:
                if total_val > mean_val * 2:  # If total is significantly different from mean
                    kpis[f'total_{col}'] = float(total_val)
                kpis[f'avg_{col}'] = float(mean_val)
                if abs(growth_val) > 5:  # Only show significant growth
                    kpis[f'{col}_growth_rate'] = float(growth_val)
        
        # Calculate derived business metrics
        kpis.update(self._calculate_derived_metrics(df))
        
        # Remove zero or irrelevant values
        kpis = {k: v for k, v in kpis.items() if v != 0 and not pd.isna(v)}
        
        return kpis
    
    def _filter_business_columns(self, columns) -> List[str]:
        """Filter columns to focus on business-relevant metrics"""
        # Priority business keywords
        business_keywords = [
            'revenue', 'sales', 'profit', 'income', 'earnings',
            'customers', 'users', 'visitors', 'traffic',
            'orders', 'purchases', 'transactions',
            'conversion', 'rate', 'engagement',
            'clicks', 'impressions', 'views',
            'cost', 'spend', 'budget',
            'growth', 'performance'
        ]
        
        # Skip technical/irrelevant columns
        skip_keywords = [
            'id', 'index', 'timestamp', 'date', 'time',
            'temp', 'weather', 'debug', 'test', 'sample',
            'latitude', 'longitude', 'coordinates'
        ]
        
        business_cols = []
        
        # First pass: Add columns with business keywords
        for col in columns:
            col_lower = col.lower()
            if (any(keyword in col_lower for keyword in business_keywords) and
                not any(skip in col_lower for skip in skip_keywords)):
                business_cols.append(col)
        
        # Second pass: Add other numeric columns if we don't have enough
        if len(business_cols) < 3:
            for col in columns:
                col_lower = col.lower()
                if (col not in business_cols and
                    not any(skip in col_lower for skip in skip_keywords)):
                    business_cols.append(col)
                    if len(business_cols) >= 6:  # Limit to 6 main columns
                        break
        
        return business_cols[:6]  # Return top 6 business columns
    
    def _calculate_derived_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate derived business metrics"""
        derived = {}
        
        # Look for common business metric combinations
        cols = df.columns.str.lower()
        
        # Conversion rate (if we have both clicks and orders/conversions)
        if any('click' in col for col in cols) and any('order' in col or 'conversion' in col for col in cols):
            clicks_col = next((col for col in df.columns if 'click' in col.lower()), None)
            orders_col = next((col for col in df.columns if 'order' in col.lower() or 'conversion' in col.lower()), None)
            
            if clicks_col and orders_col:
                total_clicks = df[clicks_col].sum()
                total_orders = df[orders_col].sum()
                if total_clicks > 0:
                    derived['conversion_rate'] = float((total_orders / total_clicks) * 100)
        
        # Revenue per customer (if we have both)
        if any('revenue' in col or 'sales' in col for col in cols) and any('customer' in col or 'user' in col for col in cols):
            revenue_col = next((col for col in df.columns if 'revenue' in col.lower() or 'sales' in col.lower()), None)
            customer_col = next((col for col in df.columns if 'customer' in col.lower() or 'user' in col.lower()), None)
            
            if revenue_col and customer_col:
                total_revenue = df[revenue_col].sum()
                total_customers = df[customer_col].sum()
                if total_customers > 0:
                    derived['revenue_per_customer'] = float(total_revenue / total_customers)
        
        return derived
    
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
                try:
                    df = pd.read_csv(source['path'], on_bad_lines='skip')
                except:
                    continue
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