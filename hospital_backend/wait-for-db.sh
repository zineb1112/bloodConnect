#!/bin/bash
# wait-for-db.sh

set -e

host="$1"
shift
cmd="$@"

echo "Waiting for PostgreSQL at $host..."

# Wait for PostgreSQL to be ready
until PGPASSWORD=$DB_PASSWORD psql -h "$host" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up - executing command"

# Check if schemas exist, create them if not
if [ "$DB_NAME" = "blood_db" ]; then
  echo "Checking/creating database schemas..."
  PGPASSWORD=$DB_PASSWORD psql -h "$host" -U "$DB_USER" -d "$DB_NAME" <<-EOSQL
    CREATE SCHEMA IF NOT EXISTS donor_schema;
    CREATE SCHEMA IF NOT EXISTS hospital_schema;
    GRANT ALL ON SCHEMA donor_schema TO $DB_USER;
    GRANT ALL ON SCHEMA hospital_schema TO $DB_USER;
EOSQL
fi

exec $cmd