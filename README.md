# 🏦 BofA Risk-Love Sentiment Analysis

Professional contrarian sentiment analysis system replicating Bank of America's famous Risk-Love indicator methodology.

## 🎯 What This Does

This system provides **real-time contrarian trading signals** based on BofA's 35-indicator sentiment framework:

- **🟢 0-20th Percentile = PANIC = BUY Signal** (Maximum opportunity)
- **🔴 80-100th Percentile = EUPHORIA = SELL Signal** (Maximum risk)

## 🚀 Quick Start

### Launch the Web App
```bash
streamlit run sentiment_analysis_app.py
```
**Or use the one-click launcher:**
```bash
./start_app.sh
```

Access at: **http://localhost:8501**

## 📊 Features

- **Real-time market data** from 15+ global markets
- **Professional heatmap** visualization matching BofA's format
- **Interactive market selection** and analysis
- **Trading signal alerts** for extreme sentiment levels
- **Detailed technical indicators** for each market

## 🎭 Market Coverage

🌍 **Global** • 🇯🇵 **Japan** • 🇨🇳 **China** • 🇮🇳 **India** • 🌏 **Emerging Markets**  
🇹🇼 **Taiwan** • 🇰🇷 **Korea** • 🇭🇰 **Hong Kong** • 🇸🇬 **Singapore** • 🇮🇩 **Indonesia**  
🇧🇷 **Brazil** • 🇲🇽 **Mexico** • 🇿🇦 **South Africa** • 🇹🇷 **Türkiye**

## 🧠 Methodology

Based on BofA's 35-indicator contrarian framework across 5 categories:

| **Category** | **Weight** | **Purpose** |
|-------------|-----------|-------------|
| **Positioning** | 20% | Fund flows, institutional exposure |
| **Put/Call Ratios** | 25% | Options market fear/greed levels |
| **Surveys** | 30% | Professional & retail sentiment |
| **Technicals** | 15% | Market momentum & trends |
| **Volatility/Spreads** | 10% | Market stress indicators |

## 📈 How to Trade

### Entry Signals
- **Markets at 0-20th percentile:** Start accumulating positions
- **High volume + negative sentiment:** Best contrarian opportunities
- **Multiple markets in panic:** Systematic buying opportunities

### Exit Signals  
- **Markets at 80-100th percentile:** Take profits, reduce risk
- **Low volatility + high sentiment:** Peak complacency conditions
- **Multiple markets euphoric:** Systematic risk reduction

## 🔧 Installation

```bash
# Clone/download the project
cd NUSSIF

# Install dependencies
pip install -r requirements.txt

# Launch app
streamlit run sentiment_analysis_app.py
```

## 📱 Deployment

### Streamlit Cloud (Free)
1. Push to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Deploy `sentiment_analysis_app.py`

### Local Network Access
```bash
streamlit run sentiment_analysis_app.py --server.address 0.0.0.0
```


- Conduct your own research
- Use proper risk management  
- Consider multiple indicators
- Consult financial professionals

## 🎯 Pro Tips

- **Best signals:** Extreme percentiles (0-20 and 80-100)
- **Risk management:** Never bet everything on sentiment alone
- **Timing:** Combine with technical analysis for entries/exits
- **Diversification:** Don't concentrate in one market

---

**🏆 Built with:** Python • Streamlit • Yahoo Finance • BofA Methodology  
**📊 Powered by:** Professional contrarian analysis framework  
**🎯 Purpose:** Educational market sentiment analysis
