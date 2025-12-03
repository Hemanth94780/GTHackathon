import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def create_sample_data():
    """Create realistic AdTech sample data for GroundTruth scenario"""
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Generate 30 days of data
    dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
    
    # 1. Footfall Data (Location visits)
    footfall_data = pd.DataFrame({
        'date': dates,
        'location_id': ['LOC_' + str(i % 5 + 1) for i in range(30)],
        'footfall_count': np.random.randint(150, 800, 30),
        'dwell_time_minutes': np.random.randint(5, 45, 30),
        'weather_condition': np.random.choice(['Sunny', 'Rainy', 'Cloudy'], 30),
        'temperature': np.random.randint(15, 35, 30)
    })
    
    # 2. Ad Performance Data
    ad_data = pd.DataFrame({
        'date': dates,
        'campaign_id': ['CAMP_' + str(i % 3 + 1) for i in range(30)],
        'impressions': np.random.randint(5000, 25000, 30),
        'clicks': np.random.randint(100, 800, 30),
        'conversions': np.random.randint(5, 50, 30),
        'spend_usd': np.random.uniform(500, 3000, 30).round(2)
    })
    
    # 3. Sales Data
    sales_data = pd.DataFrame({
        'date': dates,
        'store_id': ['STORE_' + str(i % 4 + 1) for i in range(30)],
        'revenue': np.random.uniform(2000, 15000, 30).round(2),
        'transactions': np.random.randint(50, 300, 30),
        'avg_basket_size': np.random.uniform(25, 150, 30).round(2)
    })
    
    # Save files
    footfall_data.to_csv("data/footfall_data.csv", index=False)
    ad_data.to_csv("data/ad_performance.csv", index=False)
    sales_data.to_csv("data/sales_data.csv", index=False)
    
    print("Created sample data files:")
    print("  data/footfall_data.csv - Location visit data")
    print("  data/ad_performance.csv - Ad campaign metrics")
    print("  data/sales_data.csv - Store sales data")
    
    # Show previews
    print("\nData Previews:")
    print("\n1. Footfall Data:")
    print(footfall_data.head(3))
    print("\n2. Ad Performance:")
    print(ad_data.head(3))
    print("\n3. Sales Data:")
    print(sales_data.head(3))

if __name__ == "__main__":
    create_sample_data()