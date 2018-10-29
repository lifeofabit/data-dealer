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
Too many things to count