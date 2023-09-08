'''
data_store_interface.py:
    Define a data store interface so that other data sources can be easily replaced.
'''

from abc import ABC, abstractmethod

class DataStoreInterface(ABC):
    @abstractmethod
    def save(self, data):
        pass
