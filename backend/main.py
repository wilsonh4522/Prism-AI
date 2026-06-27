from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import httpx
from google import genai
from google.genai import types
import anthropic
import openai

load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://prism-one-smoky.vercel.app"],
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
    claude = analyze_with_anthropic(ticker, stock_data)
    openai = analyze_with_openai(ticker, stock_data)
    summary = generate_summary(ticker, gemini, claude, openai)
    return {
        "data": stock_data,
        "gemini": gemini,
        "claude": claude,
        "openai": openai,
        "summary": summary
    }

def analyze_with_gemini(ticker, data):
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
You are a senior equity analyst producing a structured equity research report for {ticker}. 

IMPORTANT DATA INSTRUCTIONS:
The market data below is pulled directly from Polygon.io and reflects the current, real-time price and fundamentals. This data is ground truth. You MUST use these exact numbers for price, market cap, volume, and share count in your analysis. Do NOT substitute, override, or adjust these figures with data from your training. If your training data shows a different price or market cap, ignore it — the Polygon data is correct. Keep your total response under 1500 words. Always complete every section fully. Never cut off mid-sentence or mid-section.

MARKET DATA (Source: Polygon.io — Current & Accurate):
{data}

Use the market data above as your quantitative foundation. For qualitative context — business description, competitive landscape, recent news, and industry trends — draw on your broader knowledge and search the web for the most recent developments.

Produce a report covering the following sections:

1. BUSINESS MODEL
How does this company make money? What is its core product or service?
What is its competitive moat? Who are the top 3 competitors?

2. VALUATION
Using ONLY the price and market cap from the Polygon data above, assess whether this stock is expensive or cheap relative to peers and historical range. State the exact price and market cap from the data. Do not use any other price figures.

3. RECENT NEWS & EVENTS
Search for the most recent significant news for {ticker}. Include leadership changes, earnings updates, product launches, regulatory actions, or any major developments from the last 90 days.
Rate the impact of each: Positive, Negative, or Neutral.

4. RISK ASSESSMENT
Identify the top 3 risks facing this company. Consider competitive threats, customer concentration, macro factors, and any recent red flags.
Rate each risk: Critical, High, or Strategic.

5. TECHNICAL PICTURE
Using ONLY the open, close, high, low, and volume from the Polygon data above, analyze recent price action. What does it suggest about buying or selling pressure? Do not reference any other price levels from your training.

6. BULL CASE vs BEAR CASE
Bull case: What has to go right for this stock to outperform?
Bear case: What could cause this thesis to break down?
Net view: Your honest assessment. What would change your mind?

Be concise but thorough. Always cite the exact Polygon numbers when referencing price or market cap.
"""
    response = client.models.generate_content(
        model="gemini-3.1-pro-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            # tools=[{"google_search": {}}],
            temperature=0.7
        )
    )
    return response.text

def analyze_with_anthropic(ticker, data):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = f"""
You are a senior equity analyst producing a structured equity research report for {ticker}.

IMPORTANT DATA INSTRUCTIONS:
The market data below is pulled directly from Polygon.io and reflects the current, real-time price and fundamentals. This data is ground truth. You MUST use these exact numbers for price, market cap, volume, and share count in your analysis. Do NOT substitute, override, or adjust these figures with data from your training. If your training data shows a different price or market cap, ignore it — the Polygon data is correct. Keep your total response under 1500 words. Always complete every section fully. Never cut off mid-sentence or mid-section.

MARKET DATA (Source: Polygon.io — Current & Accurate):
{data}

Use the market data above as your quantitative foundation. For qualitative context — business description, competitive landscape, recent news, and industry trends — draw on your broader knowledge and search the web for the most recent developments.

Produce a report covering the following sections:

1. BUSINESS MODEL
How does this company make money? What is its core product or service?
What is its competitive moat? Who are the top 3 competitors?

2. VALUATION
Using ONLY the price and market cap from the Polygon data above, assess whether this stock is expensive or cheap relative to peers and historical range. State the exact price and market cap from the data. Do not use any other price figures.

3. RECENT NEWS & EVENTS
Search for the most recent significant news for {ticker}. Include leadership changes, earnings updates, product launches, regulatory actions, or any major developments from the last 90 days.
Rate the impact of each: Positive, Negative, or Neutral.

4. RISK ASSESSMENT
Identify the top 3 risks facing this company. Consider competitive threats, customer concentration, macro factors, and any recent red flags.
Rate each risk: Critical, High, or Strategic.

5. TECHNICAL PICTURE
Using ONLY the open, close, high, low, and volume from the Polygon data above, analyze recent price action. What does it suggest about buying or selling pressure? Do not reference any other price levels from your training.

6. BULL CASE vs BEAR CASE
Bull case: What has to go right for this stock to outperform?
Bear case: What could cause this thesis to break down?
Net view: Your honest assessment. What would change your mind?

Be concise but thorough. Always cite the exact Polygon numbers when referencing price or market cap.
"""
    response = client.messages.create(
        model = "claude-sonnet-4-6",
        max_tokens=2048,
        messages = [
            {"role": "user", "content" : prompt}
        ]
    )
    return response.content[0].text

def analyze_with_openai(ticker, data):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"""
You are a senior equity analyst producing a structured equity research report for {ticker}.

IMPORTANT DATA INSTRUCTIONS:
The market data below is pulled directly from Polygon.io and reflects the current, real-time price and fundamentals. This data is ground truth. You MUST use these exact numbers for price, market cap, volume, and share count in your analysis. Do NOT substitute, override, or adjust these figures with data from your training. If your training data shows a different price or market cap, ignore it — the Polygon data is correct. Keep your total response under 1500 words. Always complete every section fully. Never cut off mid-sentence or mid-section.

MARKET DATA (Source: Polygon.io — Current & Accurate):
{data}

Use the market data above as your quantitative foundation. For qualitative context — business description, competitive landscape, recent news, and industry trends — draw on your broader knowledge and search the web for the most recent developments.

Produce a report covering the following sections:

1. BUSINESS MODEL
How does this company make money? What is its core product or service?
What is its competitive moat? Who are the top 3 competitors?

2. VALUATION
Using ONLY the price and market cap from the Polygon data above, assess whether this stock is expensive or cheap relative to peers and historical range. State the exact price and market cap from the data. Do not use any other price figures.

3. RECENT NEWS & EVENTS
Search for the most recent significant news for {ticker}. Include leadership changes, earnings updates, product launches, regulatory actions, or any major developments from the last 90 days.
Rate the impact of each: Positive, Negative, or Neutral.

4. RISK ASSESSMENT
Identify the top 3 risks facing this company. Consider competitive threats, customer concentration, macro factors, and any recent red flags.
Rate each risk: Critical, High, or Strategic.

5. TECHNICAL PICTURE
Using ONLY the open, close, high, low, and volume from the Polygon data above, analyze recent price action. What does it suggest about buying or selling pressure? Do not reference any other price levels from your training.

6. BULL CASE vs BEAR CASE
Bull case: What has to go right for this stock to outperform?
Bear case: What could cause this thesis to break down?
Net view: Your honest assessment. What would change your mind?

Be concise but thorough. Always cite the exact Polygon numbers when referencing price or market cap.
"""
    response = client.chat.completions.create(
        model = "gpt-4o",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def generate_summary(ticker, gemini_analysis, claude_analysis, openai_analysis):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = f"""You are a senior research director synthesizing independent equity analyses from three different AI analysts (Gemini, Claude, and GPT-4o) for {ticker}.

You are a neutral third party — you are NOT Gemini, Claude, or GPT-4o. You have no affiliation with any of the three analysts and no reason to favor any one of them, including yourself. Your only job is to represent the data and evidence fairly. Keep your total response under 6000 words. Always complete every section fully before moving to the next. Never cut off mid-sentence or mid-section. If you are running low on space, shorten each section rather than leaving the last sections incomplete.

Your job is to produce a single, objective consensus report. Do not favor any single analyst's view. Present all perspectives fairly and let the data speak.

GEMINI ANALYSIS:
{gemini_analysis}

CLAUDE ANALYSIS:
{claude_analysis}

GPT-4o ANALYSIS:
{openai_analysis}

Produce a synthesis covering the following:

1. CONSENSUS VIEW
Where do all three analysts agree? What is the strongest shared conviction across the reports?

2. POINTS OF DISAGREEMENT
Where do the analysts diverge? Present each perspective fairly without declaring a winner. 
Highlight what evidence or data supports each view and let the reader decide.

3. COMBINED RISK PICTURE
Synthesize the risk assessments into a unified top 3 risks ranked by severity.
Where analysts disagree on risk ratings, present the range of views.

4. TECHNICAL CONSENSUS
What does the combined technical picture suggest about near-term price action?

5. FINAL VERDICT
Bull case, bear case, and a neutral net recommendation based purely on the data.
Rate the stock: Strong Buy / Buy / Hold / Sell / Strong Sell
Give a price target range based on the combined analysis.
What is the single most important thing to watch for this stock?

Be objective and data-driven. Do not pick sides on disagreements — present them fairly.
"""

    response = client.messages.create(
        model = "claude-sonnet-4-6",
        max_tokens=8192,
        messages = [
            {"role": "user", "content" : prompt}
        ]
    )
    return response.content[0].text