import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import yfinance as yf
from datetime import datetime, timedelta
import warnings
import requests
import json
from bs4 import BeautifulSoup
import pandas_datareader.data as web
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="🏦 BofA Risk-Love Sentiment Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add sidebar info button
with st.sidebar:
    with st.expander("ℹ️ Scoring Reference Guide"):
        # Title
        st.write("# Risk-Love Sentiment Calculation Guide")
        
        # Market Data Section
        st.write("## Market Data Indicators (30% Weight)")
        st.markdown("""
        ### 1. Momentum Score
        | Range | Score | Signal |
        |-------|--------|---------|
        | > +20% | 90 | Strong Sell |
        | +10% to +20% | 75 | Sell |
        | -5% to +10% | 55 | Neutral |
        | -15% to -5% | 30 | Buy |
        | < -15% | 10 | Strong Buy |
        
        _Formula: ((current_price / 60day_MA) - 1) * 100_
        """)
        
        st.markdown("""
        ### 2. Volatility Score
        | Range | Score | Signal |
        |-------|--------|---------|
        | < 8% | 85 | Strong Sell |
        | 8% to 15% | 65 | Sell |
        | 15% to 25% | 50 | Neutral |
        | 25% to 35% | 25 | Buy |
        | > 35% | 10 | Strong Buy |
        
        _Formula: returns.std() * √252 * 100_
        """)
        
        st.markdown("""
        ### 3. Performance Score
        | Range | Score | Signal |
        |-------|--------|---------|
        | > +25% | 90 | Strong Sell |
        | +10% to +25% | 70 | Sell |
        | -5% to +10% | 50 | Neutral |
        | -20% to -5% | 25 | Buy |
        | < -20% | 10 | Strong Buy |
        
        _Formula: (1_month_return + 3_month_return) / 2_
        """)
        
        st.markdown("""
        ### 4. Volume Score
        | Range | Score | Signal |
        |-------|--------|---------|
        | > +50% & ↑ price | 80 | Strong Sell |
        | > +20% | 65 | Sell |
        | -20% to +20% | 50 | Neutral |
        | < -20% | 35 | Buy |
        
        _Formula: ((recent_volume / 20day_avg_volume) - 1) * 100_
        """)
        
        # Options Market Section
        st.write("## Options Market Data (25% Weight)")
        st.markdown("""
        ### 1. Put/Call Ratio Score
        | Range | Score | Signal |
        |-------|--------|---------|
        | > 1.0 | 20 | Buy (Bearish sentiment) |
        | 0.7 - 1.0 | 40 | Slightly Bearish |
        | 0.5 - 0.7 | 50 | Neutral |
        | 0.3 - 0.5 | 60 | Slightly Bullish |
        | < 0.3 | 80 | Sell (Bullish sentiment) |
        """)
        
        st.markdown("""
        ### 2. VIX Level Score
        | Range | Score | Signal |
        |-------|--------|---------|
        | > 35 | 20 | Buy (High Fear) |
        | 25 - 35 | 40 | Moderate Fear |
        | 15 - 25 | 50 | Neutral |
        | 10 - 15 | 70 | Low Fear |
        | < 10 | 90 | Sell (Complacency) |
        """)
        
        # Sentiment Surveys Section
        st.write("## Sentiment Surveys (25% Weight)")
        st.markdown("""
        ### AAII & UMich Sentiment
        | Percentile | Score | Signal |
        |------------|--------|---------|
        | > 80th | 80 | Sell |
        | 60th - 80th | 65 | Slightly Bearish |
        | 40th - 60th | 50 | Neutral |
        | 20th - 40th | 35 | Slightly Bullish |
        | < 20th | 20 | Buy |
        """)
        
        # Fund Flows Section
        st.write("## Fund Flows (20% Weight)")
        st.markdown("""
        ### ETF Premium/Discount
        | Premium to NAV | Score | Signal |
        |----------------|--------|---------|
        | > +2% | 80 | Sell |
        | +1% to +2% | 65 | Slightly Bearish |
        | -1% to +1% | 50 | Neutral |
        | -2% to -1% | 35 | Slightly Bullish |
        | < -2% | 20 | Buy |
        """)
        
        # Final Score Section
        st.write("## Final Score Interpretation")
        st.markdown("""
        | Score Range | Signal | Market Psychology |
        |-------------|--------|-------------------|
        | 80-100 | Strong Sell | Maximum Euphoria |
        | 60-80 | Sell | Optimistic |
        | 40-60 | Neutral | Balanced |
        | 20-40 | Buy | Pessimistic |
        | 0-20 | Strong Buy | Maximum Fear |
        """)
        
        st.write("## Score Calculation")
        st.code("""
final_score = (
    market_data_score * 0.30 +
    options_score * 0.25 +
    sentiment_survey_score * 0.25 +
    fund_flow_score * 0.20
)
        """)
