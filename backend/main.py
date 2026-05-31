from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import httpx
from google import genai
from google.genai import types

load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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
    print("GEMINI KEY:", GEMINI_API_KEY)
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
You are a senior equity analyst. You have been given real market data for {ticker}. 
Your job is to produce a structured research report. Be direct, specific, and data-driven. 
Use the provided data as your foundation, and search the web for recent news, leadership changes, 
and current events for {ticker} to enrich your analysis.

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

3. RECENT NEWS & EVENTS
Search for the most recent significant news for {ticker}. Include leadership changes, 
earnings updates, product launches, regulatory actions, or any major developments.
Rate the impact of each: Positive, Negative, or Neutral.

4. RISK ASSESSMENT
Identify the top 3 risks facing this company. Consider competitive threats, 
customer concentration, macro factors, and any recent red flags. 
Rate each risk: Critical, High, or Strategic.

5. TECHNICAL PICTURE
Based on the price data — open, close, high, low, volume — what does the 
recent price action suggest? Is there buying or selling pressure?

6. BULL CASE vs BEAR CASE
Bull case: What has to go right for this stock to outperform?
Bear case: What could cause this thesis to break down?
Net view: Give your honest assessment. What would change your mind?

Be concise but thorough. Use specific numbers where relevant.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            # tools=[{"google_search": {}}],
            temperature=1.0
        )
    )
    return response.text