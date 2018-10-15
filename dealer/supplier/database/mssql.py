from datetime import datetime

import pandas as pd

from dealer.process import log_method, open_file
from . import Database

class Mssql(Database):
    def __init__(self, supplier):
        super(Mssql, self).__init__(supplier)

        import pymssql
        self.sql = pymssql

    def columns(self, data):
        return data.columns.values.tolist()

    def connect(self, dbase):
        try:
            return self.sql.connect(self.metadata['host'], self.metadata['uname'], self.metadata['pword'], dbase)
        except Exception as ex:
            self.logger.error(ex.__repr__())
            raise ex

    def options(self, data):
        def get_option(dtype):
            if 'i' in dtype or 'f' in dtype:
                return '%d'
            else:
                return '%s'

        return map(get_option, [d.str for d in data.dtypes.tolist()])

    @log_method('Starting read from MSSQL database', 'MSSQL read complete')
    def read(self, dbase, **kwargs):
        query = kwargs.get('query')
        if not query:
            if kwargs.get('query_file'):
                query = open_file(kwargs.get('query_file'))
            else:
                self.logger.error('Need a query for database table')
                raise EnvironmentError

        with self.connect(dbase) as cnxn:
            data = pd.read_sql(query, cnxn)
            self.logger.info('MSSQL query produced {} results'.format(len(data)))

            return data

    def write(self, data, dbase, load_type, **kwargs):
        if not kwargs.get('table'):
            self.logger.error('No table specified. Add option --table=<table_name> to write')
            raise ValueError

        with self.connect(dbase) as cnxn:
            with cnxn.cursor() as cursor:
                table = kwargs.get('table')
                if load_type == 'merge':
                    self._merge(cursor, data, table)

                elif load_type == 'append':
                    self._append(cursor, data, table)

                elif load_type == 'overwrite':
                    self._overwrite(cursor, data, table)

                elif load_type == 'update':
                    self._update(cursor, data, table)

                else:
                    self.logger.critical('Load type {} is not supported. Current types of load: append, overwrite'.format(load_type))
                    return

                cnxn.commit()

    @log_method('Starting "append" write to MSSQL', 'MSSQL append complete')
    def _append(self, cursor, data, table):
        self._insert(cursor, data, table)

    def _insert(self, cursor, data, table):
        # data['insert_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        query = 'INSERT INTO {} ({}) VALUES ({})'.format(
            table,
            ','.join(self.columns(data)),
            ','.join(self.options(data))
        )

        items = data[self.columns(data)].values.tolist()
        items = tuple(map(tuple, items))

        self.logger.debug('Executing SQL Query: {}'.format(query))

        try:
            cursor.executemany(query, items)
            self.logger.info('Wrote {} records to MSSQL table: {}'.format(len(items), table))
        except Exception as ex:
            self.logger.error('Error writing to table: {}'.format(ex))

    def _merge(self, cursor, data, table):
        raise NotImplementedError

    @log_method('Starting "overwrite" write to MSSQL', 'MSSQL overwrite complete')
    def _overwrite(self, cursor, data, table):
        self._truncate(cursor, table)
        self._insert(cursor, data, table)

    def _truncate(self, cursor, table):
        try:
            cursor.execute('TRUNCATE TABLE {}'.format(table))
        except Exception as ex:
            self.logger.error('Error truncating table: {}'.format(table))

    def _update(self, cursor, data, table):
        raise NotImplementedError

        query = 'UPDATE {} SET {}'

class Redshift(Database):
    def __init__(self, supplier):
        super(Redshift, self).__init__(supplier)

        import psycopg2
        self.sql = psycopg2

    def columns(self, data):
        return data.columns.values.tolist()

    def connect(self, dbase):
        try:
            return self.sql.connect(host=self.metadata['host'], port=self.metadata['port'], user=self.metadata['uname'], password=self.metadata['pword'], dbname=dbase)
        except Exception as ex:
            raise ex

    def options(self, data):
        def get_option(dtype):
            return '%s'

        return map(get_option, [d.str for d in data.dtypes.tolist()])

    @log_method('Starting read from Redshift database', 'Redshift read complete')
    def read(self, dbase, **kwargs):
        query = kwargs.get('query')
        if not query:
            if kwargs.get('query_file'):
                query = open_file(kwargs.get('query_file'))
            else:
                self.logger.error('Need a query for database table')
                raise EnvironmentError

        with self.connect(dbase) as cnxn:
            data = pd.read_sql(query, cnxn)
            self.logger.info('MSSQL query produced {} results'.format(len(data)))

            return data

    def write(self, data, dbase, table, load_type):
        with self.connect(dbase) as cnxn:
            with cnxn.cursor() as cursor:
                if load_type == 'merge':
                    self._merge(cursor, data, table)

                elif load_type == 'append':
                    self._append(cursor, data, table)

                elif load_type == 'overwrite':
                    self._overwrite(cursor, data, table)

                elif load_type == 'update':
                    self._update(cursor, data, table)

                else:
                    self.logger.critical('Load type {} is not supported. Current types of load: append, overwrite'.format(load_type))
                    return

                cnxn.commit()

    @log_method('Starting "append" write to Redshift', 'Redshift append complete')
    def _append(self, cursor, data, table):
        self._insert(cursor, data, table)

    def _insert(self, cursor, data, table):
        # data['insert_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        query = 'INSERT INTO {} ({}) VALUES ({})'.format(
            table,
            ','.join(self.columns(data)),
            ','.join(self.options(data))
        )

        items = data[self.columns(data)].values.tolist()
        items = tuple(map(tuple, items))

        self.logger.debug('Executing SQL Query: {}'.format(query))

        try:
            cursor.executemany(query, items)
            self.logger.info('Wrote {} records to MSSQL table: {}'.format(len(items), table))
        except Exception as ex:
            self.logger.error('Error writing to table: {}'.format(ex))