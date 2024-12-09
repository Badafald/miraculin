#!/bin/bash

# Read secrets from mounted Docker secrets files
DB_NAME=$(cat /run/secrets/db_name)
DB_USER=$(cat /run/secrets/db_username)
DB_PASSWORD=$(cat /run/secrets/db_password)

# Initialize database and user, replace placeholders with actual secrets
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

-- 1. Create the database (if it doesn't already exist)
DO
\$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME') THEN
        PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE $DB_NAME');
    END IF;
END
\$\$;

-- 2. Create the user with the specified password (if the user doesn't exist)
DO
\$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
    END IF;
END
\$\$;

-- 3. Grant privileges to the user on the database
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- 4. Connect to the newly created database
\c $DB_NAME;

-- 5. Create the xor_table table (if it doesn't already exist)
CREATE TABLE IF NOT EXISTS xor_table (
    id SERIAL PRIMARY KEY, -- Auto-incrementing ID (backed by a sequence)
    xor_value TEXT NOT NULL -- Field to store the encrypted strings
);

-- 6. Grant all privileges on the table to the user
GRANT ALL PRIVILEGES ON TABLE xor_table TO $DB_USER;

-- 7. Additional granular privileges on the table and sequence
GRANT INSERT ON TABLE xor_table TO $DB_USER;
GRANT CONNECT ON DATABASE $DB_NAME TO $DB_USER;
GRANT USAGE, SELECT ON SEQUENCE xor_table_id_seq TO $DB_USER;

EOSQL
