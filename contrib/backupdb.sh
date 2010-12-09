#! /bin/bash

export PGPASSWORD=lasso
pg_dump -h localhost -U lasso lasso > $HOME/dbdump.sql
