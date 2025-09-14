#!/bin/bash

# BofA# Launch Streamlit app
echo "🚀 Launching Streamlit app..."
streamlit run sentiment_analysis_app.py --server.port 8501 --server.address 0.0.0.0sk-Love Streamlit App Launcher
echo "🏦 Starting BofA Risk-Love Sentiment Analysis App..."
echo "=============================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Launch Streamlit app
echo "🚀 Launching Streamlit app..."
streamlit run streamlit_bofa_app.py --server.port 8501 --server.address 0.0.0.0

echo "✅ App should be running at http://localhost:8501"
