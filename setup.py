'''Package settings'''

from setuptools import setup, find_packages, Command
from os.path import abspath, dirname, join
from subprocess import call
from codecs import open

from dealer import __version__


this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.md'), encoding='utf-8') as f:
	long_descr = f.read()

class run_tests(Command):
	''' Run all the tests '''
	description = 'tests'
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		errno = call(['py.test', '--cov=dealer', '--cov-report=term-missing'])
		raise SystemExit(errno)

setup(
    name='data-dealer',
    version=__version__,
	description = 'A command line interface for the Data Dealer',
	long_description = long_descr,
	url = 'https://github.com/lifeofabit/data-dealer.git',
	author = 'Matt Downs',
	author_email = '',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
		'boto3',
		'Click',
		'pandas',
		'psycopg2',
		'pymssql',
		'python-dateutil<2.7',
		'ruamel.yaml'
    ],
	extras_require = {
		'test': ['coverage', 'pytest', 'pytest-cov']
	},
    entry_points='''
        [console_scripts]
        dealer=dealer.cli:cli
    ''',
	cmdclass = {'test': run_tests}
)
