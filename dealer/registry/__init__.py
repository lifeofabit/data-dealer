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
                self.logger.error('Supplier {} does not exist and needs to be registered'.format(supplier))
                return
            return supplier, {}

        return supplier, self.registry[supplier]

    def load(self, file_path):
        """
        Load command.  Read a yaml from file or s3 and load as registry
        """
        self._load(file_path)
        self._write()

    def register(self, supplier, properties):
        """
        Register command.  Creates or updates a supplier in the registry
        """
        self.registry[supplier] = self._parse(properties)
        self._write()
        self.logger.info('Registring supplier: {}'.format(supplier))

    def remove_supplier(self, supplier):
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
            self.logger.error('Supplier {} does not exist. Terminating execution'.format(supplier))
            return

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
                self.logger.error('Must provide option -s with supplier name and option -p with properties')
                return

            self.register(supplier, properties)
        elif command == 'remove':
            if not supplier:
                self.logger.error('Must provide option -s with supplier name')
                return

            if not properties:
                self.remove_supplier(supplier)
            else:
                map(lambda p: self.remove_property(supplier, p), properties.split(','))

        elif command == 'load':
            if not supplier:
                self.logger.error('Must provide option -s with file path for yaml')
                return

            self.load(supplier)

        else:
            self.logger.critical('{} is not a valid Registry command. Supported commands are:\n - {}'.format(
                command,
                ', '.join(['display', 'show', 'add', 'remove', 'load'])
            ))

    def _exists(self, supplier):
        """
        Check to see if a supplier exists in the registry
        """
        if self.registry.get(supplier):
            return True

        return False

    def _load(self, file_path=REG_PATH):
        """
        Load the registry file into memory
        """
        with open(file_path, 'r') as f:
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
