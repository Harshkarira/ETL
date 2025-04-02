#!/bin/bash
sleep 20

docker-compose exec -T mssql //opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "P@ssW0rdS3cuR3!" -Q "
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'KafkaDB')
BEGIN
    CREATE DATABASE KafkaDB
END
GO

USE KafkaDB
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'source_table')
BEGIN
    CREATE TABLE source_table (
        id INT PRIMARY KEY,
        name NVARCHAR(255) NOT NULL,
        age INT NOT NULL
    )
END
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'target_table')
BEGIN
    CREATE TABLE target_table (
        id INT PRIMARY KEY,
        name NVARCHAR(255) NOT NULL,
        age INT NOT NULL
    )
END
GO
"

echo "Successfully created DB and table's."