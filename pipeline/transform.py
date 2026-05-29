import pandas as pd
import numpy as np
from datetime import datetime

def transform_all(df):
    df = df.copy()
    
    # Fix data types
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['postal_code'] = df['postal_code'].astype(str)
    
    # Data quality checks
    print(f"Null values:\n{df.isnull().sum()}")
    print(f"Duplicate order_ids: {df['order_id'].duplicated().sum()}")
    
    # Calculate derived columns
    df['discount_amount'] = (df['list_price'] * df['discount_percent'] / 100).round(2)
    df['sale_price'] = (df['list_price'] - df['discount_amount']).round(2)
    df['revenue'] = (df['sale_price'] * df['quantity']).round(2)
    df['cost'] = (df['cost_price'] * df['quantity']).round(2)
    df['profit'] = (df['revenue'] - df['cost']).round(2)
    df['profit_margin'] = ((df['profit'] / df['revenue']) * 100).round(2)
    
    # Date dimension
    dim_date = pd.DataFrame({
        'order_date': df['order_date'].unique()
    })
    dim_date['day'] = dim_date['order_date'].dt.day
    dim_date['month'] = dim_date['order_date'].dt.month
    dim_date['month_name'] = dim_date['order_date'].dt.strftime('%B')
    dim_date['quarter'] = dim_date['order_date'].dt.quarter
    dim_date['year'] = dim_date['order_date'].dt.year
    dim_date['week'] = dim_date['order_date'].dt.isocalendar().week.astype(int)
    dim_date['weekday'] = dim_date['order_date'].dt.day_name()
    
    # Product dimension
    dim_product = df[['product_id', 'category', 'sub_category']].drop_duplicates()
    dim_product = dim_product.reset_index(drop=True)
    
    # Customer/Segment dimension
    dim_segment = df[['segment', 'region', 'country']].drop_duplicates()
    dim_segment = dim_segment.reset_index(drop=True)
    dim_segment['segment_id'] = dim_segment.index + 1
    
    # Fact table
    df = df.merge(dim_segment[['segment', 'region', 'country', 'segment_id']], 
                  on=['segment', 'region', 'country'], how='left')
    
    fact_sales = df[[
        'order_id', 'order_date', 'product_id', 'segment_id',
        'city', 'state', 'ship_mode',
        'quantity', 'list_price', 'discount_percent',
        'discount_amount', 'sale_price', 'revenue',
        'cost', 'profit', 'profit_margin'
    ]]
    
    print(f"\nDim Date: {len(dim_date)} rows")
    print(f"Dim Product: {len(dim_product)} rows")
    print(f"Dim Segment: {len(dim_segment)} rows")
    print(f"Fact Sales: {len(fact_sales)} rows")
    print(f"\nSample revenue stats:")
    print(f"Total Revenue: ${fact_sales['revenue'].sum():,.2f}")
    print(f"Total Profit: ${fact_sales['profit'].sum():,.2f}")
    print(f"Avg Profit Margin: {fact_sales['profit_margin'].mean():.2f}%")
    
    return dim_date, dim_product, dim_segment, fact_sales

if __name__ == "__main__":
    from extract import extract_orders
    df = extract_orders()
    dim_date, dim_product, dim_segment, fact_sales = transform_all(df)