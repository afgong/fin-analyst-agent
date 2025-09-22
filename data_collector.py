import yfinance as yf
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np

class YahooFinanceCollector:
    def __init__(self):
        self.current_year = datetime.now().year

    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Get basic stock information"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return {
                'symbol': symbol.upper(),
                'company_name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown')
            }
        except Exception as e:
            print(f"Error fetching info for {symbol}: {e}")
            return {'symbol': symbol.upper(), 'company_name': symbol}

    def get_fundamental_data(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Collect last 4 quarters of fundamental data
        """
        try:
            stock = yf.Ticker(symbol)

            # Get quarterly financial statements
            quarterly_financials = stock.quarterly_financials
            quarterly_balance_sheet = stock.quarterly_balance_sheet

            if quarterly_financials.empty:
                print(f"No quarterly financial data available for {symbol}")
                return []

            fundamental_data = []

            # Get the last 4 quarters of data
            quarters = quarterly_financials.columns[:4]  # Most recent 4 quarters

            for quarter in quarters:
                # Get financial statement data
                income_data = quarterly_financials[quarter] if quarter in quarterly_financials.columns else pd.Series()
                balance_data = quarterly_balance_sheet[quarter] if quarter in quarterly_balance_sheet.columns else pd.Series()

                # Extract financial metrics
                revenue = self._extract_revenue(income_data)
                operating_income = self._extract_ebit(income_data)
                net_income = self._extract_net_income(income_data)

                # Balance sheet items
                total_assets = self._extract_total_assets(balance_data)
                total_debt = self._extract_total_debt(balance_data)
                shareholders_equity = self._extract_shareholders_equity(balance_data)
                cash_and_equivalents = self._extract_cash(balance_data)

                # Calculate ratios
                ebit_margin = (operating_income / revenue * 100) if revenue and operating_income else None
                roe = (net_income / shareholders_equity * 100) if net_income and shareholders_equity else None
                debt_to_equity = (total_debt / shareholders_equity) if total_debt and shareholders_equity else None

                # Determine quarter and year
                quarter_str = f"Q{quarter.quarter}"
                year = quarter.year

                fundamental_data.append({
                    'quarter': quarter_str,
                    'year': year,
                    'revenue': revenue,
                    'operating_income': operating_income,
                    'net_income': net_income,
                    'total_assets': total_assets,
                    'total_debt': total_debt,
                    'shareholders_equity': shareholders_equity,
                    'cash_and_equivalents': cash_and_equivalents,
                    'ebit_margin': ebit_margin,
                    'roe': roe,
                    'debt_to_equity': debt_to_equity
                })

            return fundamental_data

        except Exception as e:
            print(f"Error fetching fundamental data for {symbol}: {e}")
            return []

    def _extract_revenue(self, year_data: pd.Series) -> Optional[float]:
        """Extract revenue from financial data"""
        revenue_keys = [
            'Total Revenue',
            'Revenue',
            'Net Sales',
            'Total Net Sales'
        ]

        for key in revenue_keys:
            if key in year_data.index and pd.notna(year_data[key]):
                return float(year_data[key])

        return None

    def _extract_ebit(self, data: pd.Series) -> Optional[float]:
        """Extract EBIT (Operating Income) from financial data"""
        ebit_keys = [
            'Operating Income',
            'EBIT',
            'Operating Revenue',
            'Income From Operations'
        ]

        for key in ebit_keys:
            if key in data.index and pd.notna(data[key]):
                return float(data[key])

        return None

    def _extract_net_income(self, data: pd.Series) -> Optional[float]:
        """Extract net income from financial data"""
        net_income_keys = [
            'Net Income',
            'Net Income Common Stockholders',
            'Net Income Continuing Operations'
        ]

        for key in net_income_keys:
            if key in data.index and pd.notna(data[key]):
                return float(data[key])

        return None

    def _extract_total_assets(self, data: pd.Series) -> Optional[float]:
        """Extract total assets from balance sheet data"""
        assets_keys = [
            'Total Assets',
            'Total Asset'
        ]

        for key in assets_keys:
            if key in data.index and pd.notna(data[key]):
                return float(data[key])

        return None

    def _extract_total_debt(self, data: pd.Series) -> Optional[float]:
        """Extract total debt from balance sheet data"""
        debt_keys = [
            'Total Debt',
            'Long Term Debt',
            'Net Debt'
        ]

        for key in debt_keys:
            if key in data.index and pd.notna(data[key]):
                return float(data[key])

        return None

    def _extract_shareholders_equity(self, data: pd.Series) -> Optional[float]:
        """Extract shareholders equity from balance sheet data"""
        equity_keys = [
            'Stockholders Equity',
            'Total Stockholder Equity',
            'Shareholders Equity'
        ]

        for key in equity_keys:
            if key in data.index and pd.notna(data[key]):
                return float(data[key])

        return None

    def _extract_cash(self, data: pd.Series) -> Optional[float]:
        """Extract cash and cash equivalents from balance sheet data"""
        cash_keys = [
            'Cash And Cash Equivalents',
            'Cash',
            'Cash Cash Equivalents And Short Term Investments'
        ]

        for key in cash_keys:
            if key in data.index and pd.notna(data[key]):
                return float(data[key])

        return None

    def validate_symbols(self, symbols: List[str]) -> List[str]:
        """Validate that stock symbols exist and return valid ones"""
        valid_symbols = []

        for symbol in symbols:
            try:
                stock = yf.Ticker(symbol)
                info = stock.info

                # Check if the ticker is valid
                if 'symbol' in info or 'shortName' in info:
                    valid_symbols.append(symbol.upper())
                else:
                    print(f"Warning: {symbol} may not be a valid ticker")

            except Exception as e:
                print(f"Error validating {symbol}: {e}")

        return valid_symbols

    def get_daily_price_data(self, symbol: str) -> pd.DataFrame:
        """Get 4 years of daily stock price data with moving averages"""
        try:
            stock = yf.Ticker(symbol)

            # Get 4 years of daily data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=4*365)

            hist = stock.history(start=start_date, end=end_date)

            if hist.empty:
                print(f"No price data available for {symbol}")
                return pd.DataFrame()

            # Calculate moving averages
            hist['MA_20'] = hist['Close'].rolling(window=20).mean()
            hist['MA_50'] = hist['Close'].rolling(window=50).mean()
            hist['MA_200'] = hist['Close'].rolling(window=200).mean()

            # Clean up the dataframe
            hist = hist.dropna(subset=['MA_200'])  # Only keep rows with 200-day MA calculated

            return hist

        except Exception as e:
            print(f"Error fetching price data for {symbol}: {e}")
            return pd.DataFrame()

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current stock price"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1d")

            if not hist.empty:
                return float(hist['Close'].iloc[-1])
            return None

        except Exception as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return None

    def collect_bulk_data(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Collect comprehensive data for multiple stocks"""
        results = {}

        for symbol in symbols:
            print(f"Collecting data for {symbol}...")

            stock_info = self.get_stock_info(symbol)
            fundamental_data = self.get_fundamental_data(symbol)
            price_data = self.get_daily_price_data(symbol)
            current_price = self.get_current_price(symbol)

            results[symbol.upper()] = {
                'info': stock_info,
                'fundamental_data': fundamental_data,
                'price_data': price_data,
                'current_price': current_price
            }

        return results