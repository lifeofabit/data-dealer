from os.path import dirname, realpath
from ruamel import yaml

import logging

# Initialize registry.yaml if empty
# TO-DO: Need to build config file and add default registry path
REG_PATH = dirname(realpath(__file__)) + '/registry.yaml'
try:
    f = open(REG_PATH, 'r')
except IOError as io:
    with open(REG_PATH, 'w') as f:
        f.write(yaml.dump({}))
else:
    if f.read() == '':
        f.write(yaml.dump({}))

class Registry(object):
    def __init__(self):
        """
        Initialize the registry by loading yaml doc, logger, and
        supplier from registry
        """
        self.logger = logging.getLogger('dealer.registry')

        self._load()

    def display(self):
        """
        Display Command.  Print registry to terminal
        """
        if not self.registry:
            self.logger.info('The registry is empty!')
        else:
            self.logger.info('### Data Supplier Registry ###\n{}'.format(
                yaml.dump(self.registry, default_flow_style=False)))

    def get(self, supplier):
        """
        Returns the supplier and its metadata
        """
        BUILT_IN = ['json', 'csv']

        if not self._exists(supplier):
            if supplier not in BUILT_IN:
                raise ValueError('Supplier {} does not exist and needs to be registered and/or implemented.'.format(supplier))
            return supplier, {}

        return supplier, self.registry[supplier]

    def register(self, supplier, properties):
        """
        Register command.  Creates or updates a supplier in the registry
        """
        self.registry[supplier] = self._parse(properties)
        self._write()
        self.logger.info('Registring supplier: {}'.format(supplier))

    def remove(self, supplier):
        """
        Remove command.  Removes a supplier from the registry
        """
        self.registry.pop(supplier, {})
        self._write()
        self.logger.info('Removed supplier: {}'.format(supplier))

    def remove_property(self, supplier, property):
        """
        Remove property command.  Removes a property from the registry
        """
        if not self.registry.get(supplier):
            raise EnvironmentError('Supplier {} does not exist. Terminating execution'.format(supplier))

        self.registry[supplier].pop(property)
        self._write()
        self.logger.debug('Removed property {} from {}'.format(property, supplier))


    def run(self, command, supplier=None, properties=None):
        """
        Runs a registry command.  Potential to refactor from nested to functional
        """
        self.logger.debug('Running registry command: {}'.format(command))
        if command == 'display' or command == 'show':
            self.display()
        elif command == 'add' or command == 'update':
            # TO-DO: Fix update command, currently clobbers what is there
            if not supplier or not properties:
                raise EnvironmentError('Need to give a supplier and properties as options')

            self.register(supplier, properties)
        elif command == 'remove':
            if not supplier:
                raise EnvironmentError('Need to give a supplier as option')

            if not properties:
                self.remove(supplier)
            else:
                properties = properties.split(',')
                map(lambda p: self.remove_property(supplier, p), properties)

        else:
            self.logger.critical('Not a valid Registry command. Commands supported:\n - {}'.format(
                ', '.join(['display', 'show', 'add', 'remove'])
            ))
            raise EnvironmentError('Not a valid Registry command')

    def _exists(self, supplier):
        """
        Check to see if a supplier exists in the registry
        """
        if self.registry.get(supplier):
            return True

        return False

    def _load(self):
        """
        Load the registry file into memory
        """
        with open(REG_PATH, 'r') as f:
            self.registry = yaml.load(f.read(), Loader=yaml.Loader)

    def _parse(self, properties):
        """
        Turn properties string from cli option into dictionary
        """
        parsed = [tuple(prop.split('=')) for prop in properties.split(';')]
        return {k: v for (k, v) in parsed}

    def _validate(self):
        """
        Stub.  Potential method to validate necessary source properties
        """
        raise NotImplementedError

    def _write(self):
        """
        Write new registry contents to file
        """
        with open(REG_PATH, 'w') as f:
            f.write(yaml.safe_dump(self.registry, default_flow_style=False, allow_unicode=True))
