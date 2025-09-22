# AI Financial Analyst

An automated stock analysis system that collects data from Yahoo Finance, performs financial analysis, and generates AI-powered investment recommendations using Claude.

## Features

- **Data Collection**: Automated data collection from Yahoo Finance API
- **Financial Analysis**: 3-year revenue growth (CAGR) and EBIT margin trend analysis
- **Stock Ranking**: Comprehensive scoring system based on growth and profitability metrics
- **AI Recommendations**: Investment recommendations generated using Claude AI
- **Interactive Frontend**: User-friendly Streamlit interface
- **Data Storage**: SQLite database for persistent data storage

## Workflow

1. **Data Collection**: Fetch 3 years of financial data from Yahoo Finance
2. **Financial Analysis**: Calculate revenue growth rates and EBIT margin trends
3. **Ranking**: Score and rank stocks based on financial performance
4. **AI Insights**: Generate investment recommendations using Claude API

## Setup Instructions

### 1. Install Dependencies

```bash
conda create -n agent python=3.12
conda activate agent
pip install -r requirements.txt
```

### 2. Configure API Key

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Add your Claude API key to the `.env` file:
```
ANTHROPIC_API_KEY=your_claude_api_key_here
```

### 3. Run the Application

```bash
streamlit run app.py
```

The application will open in your web browser at `http://localhost:8501`

## Usage

1. **Enter Stock Symbols**: In the sidebar, enter comma-separated stock symbols (e.g., AAPL, MSFT, GOOGL)
2. **Analyze**: Click the "Analyze Stocks" button to start the analysis
3. **Review Results**: View financial metrics, rankings, and visualizations
4. **Get AI Recommendations**: Generate detailed investment recommendations

## Project Structure

```
hw2/
├── app.py                 # Main Streamlit application
├── database.py           # SQLite database operations
├── data_collector.py     # Yahoo Finance data collection
├── financial_analyzer.py # Financial analysis and ranking
├── claude_integration.py # Claude AI integration
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## Analysis Metrics

### Revenue Growth
- Calculates 3-year Compound Annual Growth Rate (CAGR)
- Scoring: 20%+ excellent, 10-20% good, 5-10% moderate, <5% low

### EBIT Margin Analysis
- Tracks profitability trends over 3 years
- Analyzes margin progression (improving/stable/declining)
- Considers average margin levels

### Ranking System
- **Revenue Growth**: 0-50 points
- **EBIT Margin Average**: 0-30 points
- **EBIT Margin Trend**: 0-20 points
- **Total Score**: 0-100 points

## API Integration

### Yahoo Finance
- Uses `yfinance` library for financial data
- Collects revenue and operating income data
- Handles data validation and error cases

### Claude AI
- Generates investment recommendations
- Provides portfolio allocation suggestions
- Creates detailed stock analysis summaries

## Database Schema

### Tables
- **stocks**: Basic stock information
- **financial_data**: 3 years of financial metrics
- **analysis_results**: Calculated analysis and rankings

## Limitations

- Relies on Yahoo Finance data availability
- Analysis limited to last 3 years of data
- EBIT calculations may vary based on financial statement formats
- Requires active internet connection for data collection

## Requirements

- Python 3.8+
- Internet connection for data collection
- Claude API key for AI recommendations
- Modern web browser for Streamlit interface
