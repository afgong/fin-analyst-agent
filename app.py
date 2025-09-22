import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List
import time
import os

# Import our custom modules
from database import FinancialDatabase
from data_collector import YahooFinanceCollector
from financial_analyzer import FinancialAnalyzer
from claude_integration import ClaudeAnalyst

# Page configuration
st.set_page_config(
    page_title="AI Financial Analyst",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analyzed_stocks' not in st.session_state:
    st.session_state.analyzed_stocks = []

def initialize_components():
    """Initialize all components"""
    try:
        db = FinancialDatabase()
        collector = YahooFinanceCollector()
        analyzer = FinancialAnalyzer()
        claude = ClaudeAnalyst()
        return db, collector, analyzer, claude
    except Exception as e:
        st.error(f"Error initializing components: {e}")
        st.info("Make sure you have set up your .env file with ANTHROPIC_API_KEY")
        return None, None, None, None

def validate_and_clean_symbols(symbols_input: str) -> List[str]:
    """Validate and clean stock symbols"""
    if not symbols_input:
        return []

    # Split by comma and clean
    symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]

    # Basic validation
    valid_symbols = []
    for symbol in symbols:
        if len(symbol) <= 5 and symbol.isalpha():
            valid_symbols.append(symbol)
        else:
            st.warning(f"Skipping invalid symbol: {symbol}")

    return valid_symbols

def display_analysis_results(db: FinancialDatabase, claude: ClaudeAnalyst):
    """Display the analysis results"""
    results_df = db.get_all_analysis_results()

    if results_df.empty:
        st.info("No analysis results available. Please analyze some stocks first.")
        return

    st.header("📊 Analysis Results")

    # Display ranking table
    st.subheader("Stock Rankings")

    # Prepare display dataframe
    display_df = results_df.copy()
    display_df['Rank'] = range(1, len(display_df) + 1)

    # Format columns for display
    display_df['Revenue Growth'] = display_df['revenue_growth_4q'].apply(
        lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
    )
    display_df['Avg EBIT Margin'] = display_df['avg_ebit_margin'].apply(
        lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
    )
    display_df['Score'] = display_df['ranking_score'].apply(
        lambda x: f"{x:.1f}" if pd.notna(x) else "N/A"
    )

    # Add simplified analysis columns
    display_df['MA50 Rising'] = results_df.apply(
        lambda row: "✓" if row.get('ma50_rising') else "✗", axis=1
    )
    display_df['Recommendation'] = results_df.get('recommendation', 'N/A')

    # Select columns for display
    table_df = display_df[['Rank', 'symbol', 'Revenue Growth', 'Avg EBIT Margin',
                          'MA50 Rising', 'Score', 'Recommendation']].copy()
    table_df.columns = ['Rank', 'Symbol', 'Revenue Growth (Q)', 'EBIT Margin (%)',
                       'MA50 Rising', 'Score', 'Recommendation']

    st.dataframe(table_df, use_container_width=True)

    # Visualization
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Ranking Scores")
        fig_scores = px.bar(
            results_df,
            x='symbol',
            y='ranking_score',
            title="Stock Ranking Scores",
            color='ranking_score',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig_scores, use_container_width=True)

    with col2:
        st.subheader("Revenue Growth vs EBIT Margin")

        # Filter for stocks with valid data
        valid_data = results_df[
            (results_df['revenue_growth_4q'].notna()) &
            (results_df['avg_ebit_margin'].notna())
        ].copy()

        if not valid_data.empty:
            fig_scatter = px.scatter(
                valid_data,
                x='revenue_growth_4q',
                y='avg_ebit_margin',
                size='ranking_score',
                color='ranking_score',
                hover_name='symbol',
                title="Quarterly Growth vs EBIT Margin",
                color_continuous_scale='RdYlGn',
                labels={'revenue_growth_4q': 'Revenue Growth QoQ (%)', 'avg_ebit_margin': 'EBIT Margin (%)'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("No valid data available for visualization")

    # Claude Analysis
    st.header("🤖 AI Investment Recommendation")

    if st.button("Generate AI Recommendation", type="primary"):
        with st.spinner("Generating AI recommendation..."):
            try:
                # Get selected model from session state
                selected_model = st.session_state.get('selected_claude_model', 'claude-3-haiku-20240307')

                # Convert dataframe to list of dicts for Claude
                stocks_data = results_df.to_dict('records')
                recommendation = claude.generate_investment_recommendation(stocks_data, model=selected_model)
                st.write(recommendation)

                # Show which model was used
                st.info(f"Generated using: {selected_model}")
            except Exception as e:
                st.error(f"Error generating recommendation: {e}")

def run_analysis(symbols: List[str], db: FinancialDatabase,
                collector: YahooFinanceCollector, analyzer: FinancialAnalyzer):
    """Run the complete analysis workflow"""

    # Clear existing database and start fresh
    with st.spinner("Clearing database and preparing for fresh analysis..."):
        db.clear_database()

    progress_bar = st.progress(0)
    status_text = st.empty()

    total_steps = len(symbols) * 3 + 1  # Fundamental + Technical + Analysis + Final ranking

    step = 0

    # Data Collection Phase
    status_text.text("Collecting fundamental and technical data...")
    collected_data = {}

    for i, symbol in enumerate(symbols):
        status_text.text(f"Collecting data for {symbol}...")

        # Get stock info and add to database
        stock_info = collector.get_stock_info(symbol)
        db.add_stock(symbol, stock_info.get('company_name'))

        # Get fundamental data (quarterly)
        fundamental_data = collector.get_fundamental_data(symbol)

        # Get technical data (daily prices with moving averages)
        technical_data = collector.get_daily_price_data(symbol)

        # Get current price
        current_price = collector.get_current_price(symbol)

        if fundamental_data:
            db.store_fundamental_data(symbol, fundamental_data)
            collected_data[symbol] = {
                'fundamental': fundamental_data,
                'technical': technical_data,
                'current_price': current_price
            }
            st.success(f"✅ Fundamental data collected for {symbol}")
        else:
            st.warning(f"⚠️ No fundamental data available for {symbol}")
            collected_data[symbol] = {
                'fundamental': [],
                'technical': pd.DataFrame(),
                'current_price': current_price
            }

        step += 1
        progress_bar.progress(step / total_steps)

        # Store technical data if available
        if not technical_data.empty:
            db.store_technical_data(symbol, technical_data)
            st.success(f"✅ Technical data collected for {symbol}")
        else:
            st.warning(f"⚠️ No technical data available for {symbol}")

        step += 1
        progress_bar.progress(step / total_steps)

    # Analysis Phase
    status_text.text("Performing financial and technical analysis...")

    analysis_results = []

    for i, symbol in enumerate(symbols):
        if symbol in collected_data:
            status_text.text(f"Analyzing {symbol}...")

            # Perform comprehensive analysis
            data = collected_data[symbol]
            analysis = analyzer.analyze_stock(
                symbol,
                data['fundamental'],
                data['technical'],
                data['current_price']
            )
            analysis_results.append(analysis)

            # Store in database
            db.store_analysis_result(symbol, analysis)

            step += 1
            progress_bar.progress(step / total_steps)

    # Ranking Phase
    status_text.text("Ranking stocks...")
    if analysis_results:
        ranked_stocks = analyzer.rank_stocks(analysis_results)
        st.session_state.analyzed_stocks = ranked_stocks

    step += 1
    progress_bar.progress(1.0)

    status_text.text("Analysis complete!")
    st.session_state.analysis_complete = True

def main():
    """Main Streamlit application"""
    st.title("🎯 AI Financial Analyst")
    st.markdown("*Automated stock analysis with AI-powered investment recommendations*")

    # Initialize components
    db, collector, analyzer, claude = initialize_components()

    if None in [db, collector, analyzer, claude]:
        st.stop()

    # Sidebar for input
    with st.sidebar:
        st.header("📝 Stock Input")

        symbols_input = st.text_area(
            "Enter stock symbols (comma-separated):",
            value="AAPL, MSFT, GOOGL, TSLA, NVDA",
            placeholder="AAPL, MSFT, GOOGL, TSLA, NVDA",
            height=100
        )

        st.markdown("**Example symbols:** AAPL, MSFT, GOOGL, TSLA, NVDA, META, AMZN")

        analyze_button = st.button("🚀 Analyze Stocks", type="primary")

        st.markdown("---")

        # Claude Model Selection
        st.header("🤖 Claude Model Settings")

        model_options = {
            "Claude 3 Haiku": "claude-3-haiku-20240307",
            "Claude 3 Sonnet": "claude-3-sonnet-20240229",
            "Claude 3.5 Sonnet (June)": "claude-3-5-sonnet-20240620",
            "Claude 3.5 Sonnet (Oct)": "claude-3-5-sonnet-20241022",
            "Claude 3.5 Sonnet": "claude-3-5-sonnet",
            "Claude 4.0 Sonnet": "claude-4-0-sonnet-20250514"
        }

        selected_model_name = st.selectbox(
            "Select Claude Model:",
            options=list(model_options.keys()),
            index=0,  # Default to Haiku since it works
            help="Choose which Claude model to use for AI recommendations. Start with Haiku and work your way up to test your API access level."
        )

        selected_model = model_options[selected_model_name]

        # Store selected model in session state
        st.session_state.selected_claude_model = selected_model

        st.info(f"Selected: {selected_model}")

        st.markdown("---")

        # API Key status
        if os.getenv('ANTHROPIC_API_KEY'):
            st.success("✅ Claude API key configured")
        else:
            st.error("❌ Claude API key not found")
            st.info("Add ANTHROPIC_API_KEY to your .env file")

    # Main content area
    if analyze_button:
        symbols = validate_and_clean_symbols(symbols_input)

        if not symbols:
            st.error("Please enter valid stock symbols (e.g., AAPL, MSFT)")
        else:
            st.info(f"Analyzing {len(symbols)} stocks: {', '.join(symbols)}")

            # Run analysis
            with st.container():
                run_analysis(symbols, db, collector, analyzer)

    # Display results if analysis is complete
    if st.session_state.analysis_complete:
        display_analysis_results(db, claude)

    # Instructions
    if not st.session_state.analysis_complete:
        st.header("📋 How to Use")
        st.markdown("""
        1. **Enter Stock Symbols**: In the sidebar, enter comma-separated stock symbols
        2. **Click Analyze**: Press the "Analyze Stocks" button to start the analysis
        3. **Review Results**: View financial metrics, rankings, and AI recommendations
        4. **Get AI Insights**: Generate detailed investment recommendations using Claude AI

        **Analysis Includes:**
        - Quarterly revenue growth
        - EBIT margin trends (4 quarters)
        - Technical analysis with moving averages (20, 50, 200-day)
        - Price vs moving average analysis
        - Comprehensive ranking system
        - AI-powered investment recommendations
        """)

        st.header("⚙️ Setup Instructions")
        st.markdown("""
        1. Install dependencies: `pip install -r requirements.txt`
        2. Copy `.env.example` to `.env`
        3. Add your Claude API key to the `.env` file
        4. Run the app: `streamlit run app.py`
        """)

if __name__ == "__main__":
    main()