from string import ascii_lowercase
from decimal import Decimal

import pandas as pd
import sys

from dealer.process import log_method, open_file
from . import Database

class Dynamo(Database):
    def __init__(self, supplier):
        super(Dynamo, self).__init__(supplier)

        from boto3.session import Session
        session = Session(
            aws_access_key_id=self.metadata['aws_key'],
            aws_secret_access_key=self.metadata['aws_secret']
        )
        self.sql = session.resource('dynamodb', region_name='us-east-1')

    def connect(self, table):
        self.table = self.sql.Table(table)

    @log_method('Starting read from DynamoDB', 'DynamoDB read complete')
    def read(self, table, **kwargs):
        self.connect(table)

        # if not kwargs.get('query') and not kwargs.get('query_type'):
        #     self.logger.error('Attributes and query type need to be set for dynamo')
        #     raise ValueError

        query = kwargs.get('query')
        query_type = kwargs.get('query_type')
        params = {'ProjectionExpression': query} if query else {}

        if not query_type:
            # Going to need to produce a DecimalEncoder I bet
            resp = self.table.scan(**params)
            items = resp['Items']

            while 'LastEvaluatedKey' in resp:
                if len(items) > kwargs.get('limit', sys.maxsize):
                    self.logger.critical('Stopping read iteration')
                    break

                resp = self.table.scan(ExclusiveStartKey=resp['LastEvaluatedKey'], **params)
                items += resp['Items']

        else:
            self.logger.error('DynamoDB query currently not implemented')
            raise NotImplementedError

        if kwargs.get('limit'):
            items = items[:kwargs.get('limit')]

        self.logger.info('Dynamo {} produced {} results from {}'.format(
                'query' if query_type else 'scan',
                len(items),
                table
        ))
        return pd.DataFrame(items)

    def write(self, data, table, load_type, **kwargs):
        self.connect(table)

        if load_type == 'merge':
            self._merge(data, table)
        elif load_type == 'overwrite':
            # Need to describeTable(), deleteTable(), recreateTable(), then load
            self.logger.error('Overwrite method currently not implemented')
            raise NotImplementedError
        elif load_type == 'update':
            if not kwargs.get('expression', None) and not kwargs.get('key', None):
                self.logger.error('Pleae provide a --key to update on and an --expression for columns to update')
                raise EnvironmentError
            self._update(data, table, kwargs.get('key'), kwargs.get('expression'))
        else:
            self.logger.critical('Load type {} is not supported. Current types of load: merge'.format(load_type))

    def _encode(self, item):
        for k, v in item.items():
            if isinstance(v, float) or isinstance(v, int):
                item.update({k: Decimal(str(v))})
            elif isinstance(v, pd._libs.tslib.Timestamp):
                item.update({k: v.to_pydatetime().strftime('%Y-%m-%d %H:%M:%S')})

        return item

    @log_method('Starting "merge" write to DynamoDB', 'DynamoDB merge complete')
    def _merge(self, data, table):
        items = data.to_dict(orient='records')
        items = [self._encode(item) for item in items]

        with self.table.batch_writer() as batch:
            compare = None
            for item in items:
                try:
                    batch.put_item(Item=item)
                except Exception as ex:
                    print(ex.message, ex.args)
                    raise Exception

                compare = item
        self.logger.info('Wrote {} records to DynamoDB table: {}'.format(len(items), table))

    @log_method('Starting update to DynamoDB', 'DynamoDB update complete')
    def _update(self, data, table, key, expression):
        items = data.to_dict(orient='records')
        items = [self._encode(item) for item in items]
        key = key.split(',')
        expression = [exp.split('=') for exp in expression.split(',')]

        # Need to refactor the zipping into one list for ease of use
        ue_format = zip([exp[0] for exp in expression], [':'+ l for l in ascii_lowercase])
        eav_format = zip([exp[1] for exp in expression], [':'+ l for l in ascii_lowercase])
        ue = ['{} = {}'.format(*z) for z in ue_format]


        for item in items:
            resp = self.table.update_item(
                Key={k: item[k] for k in key},
                UpdateExpression='set ' + ','.join(ue),
                ExpressionAttributeValues={z[1]: item[z[0]] for z in eav_format}
            )

        self.logger.info('Updated {} records in DynamoDB table: {}'.format(len(items), table))
