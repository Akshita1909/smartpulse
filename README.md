# SmartPulse

Upload any sales or transaction CSV — get instant KPIs, interactive charts, and AI-generated business insights. No fixed format required. Works with any dataset.

## Live Demo

https://smartpulse-eta.vercel.app

## Problem It Solves

Most business intelligence tools require you to connect a database, learn a query language, or pay for an expensive subscription. SmartPulse lets anyone upload a CSV and get a full analytics dashboard in seconds — no setup, no schema, no technical knowledge required.

## How It Works

1. Upload any CSV file containing sales, orders, or transaction data
2. AI automatically detects what each column means — date, revenue, category, region, segment
3. Computes KPIs — total revenue, profit, orders, average order value
4. Generates interactive charts — revenue by category, trend over time, by region, by segment
5. AI produces 4 specific, actionable business insights from your actual data

## Features

- Works with any CSV — no fixed column names required
- AI column detection with smart fallbacks for edge cases
- Auto-generates charts based on what data is available
- KPI cards adapt to your dataset
- AI business insights referencing your specific numbers
- Upload new file anytime to analyze different datasets

## Tech Stack

- Frontend: React.js, Recharts, Axios, React Markdown
- Backend: FastAPI, Python, Pandas
- AI: Groq API — LLaMA 3.3 70B Versatile
- Deployment: Vercel (frontend) + Render (backend)

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Groq API key (free at console.groq.com)

### Installation

```bash
git clone https://github.com/Akshita1909/smartpulse.git
cd smartpulse

# Backend
cd backend
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env
uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm start
```

## Project Structure
