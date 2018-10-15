from abc import ABCMeta, abstractmethod

from dealer.supplier import Supplier

class Database(Supplier):
    """
    Base class for Databases
    """
    __metaclass__ = ABCMeta

    def __init__(self, supplier):
        super(Database, self).__init__(supplier)

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def write(self):
        pass