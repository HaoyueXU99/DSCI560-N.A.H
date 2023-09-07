'''
api_interface.py:
    Define a data API interface so that other data sources can be easily replaced 
    in the future without affecting other parts of the code.
'''


from abc import ABC, abstractmethod

class DataAPIInterface(ABC):
    @abstractmethod
    def fetch_data(self, ticker, range):
        pass
