'''
csv_store.py:
    Implement the interface defined in data_store_interface.py and support data storage to CSV.
'''

import pandas as pd
from data_store_interface import DataStoreInterface

class CSVStore(DataStoreInterface):
    def __init__(self, file_path="output.csv"):
        self.file_path = file_path

    def save(self, data):
        df = pd.concat(data.values(), keys=data.keys())
        df.to_csv(self.file_path)
