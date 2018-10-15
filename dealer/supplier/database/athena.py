from botocore import exceptions as awserror

import pandas as pd
import time

from dealer.process import log_method, open_file

from . import Database

class Athena(Database):
    def __init__(self, supplier):
        super(Athena, self).__init__(supplier)

        self.connect(supplier)

    def connect(self, supplier):
        try:
            from boto3.session import Session
            session = Session(
                aws_access_key_id=self.metadata['aws_key'],
                aws_secret_access_key=self.metadata['aws_secret']
            )

            self.sql = session.client('athena', region_name=self.metadata.get('region_name', 'us-east-1'))
            self.s3 = session.client('s3', region_name=self.metadata.get('region_name', 'us-east-1'))
        except Exception as ex:
            self.logger.error(ex.__repr__())
            raise ex 

    @log_method('Starting query execution in AWS Athena', 'Athena query execution complete')
    def read(self, output_dir, **kwargs):
        query = kwargs.get('query')
        if not query:
            if kwargs.get('query_file'):
                query = open_file(kwargs.get('query_file'))
            else:
                self.logger.error('Need a query for database table')
                raise EnvironmentError

        exec_id = self.sql.start_query_execution(
            QueryString=query,
            ResultConfiguration={'OutputLocation': output_dir}
        )['QueryExecutionId']

        bucket, key = self._parse_output_dir(output_dir)
        key += '{}.csv'.format(exec_id)

        while True:
            try:
                data = self._get_from_s3(bucket, key)
            except self.s3.exceptions.NoSuchKey:
                time.sleep(5)
            except Exception as ex:
                self.logger.warning(ex.__repr__())
                raise ex
            else:
                break

        return data

    def write(self):
        raise NotImplementedError('Cannot write to AWS Athena')

    def _get_from_s3(self, bucket, key):
        result = self.s3.get_object(Bucket=bucket, Key=key)
        return pd.read_csv(result['Body'], dtype=str)

    def _parse_output_dir(self, output_dir):
        return output_dir.replace('s3://', '').split('/', 1)


    def _validate_output_dir(self, output_dir):
        '''
        TO-DO: Make sure the output directory is a valid s3 path
        '''
        raise NotImplementedError