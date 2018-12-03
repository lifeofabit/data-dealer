# data-dealer (0.0.4)
A Python wrapper for data virtualization, ETL and serialization as a pandas dataframe.  

## Installation
``` pip install data-dealer```

## Integrations
- .json and .csv file formats
- MS SQL Server
- AWS DynamoDB
- AWS Redshift
- AWS Athena (In Development)
- AWS s3 (In Development)

## Registry
In order to begin using the data dealer, you must register some suppliers. The following CLI commands will help you manage your registry

#### Register a new supplier

``` dealer registry -s test-supplier -p "dbms=mssql;host=localhost;uname=MyUsername;pword=MyPassword" add``` 

Valid supplier properties:
- dbms (athena, mssql, dynamo)
- host
- port
- uname
- pword
- aws_key
- aws_secret

#### Load a registry from file
``` dealer registry -s ~/registry.yaml load ```

#### Display current registry
``` dealer registry [display|show] ```

#### Remove a supplier from the registry
``` dealer registry -s test-supplier remove ```

## To-Do List:
- Create s3 connection to pull down files and serialize
- Fix FileNotFoundError when trying to write to a path where dir doesn't exist
- Fix registry get issue when supplier is not present in registry
- Add exception handling for pymssql OperationalError (unable to connect or does not exist 20009)
- Make some external modules optional (pymssql, psycopg)
Too many things to count