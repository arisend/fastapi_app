#!/bin/bash
set -e
set -x

echo "******PostgreSQL initialisation******"
gosu docker psql -h localhost -p 5432 -U docker -d $docker -a -f createDatabase.sql