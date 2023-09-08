'''
data_processor.py:
    Process and visualize data.
'''

import pandas as pd
class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def process_data(self):
        # TODO: Add your data processing logic

        df = self.data

        # Calculate the daily return and add it as a new column
        df['Daily Return'] = df['Close'].pct_change()

        n_periods = 20
        # Calculate the Simple Moving Average: Moving averages help identify trends
        df['SMA'] = df['Close'].rolling(window = n_periods).mean()

        # Calculate the Exponential Moving Average: Good with price changes
        df['EMA'] = df['Close'].ewm(span = n_periods, adjust = False).mean()
        processed_data = df[['Ticker', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Daily Return', 'SMA', 'EMA']]

        return processed_data
    
    def visualize_data(self):
        # TODO: Add your data processing logic
        pass
