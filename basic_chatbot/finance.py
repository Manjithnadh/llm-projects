import yfinance as yf
from langchain.tools import tool

@tool
def get_historical_stock_price(ticker: str, period: str = "1mo") -> str:
    """
    Fetches historical closing prices for a given stock ticker using Yahoo Finance.
    'period' can be like '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'.
    Returns the last few closing prices.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if not hist.empty:
            # Return the last 5 closing prices for brevity
            last_prices = hist['Close'].tail(5).to_dict()
            return f"Historical closing prices for {ticker} over {period}: {last_prices}"
        else:
            return f"No historical data found for {ticker} for the period {period}."
    except Exception as e:
        return f"Error fetching historical stock price for {ticker}: {e}"
import yfinance as yf
from langchain.tools import tool

@tool("get_current_stock_price")
def get_current_stock_price(ticker: str) -> str:
    """
    Fetches the current or last available trading price for a given stock ticker.
    Examples: 'NVDA', 'GOOGL', 'AAPL'.
    Returns the current price or an error message if the ticker is invalid or data is unavailable.
    """
    try:
        stock = yf.Ticker(ticker)
        # Get real-time or last available regular market price
        # Using .info and checking 'regularMarketPrice' or 'currentPrice' is a common approach
        # Note: yfinance data can have a slight delay (e.g., 15 minutes) depending on the source.
        info = stock.info
        price = info.get('regularMarketPrice') or info.get('currentPrice')

        if price:
            return f"The current price of {ticker} is ${price:.2f}."
        else:
            # Fallback to last close if real-time isn't directly available or check history
            hist = stock.history(period="1d")
            if not hist.empty:
                last_close = hist['Close'].iloc[-1]
                return f"The last closing price of {ticker} was ${last_close:.2f}."
            else:
                return f"Could not retrieve current or historical price for {ticker}. Please check the ticker symbol."
    except Exception as e:
        return f"An error occurred while fetching price for {ticker}: {e}. Please check the ticker symbol."

# You could add get_historical_stock_price to your tools list.