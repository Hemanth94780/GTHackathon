"""
Smart KPI Calculator - Uses AI analysis plan to calculate relevant KPIs
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class SmartKPICalculator:
    """Calculates KPIs based on AI analysis plan and actual data columns"""
    
    def calculate_kpis(self, df: pd.DataFrame, analysis_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate KPIs based on AI analysis plan
        
        Args:
            df: DataFrame to analyze
            analysis_plan: Analysis plan from AI with specific column mappings
            
        Returns:
            Dictionary of calculated KPIs
        """
        kpis = {}
        
        # Get column mappings from AI analysis
        required_cols = analysis_plan.get('required_columns', {})
        dataset_type = analysis_plan.get('dataset_type', 'generic_tabular')
        kpi_calculations = analysis_plan.get('kpi_calculations', [])
        
        print(f"📊 Calculating KPIs for {dataset_type} dataset")
        
        # Add basic metrics
        kpis.update(self._calculate_basic_metrics(df))
        
        # Calculate dataset-specific KPIs based on AI plan
        kpis.update(self._calculate_planned_kpis(df, kpi_calculations, required_cols))
        
        # Add dataset-type specific KPIs
        kpis.update(self._calculate_type_specific_kpis(df, dataset_type, required_cols))
        
        print(f"✅ Calculated {len(kpis)} KPIs")
        return kpis
    
    def _calculate_basic_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic metrics for any dataset"""
        return {
            'row_count': len(df),
            'column_count': len(df.columns),
            'data_completeness': ((df.size - df.isnull().sum().sum()) / df.size * 100) if df.size > 0 else 0,
            'numeric_columns_count': len(df.select_dtypes(include=['number']).columns),
            'categorical_columns_count': len(df.select_dtypes(include=['object']).columns)
        }
    
    def _calculate_planned_kpis(self, df: pd.DataFrame, kpi_calculations: List[Dict], required_cols: Dict) -> Dict[str, Any]:
        """Calculate KPIs based on AI analysis plan"""
        kpis = {}
        
        for kpi_plan in kpi_calculations:
            kpi_name = kpi_plan.get('kpi_name', 'unknown_kpi')
            calculation = kpi_plan.get('calculation', '')
            columns_needed = kpi_plan.get('columns_needed', [])
            
            try:
                # Find actual columns that exist in the dataframe
                actual_columns = [col for col in columns_needed if col in df.columns]
                
                if not actual_columns and columns_needed:
                    # Try to find similar columns
                    actual_columns = self._find_similar_columns(df, columns_needed)
                
                if actual_columns:
                    kpi_value = self._execute_calculation(df, calculation, actual_columns)
                    if kpi_value is not None:
                        kpis[kpi_name] = kpi_value
                        
            except Exception as e:
                logger.warning(f"Failed to calculate {kpi_name}: {str(e)}")
                continue
        
        return kpis
    
    def _calculate_type_specific_kpis(self, df: pd.DataFrame, dataset_type: str, required_cols: Dict) -> Dict[str, Any]:
        """Calculate KPIs specific to dataset type"""
        kpis = {}
        
        if dataset_type == 'ad_performance':
            kpis.update(self._calculate_ad_kpis(df, required_cols))
        elif dataset_type == 'sales_data':
            kpis.update(self._calculate_sales_kpis(df, required_cols))
        elif dataset_type == 'survey_feedback':
            kpis.update(self._calculate_survey_kpis(df, required_cols))
        elif dataset_type == 'financial_records':
            kpis.update(self._calculate_financial_kpis(df, required_cols))
        elif dataset_type == 'operations_metrics':
            kpis.update(self._calculate_operations_kpis(df, required_cols))
        elif dataset_type == 'weather_data':
            kpis.update(self._calculate_weather_kpis(df, required_cols))
        elif dataset_type == 'scientific_data':
            kpis.update(self._calculate_scientific_kpis(df, required_cols))
        else:
            kpis.update(self._calculate_generic_kpis(df, required_cols))
        
        return kpis
    
    def _calculate_ad_kpis(self, df: pd.DataFrame, required_cols: Dict) -> Dict[str, Any]:
        """Calculate advertising performance KPIs"""
        kpis = {}
        
        # CTR calculation
        if 'clicks' in df.columns and 'impressions' in df.columns:
            total_clicks = df['clicks'].sum()
            total_impressions = df['impressions'].sum()
            kpis['ctr'] = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            kpis['total_clicks'] = total_clicks
            kpis['total_impressions'] = total_impressions
        
        # Cost metrics
        cost_cols = [col for col in df.columns if any(word in col.lower() for word in ['cost', 'spend', 'budget'])]
        if cost_cols:
            cost_col = cost_cols[0]
            kpis['total_spend'] = df[cost_col].sum()
            kpis['avg_daily_spend'] = df[cost_col].mean()
            
            if 'clicks' in df.columns:
                kpis['cpc'] = kpis['total_spend'] / df['clicks'].sum() if df['clicks'].sum() > 0 else 0
        
        # Conversion metrics
        if 'conversions' in df.columns:
            kpis['total_conversions'] = df['conversions'].sum()
            if 'clicks' in df.columns:
                kpis['conversion_rate'] = (df['conversions'].sum() / df['clicks'].sum() * 100) if df['clicks'].sum() > 0 else 0
        
        return kpis
    
    def _calculate_sales_kpis(self, df: pd.DataFrame, required_cols: Dict) -> Dict[str, Any]:
        """Calculate sales data KPIs"""
        kpis = {}
        
        # Revenue metrics
        revenue_cols = [col for col in df.columns if any(word in col.lower() for word in ['revenue', 'sales', 'amount', 'total', 'price'])]
        if revenue_cols:
            revenue_col = revenue_cols[0]
            kpis['total_revenue'] = df[revenue_col].sum()
            kpis['avg_order_value'] = df[revenue_col].mean()
            kpis['max_order_value'] = df[revenue_col].max()
        
        # Quantity metrics
        if 'quantity' in df.columns:
            kpis['total_units_sold'] = df['quantity'].sum()
            kpis['avg_units_per_order'] = df['quantity'].mean()
        
        # Customer metrics
        customer_cols = [col for col in df.columns if 'customer' in col.lower()]
        if customer_cols:
            customer_col = customer_cols[0]
            kpis['unique_customers'] = df[customer_col].nunique()
        
        return kpis
    
    def _calculate_survey_kpis(self, df: pd.DataFrame, required_cols: Dict) -> Dict[str, Any]:
        """Calculate survey feedback KPIs"""
        kpis = {}
        
        kpis['total_responses'] = len(df)
        
        # Rating analysis
        rating_cols = [col for col in df.columns if any(word in col.lower() for word in ['rating', 'score', 'satisfaction'])]
        if rating_cols:
            rating_col = rating_cols[0]
            kpis['avg_rating'] = df[rating_col].mean()
            kpis['rating_std'] = df[rating_col].std()
            kpis['high_ratings_pct'] = (df[rating_col] >= 4).sum() / len(df) * 100 if len(df) > 0 else 0
        
        # Completion rate
        kpis['completion_rate'] = (1 - df.isnull().any(axis=1).sum() / len(df)) * 100 if len(df) > 0 else 0
        
        return kpis
    
    def _calculate_financial_kpis(self, df: pd.DataFrame, required_cols: Dict) -> Dict[str, Any]:
        """Calculate financial records KPIs"""
        kpis = {}
        
        # Amount analysis
        amount_cols = [col for col in df.columns if any(word in col.lower() for word in ['amount', 'value', 'balance', 'total'])]
        if amount_cols:
            amount_col = amount_cols[0]
            kpis['total_amount'] = df[amount_col].sum()
            kpis['avg_transaction'] = df[amount_col].mean()
            kpis['max_transaction'] = df[amount_col].max()
            kpis['transaction_volatility'] = df[amount_col].std()
        
        # Transaction type analysis
        type_cols = [col for col in df.columns if any(word in col.lower() for word in ['type', 'category'])]
        if type_cols:
            type_col = type_cols[0]
            kpis['transaction_types_count'] = df[type_col].nunique()
        
        return kpis
    
    def _calculate_operations_kpis(self, df: pd.DataFrame, required_cols: Dict) -> Dict[str, Any]:
        """Calculate operations metrics KPIs"""
        kpis = {}
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        # Performance metrics
        for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
            kpis[f'avg_{col}'] = df[col].mean()
            kpis[f'total_{col}'] = df[col].sum()
            kpis[f'max_{col}'] = df[col].max()
        
        # Efficiency metrics
        time_cols = [col for col in df.columns if any(word in col.lower() for word in ['time', 'duration', 'latency'])]
        if time_cols:
            time_col = time_cols[0]
            kpis['avg_processing_time'] = df[time_col].mean()
            kpis['max_processing_time'] = df[time_col].max()
        
        return kpis
    
    def _calculate_weather_kpis(self, df: pd.DataFrame, required_cols: Dict) -> Dict[str, Any]:
        """Calculate weather data KPIs"""
        kpis = {}
        
        # Temperature metrics
        temp_cols = [col for col in df.columns if 'temp' in col.lower()]
        if temp_cols:
            temp_col = temp_cols[0]
            kpis['avg_temperature'] = df[temp_col].mean()
            kpis['max_temperature'] = df[temp_col].max()
            kpis['min_temperature'] = df[temp_col].min()
            kpis['temperature_range'] = df[temp_col].max() - df[temp_col].min()
        
        # Precipitation metrics
        precip_cols = [col for col in df.columns if any(word in col.lower() for word in ['rain', 'precip', 'humidity'])]
        if precip_cols:
            precip_col = precip_cols[0]
            kpis['avg_precipitation'] = df[precip_col].mean()
            kpis['rainy_days'] = (df[precip_col] > 0).sum()
        
        return kpis
    
    def _calculate_scientific_kpis(self, df: pd.DataFrame, required_cols: Dict) -> Dict[str, Any]:
        """Calculate scientific data KPIs"""
        kpis = {}
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        # Statistical metrics
        for col in numeric_cols[:3]:  # Focus on first 3 numeric columns
            kpis[f'{col}_mean'] = df[col].mean()
            kpis[f'{col}_std'] = df[col].std()
            kpis[f'{col}_median'] = df[col].median()
            kpis[f'{col}_range'] = df[col].max() - df[col].min()
        
        # Correlation analysis
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            # Find highest correlation (excluding diagonal)
            corr_values = corr_matrix.values
            np.fill_diagonal(corr_values, 0)
            max_corr = np.max(np.abs(corr_values))
            kpis['max_correlation'] = max_corr
        
        return kpis
    
    def _calculate_generic_kpis(self, df: pd.DataFrame, required_cols: Dict) -> Dict[str, Any]:
        """Calculate generic KPIs for unknown dataset types"""
        kpis = {}
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        # Basic statistics for numeric columns
        for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
            kpis[f'avg_{col}'] = df[col].mean()
            kpis[f'total_{col}'] = df[col].sum()
        
        # Categorical analysis
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols[:2]:  # Limit to first 2 categorical columns
            kpis[f'{col}_unique_count'] = df[col].nunique()
        
        return kpis
    
    def _find_similar_columns(self, df: pd.DataFrame, target_columns: List[str]) -> List[str]:
        """Find columns in dataframe that are similar to target columns"""
        actual_columns = []
        
        for target in target_columns:
            if target == "numeric_columns":
                actual_columns.extend(df.select_dtypes(include=['number']).columns.tolist())
            else:
                # Look for partial matches
                for col in df.columns:
                    if target.lower() in col.lower() or col.lower() in target.lower():
                        actual_columns.append(col)
                        break
        
        return actual_columns
    
    def _execute_calculation(self, df: pd.DataFrame, calculation: str, columns: List[str]) -> Any:
        """Execute specific calculation on columns"""
        try:
            if calculation == "summary_statistics":
                return {col: df[col].describe().to_dict() for col in columns if col in df.columns}
            elif calculation == "sum":
                return sum(df[col].sum() for col in columns if col in df.columns)
            elif calculation == "mean":
                return sum(df[col].mean() for col in columns if col in df.columns) / len(columns)
            elif calculation == "correlation":
                if len(columns) >= 2:
                    valid_cols = [col for col in columns if col in df.columns]
                    if len(valid_cols) >= 2:
                        return df[valid_cols].corr().iloc[0, 1]
            else:
                # Default to mean for unknown calculations
                return sum(df[col].mean() for col in columns if col in df.columns) / len(columns)
        except Exception as e:
            logger.warning(f"Calculation failed: {str(e)}")
            return None