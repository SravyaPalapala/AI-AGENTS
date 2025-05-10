
import os
import time
import yfinance as yf
import streamlit as st
from agno.agent import Agent
from agno.models.google import Gemini
import plotly.graph_objects as go
from agno.exceptions import ModelProviderError
import time
import random
from functools import wraps
import yfinance as yf
import time
import random
from functools import wraps
import yfinance as yf

# Configure yfinance cache
yf.set_tz_cache_location("yfinance_cache")

def yfinance_throttle(func):
    """Decorator to throttle yfinance requests with random delays and retries"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                time.sleep(2 + random.random() * 2)  # Random delay 2-4 seconds
                result = func(*args, **kwargs)
                if result is None:  # If function returns None, retry
                    raise ValueError("Empty response")
                return result
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed after {max_retries} attempts for {args}: {str(e)}")
                    return None
                time.sleep(5 * (attempt + 1))  # Exponential backoff
    return wrapper
# ---------------------------------- Utilities ---------------------------------- #

def run_with_retries(agent, prompt, retries=3, delay=2):
    for attempt in range(retries):
        try:
            result = agent.run(prompt)
            return result.content
        except ModelProviderError as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return f"⚠️ Error from model provider: {str(e)}"
        except Exception as e:
            return f"⚠️ Unexpected error: {str(e)}"

# ------------------------------- Streamlit UI ---------------------------------- #

st.set_page_config(page_title=" MarketMetric Investment Strategist AI", page_icon="📈", layout="wide")

# Custom CSS for right sidebar and styling
st.markdown("""
    <style>
        /* Right sidebar positioning */
        [data-testid="stSidebar"] {
            position: fixed;
            right: 0;
            top: 0;
            width: 29%;
            padding: 2rem;
            background-color: #87CEEB;  /* Sky blue color */
            border-left: 1px solid #e9ecef;
            box-shadow: -5px 0 15px rgba(0,0,0,0.05);
        }

        /* Main content adjustment */
        .main .block-container {
            padding-right: 32%;
        }

        /* Header styling */
        .header {
            background: linear-gradient(135deg, #457b9d 0%, #1d3557 100%);
            padding: 2rem;
            border-radius: 0 0 15px 15px;
            margin-bottom: 2rem;
            color: white;
        }

        /* Card styling */
        .report-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border-left: 4px solid #e63946;
        }

        /* Optional: Style the text in sidebar for better contrast */
        .stSidebar .stMarkdown {
            color: #000000;  /* Black text for better readability */
        }

        /* Style the input fields in sidebar */
        .stSidebar .stTextInput input {
            background-color: #FFFFFF;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)
# Sidebar Styling
st.sidebar.markdown("""
    <p style="color: #6c757d;">Enter the stock symbols you want to analyze. The AI will provide detailed insights, performance reports, and top recommendations.</p>
""", unsafe_allow_html=True)
# Header Section
st.markdown("""
    <div class="header">
        <h1 style="text-align: center; margin: 0;">
            📊 MarketMetric Investment Strategist AI
        </h1>
        <p style="text-align: center; margin: 0.5rem 0 0; opacity: 0.9;">
            Generate personalized investment reports with the latest market insights
        </p>
    </div>
""", unsafe_allow_html=True)

# Right Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Configuration Panel")
    input_symbols = st.text_input("Enter Stock Symbols (comma separated)", "AAPL, TSLA, GOOG")
    api_key = st.text_input("Enter your Google API Key", type="password")
# ----------------------------- Agent Definitions ----------------------------- #

gemini_model = Gemini(id="gemini-2.0-flash-exp")

market_analyst = Agent(
    model=gemini_model,
    description="Analyzes and compares stock performance over time.",
    instructions=[
        "Retrieve and compare stock performance from Yahoo Finance.",
        "Calculate percentage change over a 6-month period.",
        "Rank stocks based on their relative performance."
    ],
    markdown=True
)

company_researcher = Agent(
    model=gemini_model,
    description="Fetches company profiles, financials, and latest news.",
    instructions=[
        "Retrieve company information from Yahoo Finance.",
        "Summarize latest company news relevant to investors.",
        "Provide sector, market cap, and business overview."
    ],
    markdown=True
)

stock_strategist = Agent(
    model=gemini_model,
    description="Provides investment insights and recommends top stocks.",
    instructions=[
        "Analyze stock performance trends and company fundamentals.",
        "Evaluate risk-reward potential and industry trends.",
        "Provide top stock recommendations for investors."
    ],
    markdown=True
)

team_lead = Agent(
    model=gemini_model,
    description="Aggregates stock analysis, company research, and investment strategy.",
    instructions=[
        "Compile stock performance, company analysis, and recommendations.",
        "Ensure all insights are structured in an investor-friendly report.",
        "Rank the top stocks based on combined analysis."
    ],
    markdown=True
)

# -------------------------- Data Fetching Functions -------------------------- #

@yfinance_throttle
def get_company_news(symbol):
    stock = yf.Ticker(symbol)
    try:
        return stock.news[:5] if hasattr(stock, "news") else []
    except:
        return []

@yfinance_throttle
def compare_stocks(symbols):
    data = {}
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="6mo")
            if not hist.empty:
                data[symbol] = hist['Close'].pct_change().sum()
        except:
            continue
    return data
def get_final_investment_report(symbols):
    """Main function with complete error handling"""
    valid_symbols = [s for s in symbols if s.strip()]
    if not valid_symbols:
        return "No valid stock symbols provided"
    
    # Get market analysis with fallback
    market_analysis = get_market_analysis(valid_symbols) or "Market analysis unavailable"
    
    # Get company analyses with fallbacks
    company_analyses = []
    for s in valid_symbols:
        time.sleep(1 + random.random())  # Delay between requests
        analysis = get_company_analysis(s)
        company_analyses.append(analysis)
    
    # Get recommendations with fallback
    recommendations = get_stock_recommendations(valid_symbols) or "Recommendations unavailable"
    
    prompt = (
        f"Market Analysis:\n{market_analysis}\n\n"
        f"Company Analyses:\n{company_analyses}\n\n"
        f"Stock Recommendations:\n{recommendations}\n\n"
        f"Provide a final ranked list of stocks with detailed reasoning."
    )
    return run_with_retries(team_lead, prompt) or "Report generation failed"
# -------------------------- AI-Based Analysis Logic -------------------------- #

def get_market_analysis(symbols):
    perf_data = compare_stocks(symbols)
    if not perf_data:
        return "⚠️ No valid stock data found."
    return run_with_retries(market_analyst, f"Compare these stock performances: {perf_data}")

@yfinance_throttle
def get_company_info(symbol):
    """Safe company info fetcher with default values"""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            "name": info.get("longName", symbol),
            "sector": info.get("sector", "Unknown Sector"),
            "market_cap": info.get("marketCap", "N/A"),
            "summary": info.get("longBusinessSummary", "No description available"),
        }
    except Exception as e:
        print(f"Error getting info for {symbol}: {str(e)}")
        return {
            "name": symbol,
            "sector": "Unknown Sector",
            "market_cap": "N/A",
            "summary": "No description available",
        }

def get_company_analysis(symbol):
    """Safe company analysis that never returns None"""
    info = get_company_info(symbol) or {
        "name": symbol,
        "sector": "Unknown Sector",
        "market_cap": "N/A",
        "summary": "No description available",
    }
    
    news = get_company_news(symbol) or []
    news_text = "\n".join([f"- {n.get('title', 'No title')}" for n in news])
    
    prompt = (
        f"Provide an analysis for {info['name']} in the {info['sector']} sector.\n"
        f"Market Cap: {info['market_cap']}\n"
        f"Summary: {info['summary']}\n"
        f"Latest News:\n{news_text}"
    )
    return run_with_retries(company_researcher, prompt) or f"Analysis unavailable for {symbol}"
def get_stock_recommendations(symbols):
    market_analysis = get_market_analysis(symbols)
    company_data = {sym: get_company_analysis(sym) for sym in symbols}
    prompt = (
        f"Based on the market analysis: {market_analysis}, and company news: {company_data}, "
        f"which stocks would you recommend for investment?"
    )
    return run_with_retries(stock_strategist, prompt)
def get_final_investment_report(symbols):
    # Initial delay
    time.sleep(3)
    
    market_analysis = get_market_analysis(symbols)
    
    company_analyses = []
    for s in symbols:
        # Add delay between each company analysis
        time.sleep(1 + random.random())
        company_analyses.append(get_company_analysis(s))
    
    recommendations = get_stock_recommendations(symbols)
    
    prompt = (
        f"Market Analysis:\n{market_analysis}\n\n"
        f"Company Analyses:\n{company_analyses}\n\n"
        f"Stock Recommendations:\n{recommendations}\n\n"
        f"Provide a final ranked list of stocks with detailed reasoning."
    )
    return run_with_retries(team_lead, prompt)
# ---------------------------- Streamlit Interaction ---------------------------- #

# Parse input (kept here as it's part of the interaction flow)
stocks_symbols = [s.strip().upper() for s in input_symbols.split(",") if s.strip()]
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key

# Button in sidebar triggers the interaction
if st.sidebar.button("💰📊📈 Build Investment Report"):
    if not stocks_symbols:
        st.sidebar.warning("Please enter at least one stock symbol.")
    elif not api_key:
        st.sidebar.warning("Please enter your API Key.")
    else:
        with st.spinner("Generating investment report..."):
            report = get_final_investment_report(stocks_symbols)

        # Display Results
        st.markdown("### 📄 Investment Report")
        st.markdown(report)
        st.info("This report includes market performance, company analysis, and investment recommendations.")

        # Plot
        st.markdown("### 📊 Stock Performance (6-Months)")
        stock_data = yf.download(stocks_symbols, period="6mo")['Close']
        fig = go.Figure()
        for sym in stocks_symbols:
            if sym in stock_data:
                fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data[sym], mode='lines', name=sym))
        fig.update_layout(title="Stock Performance Over the Last 6 Months",
                         xaxis_title="Date",
                         yaxis_title="Price (USD)",
                         template="plotly_dark")
        st.plotly_chart(fig)
