import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from scipy import stats

class FinancialAnalyzer:
    def __init__(self):
        pass

    def calculate_revenue_growth(self, fundamental_data: List[Dict[str, Any]]) -> Optional[float]:
        """
        Calculate quarterly revenue growth rate (QoQ)
        """
        if len(fundamental_data) < 2:
            return None

        # Sort by year and quarter (newest first)
        sorted_data = sorted(fundamental_data,
                           key=lambda x: (x['year'], x['quarter']),
                           reverse=True)

        revenues = [d['revenue'] for d in sorted_data if d['revenue'] is not None]

        if len(revenues) < 2:
            return None

        # Calculate quarter-over-quarter growth
        try:
            # Compare most recent quarter to previous quarter
            current_quarter = revenues[0]
            previous_quarter = revenues[1]

            if previous_quarter <= 0:
                return None

            qoq_growth = ((current_quarter - previous_quarter) / previous_quarter) * 100
            return round(qoq_growth, 2)
        except:
            return None

    def analyze_ebit_margin_trend(self, fundamental_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get average EBIT margin from last 4 quarters
        """
        if not fundamental_data:
            return {'avg_margin': None}

        margins = [d['ebit_margin'] for d in fundamental_data if d['ebit_margin'] is not None]

        if not margins:
            return {'avg_margin': None}

        avg_margin = np.mean(margins)
        return {'avg_margin': round(avg_margin, 2)}

    def analyze_technical_indicators(self, technical_data: pd.DataFrame, current_price: float) -> Dict[str, Any]:
        """
        Check if MA50 is rising over the last 10 days
        """
        if technical_data.empty or current_price is None:
            return {
                'ma_20': None,
                'ma_50': None,
                'ma_200': None,
                'price_vs_ma20': None,
                'price_vs_ma50': None,
                'price_vs_ma200': None,
                'ma50_rising': False
            }

        try:
            # Get most recent moving averages
            latest_data = technical_data.iloc[-1]
            ma_20 = latest_data['MA_20']
            ma_50 = latest_data['MA_50']
            ma_200 = latest_data['MA_200']

            # Calculate price vs moving averages
            price_vs_ma20 = ((current_price - ma_20) / ma_20 * 100) if pd.notna(ma_20) else None
            price_vs_ma50 = ((current_price - ma_50) / ma_50 * 100) if pd.notna(ma_50) else None
            price_vs_ma200 = ((current_price - ma_200) / ma_200 * 100) if pd.notna(ma_200) else None

            # Check if MA50 is rising (compare last 10 days)
            ma50_rising = False
            if len(technical_data) >= 10 and pd.notna(ma_50):
                ma50_10_days_ago = technical_data.iloc[-10]['MA_50']
                if pd.notna(ma50_10_days_ago) and ma_50 > ma50_10_days_ago:
                    ma50_rising = True

            return {
                'ma_20': round(ma_20, 2) if pd.notna(ma_20) else None,
                'ma_50': round(ma_50, 2) if pd.notna(ma_50) else None,
                'ma_200': round(ma_200, 2) if pd.notna(ma_200) else None,
                'price_vs_ma20': round(price_vs_ma20, 2) if price_vs_ma20 else None,
                'price_vs_ma50': round(price_vs_ma50, 2) if price_vs_ma50 else None,
                'price_vs_ma200': round(price_vs_ma200, 2) if price_vs_ma200 else None,
                'ma50_rising': ma50_rising
            }

        except Exception as e:
            print(f"Error in technical analysis: {e}")
            return {
                'ma_20': None,
                'ma_50': None,
                'ma_200': None,
                'price_vs_ma20': None,
                'price_vs_ma50': None,
                'price_vs_ma200': None,
                'ma50_rising': False
            }

    def calculate_ranking_score(self, revenue_growth: Optional[float],
                              ebit_analysis: Dict[str, Any],
                              technical_analysis: Dict[str, Any]) -> float:
        """
        Simplified ranking based on 3 key criteria:
        1. Revenue growth quarter-over-quarter (40 points)
        2. Highest EBIT margin (40 points)
        3. Rising MA50 (20 points)
        """
        score = 0

        # 1. Revenue growth QoQ scoring (0-40 points)
        if revenue_growth is not None:
            if revenue_growth >= 10:  # Excellent quarterly growth
                score += 40
            elif revenue_growth >= 5:  # Good growth
                score += 30
            elif revenue_growth >= 0:  # Positive growth
                score += 20
            else:  # Negative growth
                score += 0

        # 2. EBIT margin scoring (0-40 points)
        avg_margin = ebit_analysis.get('avg_margin')
        if avg_margin is not None:
            if avg_margin >= 25:  # Excellent margins
                score += 40
            elif avg_margin >= 20:  # Very good margins
                score += 35
            elif avg_margin >= 15:  # Good margins
                score += 30
            elif avg_margin >= 10:  # Moderate margins
                score += 20
            elif avg_margin >= 5:  # Low margins
                score += 10
            else:  # Negative or very low margins
                score += 0

        # 3. Rising MA50 scoring (0-20 points)
        ma50_rising = technical_analysis.get('ma50_rising', False)
        if ma50_rising:
            score += 20

        return round(score, 1)

    def analyze_stock(self, symbol: str, fundamental_data: List[Dict[str, Any]],
                     technical_data: pd.DataFrame, current_price: float) -> Dict[str, Any]:
        """
        Perform simplified analysis for a single stock
        """
        revenue_growth = self.calculate_revenue_growth(fundamental_data)
        ebit_analysis = self.analyze_ebit_margin_trend(fundamental_data)
        technical_analysis = self.analyze_technical_indicators(technical_data, current_price)
        ranking_score = self.calculate_ranking_score(revenue_growth, ebit_analysis, technical_analysis)

        # Generate simple recommendation
        if ranking_score >= 80:
            recommendation = "STRONG BUY"
        elif ranking_score >= 60:
            recommendation = "BUY"
        elif ranking_score >= 40:
            recommendation = "HOLD"
        else:
            recommendation = "SELL"

        return {
            'symbol': symbol,
            'revenue_growth_4q': revenue_growth,
            'avg_ebit_margin': ebit_analysis.get('avg_margin'),
            'current_price': current_price,
            'ma_20': technical_analysis.get('ma_20'),
            'ma_50': technical_analysis.get('ma_50'),
            'ma_200': technical_analysis.get('ma_200'),
            'price_vs_ma20': technical_analysis.get('price_vs_ma20'),
            'price_vs_ma50': technical_analysis.get('price_vs_ma50'),
            'price_vs_ma200': technical_analysis.get('price_vs_ma200'),
            'ma50_rising': technical_analysis.get('ma50_rising'),
            'ebit_trend_details': ebit_analysis,
            'technical_details': technical_analysis,
            'ranking_score': ranking_score,
            'recommendation': recommendation
        }

    def rank_stocks(self, analysis_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank stocks based on their analysis scores
        """
        # Sort by ranking score (highest first)
        ranked_stocks = sorted(analysis_results,
                             key=lambda x: x['ranking_score'],
                             reverse=True)

        # Add rank position
        for i, stock in enumerate(ranked_stocks):
            stock['rank'] = i + 1

        return ranked_stocks

    def generate_analysis_summary(self, analysis: Dict[str, Any]) -> str:
        """
        Generate simplified analysis summary based on 3 key criteria
        """
        symbol = analysis['symbol']
        revenue_growth = analysis['revenue_growth_4q']
        avg_margin = analysis['avg_ebit_margin']
        score = analysis['ranking_score']
        recommendation = analysis['recommendation']

        # Get MA50 rising status from technical details
        ma50_rising = analysis.get('ma50_rising', False)

        summary_parts = [f"Stock: {symbol}"]

        # Revenue growth (QoQ)
        if revenue_growth is not None:
            summary_parts.append(f"Revenue growth QoQ: {revenue_growth}%")
        else:
            summary_parts.append("Revenue growth: No data")

        # EBIT margin
        if avg_margin is not None:
            summary_parts.append(f"EBIT margin: {avg_margin}%")
        else:
            summary_parts.append("EBIT margin: No data")

        # MA50 trend
        if ma50_rising:
            summary_parts.append("MA50: Rising ✓")
        else:
            summary_parts.append("MA50: Not rising")

        summary_parts.append(f"Score: {score}/100 - {recommendation}")

        return ". ".join(summary_parts) + "."