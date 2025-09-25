import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

class FinancialDatabase:
    def __init__(self, db_path: str = "financial_data.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create stocks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                company_name TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create fundamental_data table (quarterly data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fundamental_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                quarter TEXT NOT NULL,
                year INTEGER NOT NULL,
                revenue REAL,
                operating_income REAL,
                net_income REAL,
                total_assets REAL,
                total_debt REAL,
                shareholders_equity REAL,
                cash_and_equivalents REAL,
                ebit_margin REAL,
                roe REAL,
                debt_to_equity REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES stocks (symbol),
                UNIQUE(symbol, quarter, year)
            )
        """)

        # Create technical_data table (daily price data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS technical_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date DATE NOT NULL,
                open_price REAL,
                high_price REAL,
                low_price REAL,
                close_price REAL,
                volume INTEGER,
                adj_close REAL,
                ma_20 REAL,
                ma_50 REAL,
                ma_200 REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES stocks (symbol),
                UNIQUE(symbol, date)
            )
        """)

        # Create analysis_results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                revenue_growth_4q REAL,
                avg_ebit_margin REAL,
                ebit_margin_trend TEXT,
                current_price REAL,
                ma_20 REAL,
                ma_50 REAL,
                ma_200 REAL,
                price_vs_ma20 REAL,
                price_vs_ma50 REAL,
                price_vs_ma200 REAL,
                ranking_score REAL,
                recommendation TEXT,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES stocks (symbol)
            )
        """)

        conn.commit()
        conn.close()

    def add_stock(self, symbol: str, company_name: str = None):
        """Add a stock to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO stocks (symbol, company_name, last_updated)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (symbol.upper(), company_name))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding stock {symbol}: {e}")
        finally:
            conn.close()

    def store_fundamental_data(self, symbol: str, fundamental_data: List[Dict[str, Any]]):
        """Store quarterly fundamental data for a stock"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            for data in fundamental_data:
                cursor.execute("""
                    INSERT OR REPLACE INTO fundamental_data
                    (symbol, quarter, year, revenue, operating_income, net_income,
                     total_assets, total_debt, shareholders_equity, cash_and_equivalents,
                     ebit_margin, roe, debt_to_equity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol.upper(), data['quarter'], data['year'], data['revenue'],
                     data['operating_income'], data['net_income'], data['total_assets'],
                     data['total_debt'], data['shareholders_equity'], data['cash_and_equivalents'],
                     data['ebit_margin'], data['roe'], data['debt_to_equity']))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error storing fundamental data for {symbol}: {e}")
        finally:
            conn.close()

    def store_technical_data(self, symbol: str, technical_data: pd.DataFrame):
        """Store daily technical data for a stock"""
        conn = sqlite3.connect(self.db_path)

        try:
            # Prepare dataframe for insertion
            tech_data = technical_data.copy()
            tech_data['symbol'] = symbol.upper()
            tech_data = tech_data.reset_index()

            # Rename columns to match database schema
            column_mapping = {
                'Date': 'date',
                'Open': 'open_price',
                'High': 'high_price',
                'Low': 'low_price',
                'Close': 'close_price',
                'Volume': 'volume',
                'Adj Close': 'adj_close',
                'MA_20': 'ma_20',
                'MA_50': 'ma_50',
                'MA_200': 'ma_200'
            }
            tech_data = tech_data.rename(columns=column_mapping)

            # Select only the columns we need
            columns_to_insert = ['symbol', 'date', 'open_price', 'high_price', 'low_price',
                               'close_price', 'volume', 'adj_close', 'ma_20', 'ma_50', 'ma_200']
            tech_data = tech_data[columns_to_insert]

            # Insert data
            tech_data.to_sql('technical_data', conn, if_exists='append', index=False)
            conn.commit()

        except Exception as e:
            print(f"Error storing technical data for {symbol}: {e}")
        finally:
            conn.close()

    def get_fundamental_data(self, symbol: str) -> pd.DataFrame:
        """Retrieve quarterly fundamental data for a stock"""
        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT quarter, year, revenue, operating_income, net_income,
                   total_assets, total_debt, shareholders_equity, cash_and_equivalents,
                   ebit_margin, roe, debt_to_equity
            FROM fundamental_data
            WHERE symbol = ?
            ORDER BY year DESC, quarter DESC
            LIMIT 4
        """

        df = pd.read_sql_query(query, conn, params=(symbol.upper(),))
        conn.close()

        return df

    def get_technical_data(self, symbol: str, days: int = None) -> pd.DataFrame:
        """Retrieve technical data for a stock"""
        conn = sqlite3.connect(self.db_path)

        if days:
            query = """
                SELECT date, open_price, high_price, low_price, close_price,
                       volume, adj_close, ma_20, ma_50, ma_200
                FROM technical_data
                WHERE symbol = ?
                ORDER BY date DESC
                LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(symbol.upper(), days))
        else:
            query = """
                SELECT date, open_price, high_price, low_price, close_price,
                       volume, adj_close, ma_20, ma_50, ma_200
                FROM technical_data
                WHERE symbol = ?
                ORDER BY date DESC
            """
            df = pd.read_sql_query(query, conn, params=(symbol.upper(),))

        conn.close()
        return df

    def store_analysis_result(self, symbol: str, analysis: Dict[str, Any]):
        """Store analysis results for a stock"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO analysis_results
                (symbol, revenue_growth_4q, avg_ebit_margin, ebit_margin_trend,
                 current_price, ma_20, ma_50, ma_200, price_vs_ma20, price_vs_ma50, price_vs_ma200,
                 ranking_score, recommendation, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (symbol.upper(), analysis.get('revenue_growth_4q'),
                 analysis.get('avg_ebit_margin'), analysis.get('ebit_margin_trend'),
                 analysis.get('current_price'), analysis.get('ma_20'), analysis.get('ma_50'),
                 analysis.get('ma_200'), analysis.get('price_vs_ma20'), analysis.get('price_vs_ma50'),
                 analysis.get('price_vs_ma200'), analysis.get('ranking_score'),
                 analysis.get('recommendation'), analysis.get('summary')))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error storing analysis for {symbol}: {e}")
        finally:
            conn.close()

    def get_all_analysis_results(self) -> pd.DataFrame:
        """Get all analysis results for ranking"""
        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT symbol, revenue_growth_4q, avg_ebit_margin, ebit_margin_trend,
                   current_price, ma_20, ma_50, ma_200, price_vs_ma20, price_vs_ma50, price_vs_ma200,
                   ranking_score, recommendation, summary
            FROM analysis_results
            ORDER BY ranking_score DESC
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        return df

    def clear_database(self):
        """Clear all data from the database and start fresh"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Drop all tables
            cursor.execute("DROP TABLE IF EXISTS analysis_results")
            cursor.execute("DROP TABLE IF EXISTS technical_data")
            cursor.execute("DROP TABLE IF EXISTS fundamental_data")
            cursor.execute("DROP TABLE IF EXISTS financial_data")  # Remove old table
            cursor.execute("DROP TABLE IF EXISTS stocks")

            conn.commit()

            # Recreate tables with new schema
            self.init_database()

            print("Database cleared and recreated successfully")

        except sqlite3.Error as e:
            print(f"Error clearing database: {e}")
        finally:
            conn.close()