#!/bin/bash
set -e

# Read secrets from mounted Docker secrets files
DB_NAME=$(cat /run/secrets/db_name)
DB_USER=$(cat /run/secrets/db_username)
DB_PASSWORD=$(cat /run/secrets/db_password)

# 1. Create database and user if they don’t exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
    -- Create the database if it doesn't exist
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME') THEN
            CREATE DATABASE $DB_NAME;
        END IF;
    END
    \$\$;

    -- Create the user if it doesn't exist
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$DB_USER') THEN
            CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
        END IF;
    END
    \$\$;

    -- Grant all privileges on the database to the user
    GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOSQL

# 2. Create table and grant privileges within the target database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DB_NAME" <<-EOSQL
    -- Create the xor_table if it doesn't exist
    CREATE TABLE IF NOT EXISTS xor_table (
        id SERIAL PRIMARY KEY,
        xor_value TEXT NOT NULL
    );

    -- Grant privileges on the table and its sequence
    GRANT ALL PRIVILEGES ON TABLE xor_table TO $DB_USER;
    GRANT INSERT ON TABLE xor_table TO $DB_USER;
    GRANT CONNECT ON DATABASE $DB_NAME TO $DB_USER;
    GRANT USAGE, SELECT ON SEQUENCE xor_table_id_seq TO $DB_USER;
EOSQL
