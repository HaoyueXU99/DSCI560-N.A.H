# trading_algo.py

import yfinance as yf
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import datetime
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

def fetch_stock_data(ticker, start_date, end_date, interval='15m'):
    try:
        stock_data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        return stock_data['Close']
    except OverflowError:
        print(f"Overflow error fetching data for {ticker}.")
        return None
    except Exception as e:
        print(f"Error fetching data for {ticker}. Reason: {e}")
        return None


def moving_average_forecast(data, window_size=30):
    return data.rolling(window=window_size).mean()

def exponential_smoothing_forecast(data):
    model = ExponentialSmoothing(data)
    model_fit = model.fit()
    forecast = model_fit.predict(len(data), len(data))
    return forecast

def arima_forecast(data):
    model = ARIMA(data, order=(5,1,0))  # example order
    model_fit = model.fit(disp=0)
    forecast = model_fit.forecast(steps=1)[0]
    return forecast

def lstm_forecast(data):
    data = np.array(data).reshape(-1, 1)
    
    # normalize data
    scaler = MinMaxScaler(feature_range=(0, 1))
    data = scaler.fit_transform(data)
    
    # transform data for LSTM
    X, y = [], []
    for i in range(len(data)-1-1):
        X.append(data[i:(i+1), 0])
        y.append(data[i + 1, 0])
    X, y = np.array(X), np.array(y)
    
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    
    model = Sequential()
    model.add(LSTM(50, input_shape=(X.shape[1], X.shape[2])))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X, y, epochs=50, batch_size=1, verbose=0)
    
    pred = model.predict(np.array([data[-2]]).reshape(1,1,1))
    return scaler.inverse_transform(pred)[0, 0]

def generate_signals(data, forecast):
    buy_signal = (data.shift(1) < forecast.shift(1)) & (data > forecast)
    sell_signal = (data.shift(1) > forecast.shift(1)) & (data < forecast)
    return buy_signal, sell_signal

def compute_metrics(true_data, predictions):
    mae = mean_absolute_error(true_data, predictions)
    rmse = np.sqrt(mean_squared_error(true_data, predictions))
    return mae, rmse

def plot_forecasts(ticker, data, forecasts, algorithm_name):
    plt.figure(figsize=(12,6))
    plt.plot(data, label='True Data')
    plt.plot(forecasts, label=f'{algorithm_name} Forecast', alpha=0.7)
    plt.title(f'{ticker} Stock Prices and {algorithm_name} Forecasts')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    tickers = ["DIS", "AMZN", "LULU", "TSLA", "AAPL"]
    end_date = datetime.datetime.now().strftime('%Y-%m-%d') 
    start_date = (datetime.datetime.now() - datetime.timedelta(weeks=2)).strftime('%Y-%m-%d')

    for ticker in tickers:
        print(f"Processing {ticker}...")

        # Fetch data
        data = fetch_stock_data(ticker, start_date, end_date)

        # Initialize metrics for choosing best model
        best_mae = float('inf')
        best_rmse = float('inf')
        best_model = None

        # Forecast with each method and evaluate
        algorithms = {
            'Moving Average': moving_average_forecast,
            'Exponential Smoothing': exponential_smoothing_forecast,
            'ARIMA': arima_forecast,
            'LSTM': lstm_forecast
        }
        
        for algo_name, algo_func in algorithms.items():
            print(f"Running {algo_name}...")
            forecast = algo_func(data)
            
            # Truncate the original data or the forecast, if necessary, to ensure equal length
            min_length = min(len(data), len(forecast))
            mae, rmse = compute_metrics(data[-min_length:], forecast[-min_length:])
            
            if mae < best_mae:  # Choose the model with the lowest MAE
                best_mae = mae
                best_rmse = rmse
                best_model = algo_name

            # For visualization
            plot_forecasts(ticker, data, forecast, algo_name)

            # Print Metrics for each algorithm
            print(f"{algo_name} - MAE: {mae}, RMSE: {rmse}")

        print(f"Best model for {ticker} is {best_model} with MAE: {best_mae} and RMSE: {best_rmse}")
        print('-' * 50)
