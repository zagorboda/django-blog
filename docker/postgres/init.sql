CREATE USER admin WITH PASSWORD 'admin';

CREATE DATABASE docker_db;
GRANT ALL PRIVILEGES ON DATABASE docker_db TO admin;
ALTER USER admin CREATEDB;
