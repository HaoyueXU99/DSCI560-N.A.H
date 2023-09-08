'''
csv_store.py:
    Implement the interface defined in data_store_interface.py and support data storage to CSV.
'''

from data_store_interface import DataStoreInterface

class CSVStore(DataStoreInterface):
    def __init__(self, file_path="output.csv"):
        self.file_path = file_path

    def save(self, data):
        data.to_csv(self.file_path)
