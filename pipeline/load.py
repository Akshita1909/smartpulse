import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DB_URL"))

def drop_all_tables():
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS fact_sales CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS dim_date CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS dim_product CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS dim_segment CASCADE"))
        conn.commit()
    print("All tables dropped")

def load_all(dim_date, dim_product, dim_segment, fact_sales):
    drop_all_tables()

    dim_date.to_sql('dim_date', engine, if_exists='replace', index=False)
    print(f"Loaded {len(dim_date)} date records")

    dim_product.to_sql('dim_product', engine, if_exists='replace', index=False)
    print(f"Loaded {len(dim_product)} product records")

    dim_segment.to_sql('dim_segment', engine, if_exists='replace', index=False)
    print(f"Loaded {len(dim_segment)} segment records")

    fact_sales.to_sql('fact_sales', engine, if_exists='replace', index=False)
    print(f"Loaded {len(fact_sales)} sales records")

    print("All data loaded successfully!")

if __name__ == "__main__":
    from extract import extract_orders
    from transform import transform_all

    df = extract_orders()
    dim_date, dim_product, dim_segment, fact_sales = transform_all(df)
    load_all(dim_date, dim_product, dim_segment, fact_sales)