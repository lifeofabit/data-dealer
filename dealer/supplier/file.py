""" File Suppliers """

import pandas as pd
import json

from dealer.process import log_method
from . import Supplier


class File(Supplier):
    """
    Base class for Files
    """
    def __init__(self, supplier):
        super(File, self).__init__(supplier)

    def read(self, data, **kwargs):
        if kwargs.get('query'):
            columns = kwargs.get('query').split(',')
            return data[columns]

        return data

    def write(self):
        pass

class S3(Supplier):
    """
    Base class for s3 Files
    """
    def __init__(self, supplier):
        super(S3, self).__init__(supplier)


    def read(self, data, **kwargs):
        if kwargs.get('query'):
            columns = kwargs.get('query').split(',')
            return data[columns]

        return data

    def write(self):
        pass

class Csv(File):
    def __init__(self, supplier='csv'):
        super(Csv, self).__init__('csv')

    @log_method('Reading data from CSV file', 'Reading complete')
    def read(self, file_path, **kwargs):
        data = pd.read_csv(file_path)
        return super(Csv, self).read(data, **kwargs)

    @log_method('Writing data to CSV file', 'Writing complete')
    def write(self, data, file_path, load_type, **kwargs):
        if load_type == 'overwrite':
            data.to_csv(file_path, index=False, encoding='utf-8')

        elif load_type == 'append':
            with open(file_path, 'a') as f:
                data.to_csv(f, header=False, index=False, encoding='utf-8')

        else:
            self.logger.critical('Load type {} is not currently implemeneted.  Please use overwrite or append'.format(load_type))

class Json(File):
    def __init__(self, supplier='json'):
        super(Json, self).__init__('json')

    @log_method('Reading data from JSON file', 'Reading complete')
    def read(self, file_path, **kwargs):
        data = pd.read_json(file_path)
        return super(Json, self).read(data, **kwargs)

# Error when file does not exist
#   File "/Users/mdowns/analytics-nlp/nlp/supplier/file.py", line 50, in read
#     return pd.read_json(file_path)
#   File "/Users/mdowns/analytics-nlp/tmp/venv/lib/python2.7/site-packages/pandas/io/json/json.py", line 354, in read_json
#     date_unit).parse()
#   File "/Users/mdowns/analytics-nlp/tmp/venv/lib/python2.7/site-packages/pandas/io/json/json.py", line 422, in parse
#     self._parse_no_numpy()
#   File "/Users/mdowns/analytics-nlp/tmp/venv/lib/python2.7/site-packages/pandas/io/json/json.py", line 639, in _parse_no_numpy
#     loads(json, precise_float=self.precise_float), dtype=None)
# ValueError: Expected object or value

    @log_method('Writing data to JSON file', 'Writing complete')
    def write(self, data, file_path, load_type, **kwargs):
        if load_type == 'overwrite':
            data.to_json(file_path, orient='records')

        elif load_type == 'append':
            with open(file_path, 'r') as f:
                records = json.load(f)

            data = pd.concat([data, pd.DataFrame(records)])
            data.to_json(file_path, orient='records')

        else:
            self.logger.critical('Load type {} is not currently implemeneted.  Please use overwrite or append'.format(load_type))
