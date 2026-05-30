from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import httpx
import google.generativeai as genai

load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Prism API is running"}

@app.get("/analyze/{ticker}")
def get_ticker(ticker):
    response = httpx.get(f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={POLYGON_API_KEY}")
    data = httpx.get(f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?apiKey={POLYGON_API_KEY}")
    stock_data = {
        "details": response.json(),
        "price": data.json()
    }
    gemini = analyze_with_gemini(ticker, stock_data)
    return {
        "data": stock_data,
        "gemini": gemini
    }

def analyze_with_gemini(ticker, data):
    model = genai.GenerativeModel("gemini-3.5-flash")
    prompt = f"""
You are a senior equity analyst. You have been given real market data for {ticker}. 
Your job is to produce a structured research report. Be direct, specific, and data-driven. 
Use the provided data as your foundation, but draw on your broader knowledge of this 
company, its industry, and recent market context to enrich your analysis.

MARKET DATA:
{data}

Produce a report covering the following sections:

1. BUSINESS MODEL
How does this company make money? What is its core product or service? 
What is its competitive moat? Who are the top 3 competitors?

2. VALUATION
Based on the market cap and price data provided, is this stock expensive or cheap 
relative to its peers and historical range? What does current pricing imply about 
growth expectations?

3. RISK ASSESSMENT
Identify the top 3 risks facing this company. Consider competitive threats, 
customer concentration, macro factors, and any recent red flags. 
Rate each risk: Critical, High, or Strategic.

4. TECHNICAL PICTURE
Based on the price data — open, close, high, low, volume — what does the 
recent price action suggest? Is there buying or selling pressure?

5. BULL CASE vs BEAR CASE
Bull case: What has to go right for this stock to outperform?
Bear case: What could cause this thesis to break down?
Net view: Give your honest assessment. What would change your mind?

Be concise but thorough. Use specific numbers where relevant.
"""
    response = model.generate_content(prompt)
    return response.text