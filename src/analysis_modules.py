"""
Dynamic Analysis Modules - Dataset-specific analysis engines
"""
import pandas as pd
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class AnalysisRouter:
    """Routes datasets to appropriate analysis engines"""
    
    def __init__(self):
        self.engines = {
            'ad_performance': self.analyze_ads,
            'sales_data': self.analyze_sales,
            'survey_feedback': self.analyze_survey,
            'financial_records': self.analyze_finance,
            'operations_metrics': self.analyze_operations,
            'generic_tabular': self.analyze_generic
        }
    
    def execute_analysis(self, df: pd.DataFrame, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute analysis based on dataset type
        
        Args:
            df: DataFrame to analyze
            plan: Analysis plan from LLM
            
        Returns:
            KPI results dictionary
        """
        dataset_type = plan.get('dataset_type', 'generic_tabular')
        engine = self.engines.get(dataset_type, self.analyze_generic)
        
        logger.info(f"Executing {dataset_type} analysis")
        return engine(df, plan)
    
    def analyze_ads(self, df: pd.DataFrame, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze advertising performance data"""
        kpis = {}
        
        # Standard ad metrics
        if 'clicks' in df.columns and 'impressions' in df.columns:
            kpis['ctr'] = (df['clicks'].sum() / df['impressions'].sum() * 100) if df['impressions'].sum() > 0 else 0
        
        if 'spend' in df.columns or 'cost' in df.columns:
            spend_col = 'spend' if 'spend' in df.columns else 'cost'
            kpis['total_spend'] = df[spend_col].sum()
            
            if 'clicks' in df.columns:
                kpis['cpc'] = kpis['total_spend'] / df['clicks'].sum() if df['clicks'].sum() > 0 else 0
        
        if 'conversions' in df.columns and 'spend' in df.columns:
            kpis['roas'] = df['conversions'].sum() / df['spend'].sum() if df['spend'].sum() > 0 else 0
        
        # Add generic metrics
        kpis.update(self._add_generic_metrics(df))
        return kpis
    
    def analyze_sales(self, df: pd.DataFrame, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sales data"""
        kpis = {}
        
        # Revenue metrics
        revenue_cols = [col for col in df.columns if any(word in col.lower() for word in ['revenue', 'sales', 'amount', 'total'])]
        if revenue_cols:
            revenue_col = revenue_cols[0]
            kpis['total_revenue'] = df[revenue_col].sum()
            kpis['avg_order_value'] = df[revenue_col].mean()
        
        # Customer metrics
        if 'customer_id' in df.columns or 'customers' in df.columns:
            customer_col = 'customer_id' if 'customer_id' in df.columns else 'customers'
            kpis['unique_customers'] = df[customer_col].nunique()
        
        # Product metrics
        if 'quantity' in df.columns:
            kpis['total_units_sold'] = df['quantity'].sum()
        
        kpis.update(self._add_generic_metrics(df))
        return kpis
    
    def analyze_survey(self, df: pd.DataFrame, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze survey feedback data"""
        kpis = {}
        
        # Response metrics
        kpis['total_responses'] = len(df)
        
        # Rating analysis
        rating_cols = [col for col in df.columns if any(word in col.lower() for word in ['rating', 'score', 'satisfaction'])]
        if rating_cols:
            rating_col = rating_cols[0]
            kpis['avg_rating'] = df[rating_col].mean()
            kpis['rating_distribution'] = df[rating_col].value_counts().to_dict()
        
        # Completion rate
        kpis['completion_rate'] = (1 - df.isnull().any(axis=1).sum() / len(df)) * 100
        
        kpis.update(self._add_generic_metrics(df))
        return kpis
    
    def analyze_finance(self, df: pd.DataFrame, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial records"""
        kpis = {}
        
        # Financial metrics
        amount_cols = [col for col in df.columns if any(word in col.lower() for word in ['amount', 'value', 'balance', 'total'])]
        if amount_cols:
            amount_col = amount_cols[0]
            kpis['total_amount'] = df[amount_col].sum()
            kpis['avg_transaction'] = df[amount_col].mean()
            kpis['max_transaction'] = df[amount_col].max()
        
        # Transaction analysis
        if 'type' in df.columns or 'category' in df.columns:
            type_col = 'type' if 'type' in df.columns else 'category'
            kpis['transaction_types'] = df[type_col].value_counts().to_dict()
        
        kpis.update(self._add_generic_metrics(df))
        return kpis
    
    def analyze_operations(self, df: pd.DataFrame, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze operations metrics"""
        kpis = {}
        
        # Performance metrics
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            kpis[f'avg_{col}'] = df[col].mean()
            kpis[f'total_{col}'] = df[col].sum()
        
        # Efficiency metrics
        if 'duration' in df.columns or 'time' in df.columns:
            time_col = 'duration' if 'duration' in df.columns else 'time'
            kpis['avg_processing_time'] = df[time_col].mean()
        
        kpis.update(self._add_generic_metrics(df))
        return kpis
    
    def analyze_generic(self, df: pd.DataFrame, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generic analysis for unknown dataset types"""
        kpis = self._add_generic_metrics(df)
        
        # Add basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
            kpis[f'avg_{col}'] = df[col].mean()
            kpis[f'total_{col}'] = df[col].sum()
        
        return kpis
    
    def _add_generic_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Add generic metrics applicable to any dataset"""
        return {
            'row_count': len(df),
            'column_count': len(df.columns),
            'data_completeness': ((df.size - df.isnull().sum().sum()) / df.size * 100) if df.size > 0 else 0
        }