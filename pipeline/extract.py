import pandas as pd

def extract_orders(filepath='pipeline/orders.csv'):
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    print(f"Extracted {len(df)} orders with columns: {df.columns.tolist()}")
    return df

if __name__ == "__main__":
    df = extract_orders()
    print(df.head(3))
    print(df.dtypes)