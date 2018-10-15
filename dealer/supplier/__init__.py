""" Supplier Base Class """

from dealer.registry import Registry
import dealer

import logging

class Supplier(object):
    def __init__(self, supplier):
        self.logger = logging.getLogger('dealer.supplier.{}'.format(self.__class__.__name__))
        self.supplier, self.metadata = Registry().get(supplier)

    @staticmethod
    def determine(supplier):
        _, metadata = Registry().get(supplier)

        # Change 'dbms' to something more generic
        if metadata.get('dbms'):
            return metadata.get('dbms').title()

        return supplier.title()

    @staticmethod
    def exists(supplier):
        from inspect import getmembers, isclass

        members = [m[0] for m in getmembers(dealer.supplier, isclass) if 'dealer.supplier' in m[1].__module__]
        # TO-DO: Add logic to filter out base and abstract classes

        if supplier.title() in members:
            return True
        return False

    @staticmethod
    def infer(store):
        if '.' in store.split('/')[-1]:
            return store.split('.')[-1]

        # Check if file dir/
        raise EnvironmentError('Cannot determine file type, please enter a valid path.')

    @staticmethod
    def is_file_class(supplier):
        if supplier == 'file' or supplier == 's3':
            return True

        return False



from .database.athena import Athena
from .database.dynamo import Dynamo
from .database.mssql import Mssql

from .file import *
