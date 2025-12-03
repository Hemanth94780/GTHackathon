"""
AI-Driven Dynamic Chart Generation
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import os
import logging

logger = logging.getLogger(__name__)

class DynamicChartGenerator:
    """AI-driven chart generation based on data analysis plan"""
    
    def __init__(self):
        self.chart_functions = {
            'line_trend': self._create_line_trend,
            'bar_comparison': self._create_bar_comparison,
            'pie_distribution': self._create_pie_distribution,
            'scatter_correlation': self._create_scatter_correlation,
            'heatmap_correlation': self._create_heatmap,
            'histogram_distribution': self._create_histogram,
            'box_plot_outliers': self._create_box_plot,
            'stacked_bar': self._create_stacked_bar
        }
    
    def generate_charts(self, df: pd.DataFrame, analysis_plan: Dict[str, Any], name_prefix: str = "chart") -> List[str]:
        """
        Generate charts based on AI analysis plan
        
        Args:
            df: DataFrame to visualize
            analysis_plan: Plan from AI with specific chart specifications
            
        Returns:
            List of chart file paths
        """
        chart_paths = []
        charts_dir = os.path.join(os.getcwd(), 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        
        dataset_type = analysis_plan.get('dataset_type', 'generic_tabular')
        chart_specs = analysis_plan.get('chart_specs', [])
        required_cols = analysis_plan.get('required_columns', {})
        
        print(f"🎨 Generating {len(chart_specs)} AI-specified charts for {dataset_type}")
        
        for i, chart_spec in enumerate(chart_specs):
            try:
                chart_type = chart_spec.get('chart_type', 'bar_comparison')
                chart_path = self._generate_spec_chart(df, chart_spec, dataset_type, required_cols, charts_dir, f"{name_prefix}_{i+1}")
                if chart_path:
                    chart_paths.append(chart_path)
                    print(f"✅ Created {chart_type}: {os.path.basename(chart_path)}")
            except Exception as e:
                print(f"❌ Failed to create chart {i+1}: {str(e)}")
                continue
        
        return chart_paths
    
    def _generate_spec_chart(self, df: pd.DataFrame, chart_spec: Dict[str, Any], dataset_type: str, 
                            required_cols: Dict[str, Any], charts_dir: str, name_prefix: str) -> str:
        """Generate chart based on AI specification"""
        
        chart_type = chart_spec.get('chart_type', 'bar_comparison')
        x_column = chart_spec.get('x_column', 'auto_detect')
        y_column = chart_spec.get('y_column', 'auto_detect')
        purpose = chart_spec.get('purpose', 'Data visualization')
        
        if chart_type not in self.chart_functions:
            print(f"⚠️ Unknown chart type: {chart_type}")
            return None
        
        # Prepare chart data based on specification
        chart_data = self._prepare_spec_data(df, chart_spec, dataset_type, required_cols)
        
        if chart_data is None:
            print(f"⚠️ No suitable data for {chart_type}")
            return None
        
        # Generate chart
        chart_path = self.chart_functions[chart_type](chart_data, dataset_type, charts_dir, name_prefix)
        return chart_path
    
    def _prepare_spec_data(self, df: pd.DataFrame, chart_spec: Dict[str, Any], dataset_type: str, 
                          required_cols: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data based on AI chart specification"""
        
        chart_type = chart_spec.get('chart_type')
        x_column = chart_spec.get('x_column', 'auto_detect')
        y_column = chart_spec.get('y_column', 'auto_detect')
        purpose = chart_spec.get('purpose', 'Data visualization')
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Auto-detect columns if needed
        if x_column == 'auto_detect':
            x_column = self._auto_detect_column(df, 'x', chart_type, required_cols)
        if y_column == 'auto_detect':
            y_column = self._auto_detect_column(df, 'y', chart_type, required_cols)
        
        # Prepare data based on chart type
        if chart_type == 'line_trend':
            date_col = required_cols.get('date_column') or x_column
            metric_col = required_cols.get('primary_metric') or y_column
            
            if date_col and date_col in df.columns and metric_col and metric_col in df.columns:
                return {
                    'x_col': date_col,
                    'y_cols': [metric_col],
                    'data': df,
                    'title': f'{purpose} - {metric_col} Over Time'
                }
        
        elif chart_type == 'bar_comparison':
            category_col = required_cols.get('category_column') or x_column
            value_col = required_cols.get('primary_metric') or y_column
            
            if category_col and category_col in df.columns and value_col and value_col in df.columns:
                return {
                    'category_col': category_col,
                    'value_col': value_col,
                    'data': df,
                    'title': f'{purpose} - {value_col} by {category_col}'
                }
            elif len(numeric_cols) >= 2:
                return {
                    'metrics': numeric_cols[:3],
                    'data': df,
                    'title': f'{purpose} - Metrics Comparison'
                }
        
        elif chart_type == 'pie_distribution':
            category_col = required_cols.get('category_column') or x_column
            if category_col and category_col in df.columns:
                return {
                    'category_col': category_col,
                    'data': df,
                    'title': f'{purpose} - {category_col} Distribution'
                }
        
        elif chart_type == 'scatter_correlation':
            x_col = required_cols.get('primary_metric') or x_column
            y_col = required_cols.get('secondary_metric') or y_column
            
            if x_col and x_col in df.columns and y_col and y_col in df.columns:
                return {
                    'x_col': x_col,
                    'y_col': y_col,
                    'data': df,
                    'title': f'{purpose} - {x_col} vs {y_col}'
                }
        
        elif chart_type == 'histogram_distribution':
            metric_col = required_cols.get('primary_metric') or y_column
            if metric_col and metric_col in df.columns:
                return {
                    'column': metric_col,
                    'data': df,
                    'title': f'{purpose} - {metric_col} Distribution'
                }
        
        elif chart_type == 'box_plot_outliers':
            if len(numeric_cols) >= 1:
                return {
                    'columns': numeric_cols[:4],
                    'data': df,
                    'title': f'{purpose} - Outlier Analysis'
                }
        
        elif chart_type == 'heatmap_correlation':
            if len(numeric_cols) >= 2:
                return {
                    'columns': numeric_cols,
                    'data': df,
                    'title': f'{purpose} - Correlation Matrix'
                }
        
        return None
    
    def _auto_detect_column(self, df: pd.DataFrame, axis: str, chart_type: str, required_cols: Dict) -> str:
        """Auto-detect appropriate column for chart axis"""
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if axis == 'x':
            # For x-axis, prefer date/category columns
            if required_cols.get('date_column') and required_cols['date_column'] in df.columns:
                return required_cols['date_column']
            elif required_cols.get('category_column') and required_cols['category_column'] in df.columns:
                return required_cols['category_column']
            elif categorical_cols:
                return categorical_cols[0]
            elif numeric_cols:
                return numeric_cols[0]
        
        elif axis == 'y':
            # For y-axis, prefer numeric metrics
            if required_cols.get('primary_metric') and required_cols['primary_metric'] in df.columns:
                return required_cols['primary_metric']
            elif numeric_cols:
                return numeric_cols[0]
        
        return None
    
    def _create_line_trend(self, chart_data: Dict[str, Any], dataset_type: str, charts_dir: str, name_prefix: str) -> str:
        """Create line trend chart"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        df = chart_data['data']
        x_col = chart_data['x_col']
        y_cols = chart_data['y_cols']
        
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
        
        for i, col in enumerate(y_cols):
            if col in df.columns:
                if x_col:
                    try:
                        x_data = pd.to_datetime(df[x_col])
                    except:
                        x_data = range(len(df))
                else:
                    x_data = range(len(df))
                
                ax.plot(x_data, df[col], marker='o', linewidth=2.5, 
                       color=colors[i % len(colors)], label=col.replace('_', ' ').title())
        
        ax.set_title(chart_data['title'], fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Time' if x_col else 'Data Points')
        ax.set_ylabel('Values')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if x_col:
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        chart_path = os.path.join(charts_dir, f'{name_prefix}_trend.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return chart_path
    
    def _create_bar_comparison(self, chart_data: Dict[str, Any], dataset_type: str, charts_dir: str, name_prefix: str) -> str:
        """Create bar comparison chart"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        df = chart_data['data']
        
        if 'category_col' in chart_data:
            # Category-based comparison
            category_col = chart_data['category_col']
            value_col = chart_data['value_col']
            
            grouped = df.groupby(category_col)[value_col].sum().sort_values(ascending=False)[:10]
            bars = ax.bar(range(len(grouped)), grouped.values, color='#2E86AB')
            ax.set_xticks(range(len(grouped)))
            ax.set_xticklabels(grouped.index, rotation=45, ha='right')
            
        else:
            # Metrics comparison
            metrics = chart_data['metrics']
            values = [df[col].mean() for col in metrics if col in df.columns]
            labels = [col.replace('_', ' ').title() for col in metrics if col in df.columns]
            
            colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#9467BD']
            bars = ax.bar(labels, values, color=colors[:len(values)])
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_title(chart_data['title'], fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel('Values')
        
        plt.tight_layout()
        chart_path = os.path.join(charts_dir, f'{name_prefix}_comparison.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return chart_path
    
    def _create_pie_distribution(self, chart_data: Dict[str, Any], dataset_type: str, charts_dir: str, name_prefix: str) -> str:
        """Create pie distribution chart"""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        df = chart_data['data']
        category_col = chart_data['category_col']
        
        distribution = df[category_col].value_counts()[:8]  # Top 8 categories
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(distribution)))
        wedges, texts, autotexts = ax.pie(distribution.values, labels=distribution.index, 
                                         autopct='%1.1f%%', colors=colors, startangle=90)
        
        ax.set_title(chart_data['title'], fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        chart_path = os.path.join(charts_dir, f'{name_prefix}_distribution.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return chart_path
    
    def _create_scatter_correlation(self, chart_data: Dict[str, Any], dataset_type: str, charts_dir: str, name_prefix: str) -> str:
        """Create scatter correlation chart"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        df = chart_data['data']
        x_col = chart_data['x_col']
        y_col = chart_data['y_col']
        
        ax.scatter(df[x_col], df[y_col], alpha=0.6, color='#2E86AB', s=50)
        
        # Add trend line
        z = np.polyfit(df[x_col].dropna(), df[y_col].dropna(), 1)
        p = np.poly1d(z)
        ax.plot(df[x_col], p(df[x_col]), "r--", alpha=0.8, linewidth=2)
        
        ax.set_xlabel(x_col.replace('_', ' ').title())
        ax.set_ylabel(y_col.replace('_', ' ').title())
        ax.set_title(chart_data['title'], fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        chart_path = os.path.join(charts_dir, f'{name_prefix}_correlation.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return chart_path
    
    def _create_heatmap(self, chart_data: Dict[str, Any], dataset_type: str, charts_dir: str, name_prefix: str) -> str:
        """Create correlation heatmap"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        df = chart_data['data']
        columns = chart_data.get('columns', [])
        
        if columns and len(columns) >= 2:
            valid_cols = [col for col in columns if col in df.columns]
            if len(valid_cols) >= 2:
                corr_matrix = df[valid_cols].corr()
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=ax, fmt='.2f')
                ax.set_title(chart_data['title'], fontsize=16, fontweight='bold', pad=20)
            else:
                ax.text(0.5, 0.5, 'Insufficient numeric columns for correlation', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
                ax.set_title(chart_data['title'], fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        chart_path = os.path.join(charts_dir, f'{name_prefix}_heatmap.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return chart_path
    
    def _create_histogram(self, chart_data: Dict[str, Any], dataset_type: str, charts_dir: str, name_prefix: str) -> str:
        """Create histogram distribution"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        df = chart_data['data']
        col = chart_data.get('column')
        
        if col and col in df.columns:
            data_to_plot = df[col].dropna()
            if len(data_to_plot) > 0:
                ax.hist(data_to_plot, bins=min(20, len(data_to_plot)), alpha=0.7, color='#2E86AB', edgecolor='black')
                ax.set_xlabel(col.replace('_', ' ').title())
                ax.set_ylabel('Frequency')
                ax.set_title(chart_data['title'], fontsize=16, fontweight='bold', pad=20)
                ax.grid(True, alpha=0.3)
            else:
                ax.text(0.5, 0.5, 'No data available for histogram', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
                ax.set_title(chart_data['title'], fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        chart_path = os.path.join(charts_dir, f'{name_prefix}_histogram.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return chart_path
    
    def _create_box_plot(self, chart_data: Dict[str, Any], dataset_type: str, charts_dir: str, name_prefix: str) -> str:
        """Create box plot for outlier detection"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        df = chart_data['data']
        columns = chart_data.get('columns', [])
        
        if columns and len(columns) > 0:
            valid_cols = [col for col in columns if col in df.columns]
            if valid_cols:
                df[valid_cols].boxplot(ax=ax)
                ax.set_title(chart_data['title'], fontsize=16, fontweight='bold', pad=20)
                ax.set_ylabel('Values')
                plt.xticks(rotation=45)
            else:
                ax.text(0.5, 0.5, 'No suitable columns for box plot', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
                ax.set_title(chart_data['title'], fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        chart_path = os.path.join(charts_dir, f'{name_prefix}_boxplot.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return chart_path
    
    def _create_stacked_bar(self, chart_data: Dict[str, Any], dataset_type: str, charts_dir: str, name_prefix: str) -> str:
        """Create stacked bar chart"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        df = chart_data['data']
        numeric_cols = df.select_dtypes(include=[np.number]).columns[:3]
        
        if len(numeric_cols) >= 2:
            bottom = np.zeros(len(df))
            colors = ['#2E86AB', '#A23B72', '#F18F01']
            
            for i, col in enumerate(numeric_cols):
                ax.bar(range(len(df)), df[col], bottom=bottom, 
                      label=col.replace('_', ' ').title(), color=colors[i % len(colors)])
                bottom += df[col]
            
            ax.set_title(chart_data['title'], fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Records')
            ax.set_ylabel('Values')
            ax.legend()
        
        plt.tight_layout()
        chart_path = os.path.join(charts_dir, f'{name_prefix}_stacked.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return chart_path