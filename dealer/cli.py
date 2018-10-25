""" Command Line Interface """
# Matt was here
from os.path import dirname, realpath
from functools import update_wrapper
from inspect import getargspec

import logging
import click

from dealer.registry import Registry
from dealer.supplier import Supplier
from dealer.process import Logger

import dealer.supplier

@click.group(chain=True)
def cli():
    """
    The data-dealer cli gives an interface to run a series
    of commands to extract, transform, and load data sources.

    Example Commands:
    """
    Logger.debug('Logging setup. Opening command line interface and initializing')
    pass


@cli.resultcallback()
def process_commands(processors):
    """
    This result callback is invoked with an iterable of all the chained
    subcommands.  As in this example each subcommand returns a function
    we can chain them together to feed one into the other, similar to how
    a pipe on unix works.
    """
    stream = ()

    for processor in processors:
        stream = processor(stream)

    for _ in stream:
        pass

def processor(f):
    """
    Helper decorator to rewrite a function so that it returns another
    function from it.
    """
    def new_func(*args, **kwargs):
        def processor(stream):
            return f(stream, *args, **kwargs)
        return processor
    return update_wrapper(new_func, f)

def generator(f):
    """
    Similar to the :func:`processor` but passes through old values
    unchanged and does not pass through the values as parameter.
    """
    @processor
    def new_func(stream, *args, **kwargs):
        for item in stream:
            yield item
        for item in f(*args, **kwargs):
            yield item
    return update_wrapper(new_func, f)

# @cli.command()
# @click.argument('obj')
# @click.option('-n', '--name', 'name', type=str, default='new_column')
# @click.option('-t', '--type', 'data_type', type=str)
# @click.option('-v', '--value', 'value', type=str, default='NA')
# @processor
# def add(data, obj, name, data_type, value):
#     """
#     Add to the data structure
#     """
#     from nlp.worker import Worker
#
#     for df in data:
#         _class = Worker(df, is_normalized=True)
#
#         if obj == 'column':
#             _class.add_column(name, data_type, value)
#
#         yield _class.df

@cli.command()
@click.option('--columns', 'columns',
              help='Comma separated list of columns to display')
@click.option('--head', 'head', is_flag=True,
              help='Prints sample of the data')
@click.option('--summary', 'summary', is_flag=True,
              help='Prints summary of the current dataframe')
@processor
def display(data, columns, head, summary):
    """
    Print resulting dataframe to the screen
    """
    for df in data:
        if head:
            print(df.head(20))

        elif columns:
            cols = columns.split(',')
            for index, row in df[cols].iterrows():
                print('\t'.join([str(r) if len(str(r)) < 64 else str(r)[:32] + '...' + str(r)[-32:] for r in row.tolist()]))

        elif summary:
            from numpy import object
            print(df.describe(include=[object]))

        else:
            print('\t'.join(df.columns))
            for index, row in df[:].iterrows():
                print('\t'.join([str(r).encode('ascii', 'ignore') for r in row.tolist()]))

        yield df


@cli.command()
@click.argument('supplier')
@click.argument('store')
@click.option('-f', '--file_type', 'file_type')
@click.option('-l', '--limit', 'limit', type=int)
@click.option('-q', '--query', 'query',
              help='SQL query or named fields')
@click.option('-qf', '--query_file', 'query_file',
              help='Pull in data query from a file')
@click.option('--query/--scan', 'query_type', default=False)
@generator
def extract(supplier, store, file_type, limit, query, query_file, query_type):
    """
    Pull data from a supplier
    """
    kwargs = {k: v for k, v in locals().items() if v is not None}
    kwargs.pop('supplier'); kwargs.pop('store')

    try:
        if Supplier.is_file_class(supplier):
            if not file_type:
                supplier = Supplier.infer(store)
            else:
                supplier = file_type

        _class = getattr(dealer.supplier, Supplier.determine(supplier))(supplier)
        df = _class.read(store, **kwargs)
    except Exception as ex:
        Logger.error(ex.message)
        Logger.critical('Terminating execution')
        return

    yield df


@cli.command()
@click.argument('supplier')
@click.argument('store')
@click.argument('load_type')
@click.option('-e', '--expression', 'expression')
@click.option('-f', '--file_type', 'file_type')
@click.option('-k', '--key', 'key')
@click.option('-t', '--table', 'table')
@processor
def load(data, supplier, store, load_type, expression, file_type, key, table):
    """
    Load data to a destination
    """
    kwargs = {k: v for k, v in locals().items() if v is not None}
    kwargs.pop('supplier'); kwargs.pop('store')
    kwargs.pop('load_type'); kwargs.pop('data')

    # try:
    if Supplier.is_file_class(supplier):
        if not file_type:
            supplier = Supplier.infer(store)
        else:
            supplier = file_type

    _class = getattr(dealer.supplier, Supplier.determine(supplier))(supplier)
    for df in data:
        _class.write(df, store, load_type, **kwargs)
        yield df

    # except Exception, ex:
    #     print ex
    #     Logger.error(ex.message)
    #     Logger.critical('Terminating execution')
    #     return

@cli.command()
@click.argument('reg_command')
@click.option('-s', '--supplier', 'supplier')
@click.option('-p', '--properties', 'properties')
@generator
def registry(reg_command, supplier, properties):
    """
    Access registry with registry commands
    """
    kwargs = {k: v for k, v in locals().items() if v is not None}
    kwargs.pop('reg_command')

    Registry().run(reg_command, **kwargs)
    yield None


# @cli.command()
# @click.argument('obj')
# @click.argument('names')
# @processor
# def remove(data, obj, names):
#     """
#     Remove from the current data structure
#     """
#     from nlp.worker import Worker
#
#     for df in data:
#         _class = Worker(df, is_normalized=True)
#
#         if obj == 'column':
#             _class.remove_column(names)
#
#         yield _class.df

# To rename a column or something else
# def rename(data, obj, name):
#     pass




# cli.add_command(add)
cli.add_command(display)
cli.add_command(extract)
cli.add_command(load)
cli.add_command(registry)
# cli.add_command(remove)
