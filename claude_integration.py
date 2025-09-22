import os
from typing import Dict, List, Any
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ClaudeAnalyst:
    def __init__(self, api_key: str = None):
        """
        Initialize Claude integration for investment recommendations
        """
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv('ANTHROPIC_API_KEY')

        if not self.api_key:
            raise ValueError("Claude API key not found. Please set ANTHROPIC_API_KEY in your .env file")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate_investment_recommendation(self, ranked_stocks: List[Dict[str, Any]], model: str = "claude-3-haiku-20240307") -> str:
        """
        Generate investment recommendation using Claude based on stock analysis
        """
        # Prepare the analysis data for Claude
        analysis_summary = self._prepare_analysis_summary(ranked_stocks)

        prompt = f"""
As a financial analyst, please provide an investment recommendation based on the following stock analysis data:

{analysis_summary}

Please provide:
1. An overall investment recommendation (Buy, Hold, or Avoid) for each stock
2. A portfolio allocation suggestion if investing in multiple stocks
3. Key risks and opportunities identified
4. Summary rationale for your recommendations

Please format your response as a professional investment report suitable for presentation to investment committee.
"""

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.content[0].text

        except Exception as e:
            error_msg = f"Claude API Error: {str(e)}"
            print(f"Full error details: {e}")
            return error_msg

    def generate_individual_stock_summary(self, stock_analysis: Dict[str, Any],
                                        market_context: str = "") -> str:
        """
        Generate a detailed summary for an individual stock
        """
        prompt = f"""
As a financial analyst, provide a detailed investment analysis for the following stock:

Stock Symbol: {stock_analysis['symbol']}
3-Year Revenue Growth (CAGR): {stock_analysis.get('revenue_growth_3yr', 'N/A')}%
Average EBIT Margin: {stock_analysis.get('avg_ebit_margin', 'N/A')}%
EBIT Margin Trend: {stock_analysis.get('ebit_margin_trend', 'N/A')}
Overall Ranking Score: {stock_analysis.get('ranking_score', 'N/A')}/100

{market_context}

Please provide:
1. Investment thesis (2-3 sentences)
2. Key strengths and weaknesses
3. Risk factors to consider
4. Price target recommendation (qualitative)
5. Overall rating: Strong Buy / Buy / Hold / Sell / Strong Sell

Keep the analysis concise but professional.
"""

        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.content[0].text

        except Exception as e:
            return f"Error generating stock summary: {str(e)}"

    def _prepare_analysis_summary(self, ranked_stocks: List[Dict[str, Any]]) -> str:
        """
        Prepare a formatted summary of all stock analyses for Claude
        """
        summary_lines = ["STOCK ANALYSIS SUMMARY", "=" * 50, ""]

        for stock in ranked_stocks:
            summary_lines.extend([
                f"Stock: {stock['symbol']} (Rank #{stock.get('rank', 'N/A')})",
                f"  3-Year Revenue Growth: {stock.get('revenue_growth_3yr', 'N/A')}%",
                f"  Average EBIT Margin: {stock.get('avg_ebit_margin', 'N/A')}%",
                f"  EBIT Margin Trend: {stock.get('ebit_margin_trend', 'N/A')}",
                f"  Overall Score: {stock.get('ranking_score', 'N/A')}/100",
                ""
            ])

        return "\n".join(summary_lines)

    def generate_portfolio_strategy(self, top_stocks: List[Dict[str, Any]],
                                  investment_amount: float = 100000) -> str:
        """
        Generate a portfolio allocation strategy
        """
        prompt = f"""
As a portfolio manager, create an investment strategy for a ${investment_amount:,.0f} portfolio based on these top-ranked stocks:

{self._prepare_analysis_summary(top_stocks[:5])}  # Top 5 stocks only

Provide:
1. Recommended portfolio allocation (% for each stock)
2. Rationale for allocation weights
3. Risk management considerations
4. Rebalancing timeline recommendations
5. Expected portfolio characteristics (growth vs value, risk level)

Format as a professional portfolio strategy document.
"""

        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.content[0].text

        except Exception as e:
            return f"Error generating portfolio strategy: {str(e)}"