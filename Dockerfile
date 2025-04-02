FROM mcr.microsoft.com/mssql/server:2022-latest

ENV ACCEPT_EULA=Y
ENV MSSQL_PID=Developer

USER root

RUN apt-get update && \
    apt-get install -y mssql-tools unixodbc-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="$PATH:/opt/mssql-tools/bin"