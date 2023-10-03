# mock_trading.py

import trading_algo as ta

tickers = ["DIS", "AMZN", "LULU", "TSLA", "AAPL"]
initial_investment = 10000
fund_per_stock = initial_investment / len(tickers)
portfolio = {ticker: {'shares': 0, 'fund': fund_per_stock} for ticker in tickers}

def trade(portfolio, ticker, data):
    forecast = ta.moving_average_forecast(data)  # example with moving average
    buy_signal, sell_signal = ta.generate_signals(data, forecast)
    
    for date in data.index:
        if buy_signal[date]:
            portfolio[ticker]['shares'] += portfolio[ticker]['fund'] / data[date]
            portfolio[ticker]['fund'] -= portfolio[ticker]['fund'] / data[date] * data[date]
        if sell_signal[date]:
            portfolio[ticker]['fund'] += portfolio[ticker]['shares'] * data[date]
            portfolio[ticker]['shares'] = 0

def calculate_portfolio_value(portfolio, data):
    total_value = 0
    for ticker in tickers:
        total_value += portfolio[ticker]['shares'] * data[ticker].iloc[-1]
        total_value += portfolio[ticker]['fund']
    return total_value

if __name__ == '__main__':
    start_date = 'YYYY-MM-DD'
    end_date = 'YYYY-MM-DD'
    data = {ticker: ta.fetch_stock_data(ticker, start_date, end_date) for ticker in tickers}
    
    for ticker in tickers:
        trade(portfolio, ticker, data[ticker])
    
    final_value = calculate_portfolio_value(portfolio, data)
    print(f"Final Portfolio Value: ${final_value:.2f}")
