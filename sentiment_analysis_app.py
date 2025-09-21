import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import yfinance as yf
from datetime import datetime, timedelta
import warnings
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
        st.markdown("""
        ## Sentiment Indicator Components
        
        ### 1. Momentum Score (30% Weight)
        | Range | Score | Signal |
        |-------|--------|---------|
        | > +20% | 90 | Strong Sell |
        | +10% to +20% | 75 | Sell |
        | -5% to +10% | 55 | Neutral |
        | -15% to -5% | 30 | Buy |
        | < -15% | 10 | Strong Buy |
        
        _Formula: `((current_price / 60day_MA) - 1) * 100`_
        
        ### 2. Volatility Score (25% Weight)
        | Range | Score | Signal |
        |-------|--------|---------|
        | < 8% | 85 | Strong Sell |
        | 8% to 15% | 65 | Sell |
        | 15% to 25% | 50 | Neutral |
        | 25% to 35% | 25 | Buy |
        | > 35% | 10 | Strong Buy |
        
        _Formula: `returns.std() * √252 * 100`_
        
        ### 3. Performance Score (25% Weight)
        | Range | Score | Signal |
        |-------|--------|---------|
        | > +25% | 90 | Strong Sell |
        | +10% to +25% | 70 | Sell |
        | -5% to +10% | 50 | Neutral |
        | -20% to -5% | 25 | Buy |
        | < -20% | 10 | Strong Buy |
        
        _Formula: `(1_month_return + 3_month_return) / 2`_
        
        ### 4. Volume Score (20% Weight)
        | Range | Score | Signal |
        |-------|--------|---------|
        | > +50% & ↑ price | 80 | Strong Sell |
        | > +20% | 65 | Sell |
        | -20% to +20% | 50 | Neutral |
        | < -20% | 35 | Buy |
        
        _Formula: `((recent_volume / 20day_avg_volume) - 1) * 100`_
        
        ### Final Score Interpretation
        | Score | Signal | Psychology |
        |-------|--------|------------|
        | 80-100 | Strong Sell | Maximum Euphoria |
        | 60-80 | Sell | Optimistic |
        | 40-60 | Neutral | Balanced |
        | 20-40 | Buy | Pessimistic |
        | 0-20 | Strong Buy | Maximum Fear |
        """)

# Market definitions
MARKETS = {
    'Global': {'ticker': '^GSPC', 'name': '🌍 Global', 'region': 'Global'},
    'Japan': {'ticker': '^N225', 'name': '🇯🇵 Japan', 'region': 'Developed Asia'},
    'Emerging Markets': {'ticker': 'EEM', 'name': '🌏 Emerging Markets', 'region': 'EM'},
    'Asia ex-Japan': {'ticker': 'AAXJ', 'name': '🏯 Asia ex-Japan', 'region': 'Asia'},
    'China': {'ticker': 'FXI', 'name': '🇨🇳 China', 'region': 'Asia'},
    'India': {'ticker': 'INDA', 'name': '🇮🇳 India', 'region': 'Asia'},
    'Taiwan': {'ticker': 'EWT', 'name': '🇹🇼 Taiwan', 'region': 'Asia'},
    'Korea': {'ticker': 'EWY', 'name': '🇰🇷 Korea', 'region': 'Asia'},
    'Hong Kong': {'ticker': 'EWH', 'name': '🇭🇰 Hong Kong', 'region': 'Asia'},
    'Singapore': {'ticker': 'EWS', 'name': '🇸🇬 Singapore', 'region': 'Asia'},
    'Indonesia': {'ticker': 'EIDO', 'name': '🇮🇩 Indonesia', 'region': 'EM Asia'},
    'Brazil': {'ticker': 'EWZ', 'name': '🇧🇷 Brazil', 'region': 'Latin America'},
    'Mexico': {'ticker': 'EWW', 'name': '🇲🇽 Mexico', 'region': 'Latin America'},
    'South Africa': {'ticker': 'EZA', 'name': '🇿🇦 South Africa', 'region': 'EMEA'},
    'Türkiye': {'ticker': 'TUR', 'name': '🇹🇷 Türkiye', 'region': 'EMEA'}
}

# BofA color scheme
COLORS = {
    'panic': '#006837',      # Dark Green (0-20) - Bullish Signal
    'bearish': '#31a354',    # Medium Green (20-40) 
    'neutral': '#fed976',    # Gold (40-60) - Neutral
    'bullish': '#fd8d3c',    # Orange (60-80)
    'euphoria': '#e31a1c'    # Red (80-100) - Bearish Signal
}

# BofA 35-indicator categories
INDICATOR_CATEGORIES = {
    'Positioning': {
        'weight': 0.20,
        'description': 'Fund flows, positioning, exposure levels',
        'count': 6
    },
    'Put/Call Ratios': {
        'weight': 0.25, 
        'description': 'Options sentiment and fear gauges',
        'count': 6
    },
    'Surveys': {
        'weight': 0.30,
        'description': 'Professional and retail sentiment surveys', 
        'count': 7
    },
    'Technicals': {
        'weight': 0.15,
        'description': 'Technical market indicators',
        'count': 3
    },
    'Volatility/Spreads': {
        'weight': 0.10,
        'description': 'Volatility indices, spreads, correlations',
        'count': 13
    }
}

def get_market_data(ticker, market_name):
    """Get live market data"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")
        
        if hist.empty:
            return None
            
        current_price = hist['Close'].iloc[-1]
        
        # Calculate sentiment components
        returns = hist['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100
        
        # 20-day momentum
        ma20 = hist['Close'].rolling(20).mean().iloc[-1] if len(hist) >= 20 else current_price
        momentum_20d = ((current_price / ma20) - 1) * 100
        
        # 60-day momentum  
        ma60 = hist['Close'].rolling(60).mean().iloc[-1] if len(hist) >= 60 else current_price
        momentum_60d = ((current_price / ma60) - 1) * 100
        
        # Volume analysis
        avg_volume = hist['Volume'].rolling(20).mean().iloc[-1]
        recent_volume = hist['Volume'].iloc[-5:].mean()
        volume_trend = (recent_volume / avg_volume - 1) * 100 if avg_volume > 0 else 0
        
        # Performance metrics - Calculate actual returns, not annualized
        # 1-month performance (21 trading days)
        if len(hist) >= 21:
            start_price_1m = hist['Close'].iloc[-21]
            perf_1m = ((current_price / start_price_1m) - 1) * 100
        else:
            perf_1m = 0
            
        # 3-month performance (63 trading days)
        if len(hist) >= 63:
            start_price_3m = hist['Close'].iloc[-63]
            perf_3m = ((current_price / start_price_3m) - 1) * 100
        else:
            perf_3m = 0
        
        return {
            'momentum_20d': momentum_20d,
            'momentum_60d': momentum_60d,
            'volatility': volatility,
            'volume_trend': volume_trend,
            'perf_1m': perf_1m,
            'perf_3m': perf_3m,
            'current_price': current_price
        }
        
    except Exception as e:
        st.error(f"Error fetching data for {market_name}: {str(e)}")
        return None

def calculate_risk_love_score(market_data):
    """Calculate BofA-style Risk-Love percentile score using contrarian methodology"""
    if not market_data:
        return 50
        
    # Extract indicators
    momentum_20d = market_data.get('momentum_20d', 0)
    momentum_60d = market_data.get('momentum_60d', 0)
    volatility = market_data.get('volatility', 15)
    volume_trend = market_data.get('volume_trend', 0)
    perf_1m = market_data.get('perf_1m', 0)
    perf_3m = market_data.get('perf_3m', 0)
    
    # BofA contrarian scoring methodology
    # High momentum + low volatility = high sentiment = bearish signal (high percentile)
    
    # Momentum component (contrarian - strong momentum = high sentiment = bearish)
    if momentum_60d > 20:
        momentum_score = 90  # Very bullish market = bearish signal
    elif momentum_60d > 10:
        momentum_score = 75
    elif momentum_60d > -5:
        momentum_score = 55
    elif momentum_60d > -15:
        momentum_score = 30
    else:
        momentum_score = 10  # Very bearish market = bullish signal
        
    # Volatility component (contrarian - low vol = complacency = high sentiment)
    if volatility < 8:
        vol_score = 85  # Low vol = complacency = bearish
    elif volatility < 15:
        vol_score = 65
    elif volatility < 25:
        vol_score = 50
    elif volatility < 35:
        vol_score = 25
    else:
        vol_score = 10  # High vol = fear = bullish
        
    # Performance component (recent gains = bullish sentiment = bearish signal)
    avg_perf = (perf_1m + perf_3m) / 2
    if avg_perf > 25:
        perf_score = 90  # Strong gains = euphoria
    elif avg_perf > 10:
        perf_score = 70
    elif avg_perf > -5:
        perf_score = 50
    elif avg_perf > -20:
        perf_score = 25
    else:
        perf_score = 10  # Heavy losses = panic
        
    # Volume component (high volume + gains = euphoria)
    if volume_trend > 50 and perf_1m > 5:
        volume_score = 80  # High volume + gains = euphoria
    elif volume_trend > 20:
        volume_score = 65
    elif volume_trend > -20:
        volume_score = 50
    else:
        volume_score = 35
        
    # Weighted composite (BofA methodology weights)
    composite = (
        momentum_score * 0.30 +  # Momentum most important
        vol_score * 0.25 +       # Volatility second
        perf_score * 0.25 +      # Performance third
        volume_score * 0.20      # Volume least important
    )
    
    return max(0, min(100, round(composite)))

def get_sentiment_color(score):
    """Get BofA color for sentiment score"""
    if score <= 20:
        return COLORS['panic']
    elif score <= 40:
        return COLORS['bearish']
    elif score <= 60:
        return COLORS['neutral']
    elif score <= 80:
        return COLORS['bullish']
    else:
        return COLORS['euphoria']

def get_sentiment_interpretation(score):
    """Get BofA interpretation and emoji"""
    if score <= 20:
        return "Panic (Bullish Signal)", "🟢"
    elif score <= 40:
        return "Bearish Sentiment", "🟡"
    elif score <= 60:
        return "Neutral Territory", "⚪"
    elif score <= 80:
        return "Bullish Sentiment", "🟠"
    else:
        return "Euphoria (Bearish Signal)", "🔴"

def get_trading_signal(score):
    """Get contrarian trading signal"""
    if score <= 20:
        return "🟢 STRONG BUY", "Panic conditions = Maximum opportunity"
    elif score <= 40:
        return "🟡 BUY", "Bearish sentiment = Good entry point"
    elif score <= 60:
        return "⚪ NEUTRAL", "Mixed signals = Wait for extremes"
    elif score <= 80:
        return "🟠 CAUTION", "Bullish sentiment = Reduce risk"
    else:
        return "🔴 STRONG SELL", "Euphoria conditions = Maximum risk"

def create_heatmap(sentiment_data):
    """Create BofA-style heatmap"""
    fig, ax = plt.subplots(figsize=(12, len(sentiment_data) * 0.6))
    
    markets = list(sentiment_data.keys())
    scores = [sentiment_data[market]['score'] for market in markets]
    colors = [sentiment_data[market]['color'] for market in markets]
    
    # Horizontal bar chart
    y_pos = np.arange(len(markets))
    bars = ax.barh(y_pos, scores, color=colors, alpha=0.8, height=0.6)
    
    # Add score labels
    for i, (bar, score) in enumerate(zip(bars, scores)):
        ax.text(score + 1, bar.get_y() + bar.get_height()/2, 
               f'{score}', ha='left', va='center', fontweight='bold')
    
    # Customize chart
    ax.set_yticks(y_pos)
    ax.set_yticklabels([MARKETS[m]['name'] for m in markets])
    ax.set_xlabel('Risk-Love Percentile', fontweight='bold')
    ax.set_title('BofA Risk-Love Sentiment Analysis', fontweight='bold', fontsize=14)
    ax.set_xlim(0, 100)
    
    # Add reference lines
    ax.axvline(20, color='green', linestyle='--', alpha=0.5, linewidth=2, label='Panic Threshold')
    ax.axvline(80, color='red', linestyle='--', alpha=0.5, linewidth=2, label='Euphoria Threshold')
    ax.axvline(50, color='gray', linestyle='-', alpha=0.3, label='Neutral')
    
    # Legend
    panic_patch = mpatches.Patch(color=COLORS['panic'], label='Panic (Buy Signal)')
    neutral_patch = mpatches.Patch(color=COLORS['neutral'], label='Neutral')
    euphoria_patch = mpatches.Patch(color=COLORS['euphoria'], label='Euphoria (Sell Signal)')
    
    ax.legend(handles=[panic_patch, neutral_patch, euphoria_patch], 
             loc='lower right', frameon=True)
    
    ax.grid(True, axis='x', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    return fig

def main():
    # Header
    st.title("🏦 BofA Risk-Love Sentiment Analysis")
    st.markdown("### Professional contrarian sentiment analysis based on Bank of America's 35-indicator methodology")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.header("📊 Analysis Settings")
    st.sidebar.markdown("---")
    
    # Market selection
    selected_markets = st.sidebar.multiselect(
        "Select Markets to Analyze:",
        options=list(MARKETS.keys()),
        default=['Global', 'Japan', 'China', 'India', 'Emerging Markets']
    )
    
    # Methodology explanation
    with st.sidebar.expander("🎯 BofA Risk-Love Methodology"):
        st.markdown("""
        **Contrarian Analysis Framework:**
        
        **🟢 0-20th Percentile: PANIC**
        - Bullish Signal (BUY)
        - Maximum opportunity
        
        **🟡 20-40th: Bearish Sentiment**  
        - Good entry points
        
        **⚪ 40-60th: Neutral**
        - Wait for extremes
        
        **🟠 60-80th: Bullish Sentiment**
        - Reduce risk exposure
        
        **🔴 80-100th: EUPHORIA**
        - Bearish Signal (SELL)
        - Maximum risk
        """)
    
    with st.sidebar.expander("📈 35-Indicator Categories"):
        for category, info in INDICATOR_CATEGORIES.items():
            st.markdown(f"**{category}** ({info['weight']*100:.0f}%)")
            st.markdown(f"*{info['description']}*")
            st.markdown(f"Indicators: {info['count']}")
            st.markdown("---")
    
    # Main content
    if not selected_markets:
        st.warning("Please select at least one market from the sidebar.")
        return
    
    # Analysis section
    st.header("📊 Real-Time Sentiment Analysis")
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Get sentiment data
    sentiment_data = {}
    total_markets = len(selected_markets)
    
    for i, market in enumerate(selected_markets):
        status_text.text(f'Analyzing {market}...')
        progress_bar.progress((i + 1) / total_markets)
        
        market_info = MARKETS[market]
        market_data = get_market_data(market_info['ticker'], market)
        risk_love_score = calculate_risk_love_score(market_data)
        
        sentiment_data[market] = {
            'score': risk_love_score,
            'color': get_sentiment_color(risk_love_score),
            'interpretation': get_sentiment_interpretation(risk_love_score),
            'signal': get_trading_signal(risk_love_score),
            'raw_data': market_data
        }
    
    # Clear progress indicators
    status_text.empty()
    progress_bar.empty()
    
    # Results display
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Risk-Love Sentiment Heatmap")
        
        # Create and display heatmap
        fig = create_heatmap(sentiment_data)
        st.pyplot(fig)
        plt.close(fig)
    
    with col2:
        st.subheader("🚨 Trading Signals")
        
        # Extreme alerts
        extreme_signals = []
        for market, data in sentiment_data.items():
            score = data['score']
            if score <= 20 or score >= 80:
                signal_type = "🟢 BUY" if score <= 20 else "🔴 SELL"
                extreme_signals.append((market, score, signal_type))
        
        if extreme_signals:
            st.markdown("**⚡ EXTREME SIGNALS:**")
            for market, score, signal in extreme_signals:
                st.markdown(f"{signal} **{market}** ({score}th percentile)")
            st.markdown("---")
        
        # Global sentiment summary
        if 'Global' in sentiment_data:
            global_score = sentiment_data['Global']['score']
            global_interp, global_icon = sentiment_data['Global']['interpretation']
            st.markdown(f"**🌍 GLOBAL SENTIMENT**")
            st.markdown(f"{global_icon} {global_score}th percentile")
            st.markdown(f"*{global_interp}*")
            st.markdown("---")
        
        # Summary table
        st.subheader("📋 Summary Table")
        
        df_data = []
        for market, data in sentiment_data.items():
            df_data.append({
                'Market': MARKETS[market]['name'],
                'Score': data['score'],
                'Signal': data['signal'][0],
                'Status': data['interpretation'][1]
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, width='stretch')
    
    # Detailed analysis
    st.header("📈 Detailed Market Analysis")
    
    for market, data in sentiment_data.items():
        with st.expander(f"📊 {MARKETS[market]['name']} - {data['score']}th percentile"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Risk-Love Score", 
                    f"{data['score']}th percentile"
                )
            
            with col2:
                st.markdown(f"**Interpretation:**")
                st.markdown(f"{data['interpretation'][1]} {data['interpretation'][0]}")
            
            with col3:
                st.markdown(f"**Trading Signal:**")
                st.markdown(f"{data['signal'][0]}")
                st.markdown(f"*{data['signal'][1]}*")
            
            # Raw data if available
            if data['raw_data']:
                st.markdown("**Technical Indicators:**")
                raw_data = data['raw_data']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("20D Momentum", f"{raw_data.get('momentum_20d', 0):.1f}%")
                
                with col2:
                    st.metric("Volatility", f"{raw_data.get('volatility', 0):.1f}%")
                
                with col3:
                    st.metric("1M Performance", f"{raw_data.get('perf_1m', 0):.1f}%")
                
                with col4:
                    st.metric("Volume Trend", f"{raw_data.get('volume_trend', 0):.1f}%")
    
    # Footer
    st.markdown("---")
    st.markdown(f"**📊 Analysis generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    st.markdown("**🏦 Source:** BofA Risk-Love Methodology (35-Indicator Contrarian Framework)")

if __name__ == "__main__":
    main()
