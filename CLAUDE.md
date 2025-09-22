# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered financial analysis application that:
- Collects financial data from Yahoo Finance
- Performs revenue growth and EBIT margin analysis
- Ranks stocks based on financial performance
- Generates AI investment recommendations using Claude API
- Provides a Streamlit web interface for analysis

## Development Commands

### Setup and Installation
```bash
pip install -r requirements.txt
cp .env.example .env
# Add ANTHROPIC_API_KEY to .env file
```

### Running the Application
```bash
streamlit run app.py
```

### Testing Individual Components
```bash
# Test database operations
python -c "from database import FinancialDatabase; db = FinancialDatabase(); print('Database initialized successfully')"

# Test data collection
python -c "from data_collector import YahooFinanceCollector; collector = YahooFinanceCollector(); print(collector.get_stock_info('AAPL'))"

# Test financial analysis
python -c "from financial_analyzer import FinancialAnalyzer; analyzer = FinancialAnalyzer(); print('Analyzer initialized successfully')"
```

## Architecture

### Core Components

1. **Database Layer** (`database.py`)
   - SQLite database with tables for stocks, financial_data, and analysis_results
   - Handles data persistence and retrieval
   - Uses parameterized queries for security

2. **Data Collection** (`data_collector.py`)
   - YahooFinanceCollector class for fetching financial data
   - Extracts revenue and EBIT from Yahoo Finance API
   - Validates stock symbols and handles API errors

3. **Financial Analysis** (`financial_analyzer.py`)
   - Calculates 3-year revenue CAGR
   - Analyzes EBIT margin trends using linear regression
   - Implements scoring system (0-100 points) for stock ranking

4. **AI Integration** (`claude_integration.py`)
   - Claude API integration for investment recommendations
   - Generates portfolio allocation strategies
   - Creates detailed stock analysis summaries

5. **Frontend** (`app.py`)
   - Streamlit web interface
   - Interactive data input and visualization
   - Progress tracking and error handling

### Data Flow

1. User inputs stock symbols via Streamlit interface
2. YahooFinanceCollector fetches 3 years of financial data
3. Data stored in SQLite database
4. FinancialAnalyzer calculates metrics and rankings
5. Results stored and displayed with visualizations
6. Claude API generates investment recommendations

### Key Design Patterns

- **Separation of Concerns**: Each module handles specific functionality
- **Error Handling**: Graceful degradation when data is unavailable
- **Database Persistence**: All data stored for future reference
- **Modular Architecture**: Components can be tested and used independently

## Environment Variables

Required in `.env` file:
- `ANTHROPIC_API_KEY`: Claude API key for investment recommendations

## Dependencies

Key libraries:
- `streamlit`: Web interface framework
- `yfinance`: Yahoo Finance data collection
- `pandas`: Data manipulation and analysis
- `sqlite3`: Database operations (built-in)
- `anthropic`: Claude API client
- `plotly`: Interactive visualizations
- `scipy`: Statistical analysis for trend calculations

## Error Handling

- Yahoo Finance API failures are handled gracefully
- Missing financial data doesn't break the analysis
- Claude API errors show user-friendly messages
- Database operations include try/catch blocks

## Testing Approach

- Manual testing through Streamlit interface
- Component-level testing using Python command line
- Database operations tested with sample data
- API integrations tested with real credentials