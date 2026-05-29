from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from groq import Groq
import pandas as pd
import json
import os
import io

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def detect_columns(df):
    sample = df.head(3).to_string()
    columns = df.columns.tolist()
    dtypes = df.dtypes.astype(str).to_dict()

    prompt = f"""You are a data analyst. Given these CSV columns and sample data, identify what each column represents.

Columns: {columns}
Data types: {dtypes}
Sample rows:
{sample}

Return ONLY a JSON object with these keys (use null if not found):
{{
  "date_col": "column name for date/time/order date",
  "revenue_col": "column name for revenue/sales/amount/price/list price/sale price/total. Pick the most likely sales value column even if not obvious.",
  "profit_col": "column name for profit/margin/net income (null if not found)",
  "quantity_col": "column name for quantity/units/qty/count",
  "category_col": "column name for category/product type/department/segment type",
  "product_col": "column name for product name/product id/item name/SKU",
  "region_col": "column name for region/city/state/location/country/geography",
  "customer_col": "column name for customer segment/customer type/tier/membership"
}}

Be aggressive in finding revenue — look for price, amount, sales, value, cost, list price columns.
Return ONLY the JSON, nothing else, no explanation, no backticks."""

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        max_tokens=300,
    )

    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def apply_fallbacks(df, cols):
    """If AI missed columns, apply smart fallbacks"""
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    text_cols = df.select_dtypes(include=["object"]).columns.tolist()

    # Fallback for revenue — use first numeric column
    if not cols.get("revenue_col") or cols["revenue_col"] not in df.columns:
        if numeric_cols:
            cols["revenue_col"] = numeric_cols[0]

    # Fallback for quantity — use second numeric column
    if not cols.get("quantity_col") or cols["quantity_col"] not in df.columns:
        remaining = [c for c in numeric_cols if c != cols.get("revenue_col")]
        if remaining:
            cols["quantity_col"] = remaining[0]

    # Fallback for category — first text column with fewer than 30 unique values
    if not cols.get("category_col") or cols["category_col"] not in df.columns:
        for col in text_cols:
            if df[col].nunique() < 30:
                cols["category_col"] = col
                break

    # Fallback for region — text column with fewer than 100 unique values
    if not cols.get("region_col") or cols["region_col"] not in df.columns:
        for col in text_cols:
            if col != cols.get("category_col") and df[col].nunique() < 100:
                cols["region_col"] = col
                break

    # Fallback for date — first datetime-parseable column
    if not cols.get("date_col") or cols["date_col"] not in df.columns:
        for col in text_cols:
            try:
                pd.to_datetime(df[col].head(5))
                cols["date_col"] = col
                break
            except:
                pass

    # Fallback for segment — text column with fewer than 10 unique values
    if not cols.get("customer_col") or cols["customer_col"] not in df.columns:
        for col in text_cols:
            if col not in [cols.get("category_col"), cols.get("region_col")] and df[col].nunique() < 10:
                cols["customer_col"] = col
                break

    return cols


def compute_metrics(df, cols):
    metrics = {}

    if cols.get("revenue_col") and cols["revenue_col"] in df.columns:
        metrics["total_revenue"] = round(float(df[cols["revenue_col"]].sum()), 2)
        metrics["avg_order_value"] = round(float(df[cols["revenue_col"]].mean()), 2)

    if cols.get("profit_col") and cols["profit_col"] in df.columns:
        metrics["total_profit"] = round(float(df[cols["profit_col"]].sum()), 2)
        if cols.get("revenue_col") and cols["revenue_col"] in df.columns:
            rev = df[cols["revenue_col"]].sum()
            if rev != 0:
                metrics["profit_margin"] = round(
                    float(df[cols["profit_col"]].sum() / rev * 100), 2
                )

    metrics["total_orders"] = len(df)

    if cols.get("quantity_col") and cols["quantity_col"] in df.columns:
        metrics["total_quantity"] = int(df[cols["quantity_col"]].sum())

    return metrics


def compute_charts(df, cols):
    charts = {}

    # Revenue by category
    if cols.get("category_col") and cols.get("revenue_col"):
        cat = cols["category_col"]
        rev = cols["revenue_col"]
        if cat in df.columns and rev in df.columns:
            try:
                grouped = df.groupby(cat)[rev].sum().reset_index()
                grouped = grouped.sort_values(rev, ascending=False).head(10)
                charts["revenue_by_category"] = [
                    {"category": str(row[cat]), "revenue": round(float(row[rev]), 2)}
                    for _, row in grouped.iterrows()
                ]
            except:
                pass

    # Revenue over time
    if cols.get("date_col") and cols.get("revenue_col"):
        date = cols["date_col"]
        rev = cols["revenue_col"]
        if date in df.columns and rev in df.columns:
            try:
                df = df.copy()
                df[date] = pd.to_datetime(df[date])
                df["_month"] = df[date].dt.to_period("M").astype(str)
                grouped = df.groupby("_month")[rev].sum().reset_index()
                charts["revenue_over_time"] = [
                    {"date": str(row["_month"]), "revenue": round(float(row[rev]), 2)}
                    for _, row in grouped.iterrows()
                ]
            except:
                pass

    # Revenue by region
    if cols.get("region_col") and cols.get("revenue_col"):
        region = cols["region_col"]
        rev = cols["revenue_col"]
        if region in df.columns and rev in df.columns:
            try:
                grouped = df.groupby(region)[rev].sum().reset_index()
                grouped = grouped.sort_values(rev, ascending=False).head(8)
                charts["revenue_by_region"] = [
                    {"region": str(row[region]), "revenue": round(float(row[rev]), 2)}
                    for _, row in grouped.iterrows()
                ]
            except:
                pass

    # Revenue by segment
    if cols.get("customer_col") and cols.get("revenue_col"):
        seg = cols["customer_col"]
        rev = cols["revenue_col"]
        if seg in df.columns and rev in df.columns:
            try:
                grouped = df.groupby(seg)[rev].sum().reset_index()
                charts["revenue_by_segment"] = [
                    {"segment": str(row[seg]), "revenue": round(float(row[rev]), 2)}
                    for _, row in grouped.iterrows()
                ]
            except:
                pass

    return charts


def generate_insights(df, cols, metrics, charts):
    summary_parts = []

    if "total_revenue" in metrics:
        summary_parts.append(f"Total Revenue: ${metrics['total_revenue']:,}")
    if "total_profit" in metrics:
        summary_parts.append(f"Total Profit: ${metrics['total_profit']:,}")
        summary_parts.append(f"Profit Margin: {metrics['profit_margin']}%")
    summary_parts.append(f"Total Records: {metrics['total_orders']:,}")
    if "avg_order_value" in metrics:
        summary_parts.append(f"Average Value: ${metrics['avg_order_value']:,}")

    if "revenue_by_category" in charts:
        top_cats = charts["revenue_by_category"][:3]
        cat_text = ", ".join([f"{c['category']}: ${c['revenue']:,}" for c in top_cats])
        summary_parts.append(f"Top Categories: {cat_text}")

    if "revenue_by_region" in charts:
        top_regions = charts["revenue_by_region"][:3]
        region_text = ", ".join([f"{r['region']}: ${r['revenue']:,}" for r in top_regions])
        summary_parts.append(f"Top Regions: {region_text}")

    if "revenue_by_segment" in charts:
        seg_text = ", ".join([f"{s['segment']}: ${s['revenue']:,}" for s in charts["revenue_by_segment"]])
        summary_parts.append(f"By Segment: {seg_text}")

    prompt = f"""You are a senior business analyst. Analyze this data and provide 4 specific actionable insights.

Data Summary:
{chr(10).join(summary_parts)}

Write exactly 4 insights. Each must:
- Start with **Bold Title**
- Reference specific numbers from the data
- End with one actionable recommendation

Format as numbered list."""

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        max_tokens=600,
    )
    return response.choices[0].message.content


@app.post("/analyze")
async def analyze_csv(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    df.columns = df.columns.str.strip()

    # Detect columns using AI
    cols = detect_columns(df)

    # Apply smart fallbacks for missed columns
    cols = apply_fallbacks(df, cols)

    # Compute metrics
    metrics = compute_metrics(df, cols)

    # Compute charts
    charts = compute_charts(df, cols)

    # Generate AI insights
    insights = generate_insights(df, cols, metrics, charts)

    return {
        "success": True,
        "rows": len(df),
        "columns_detected": cols,
        "metrics": metrics,
        "charts": charts,
        "insights": insights
    }


@app.get("/")
def root():
    return {"status": "SmartPulse API running"}