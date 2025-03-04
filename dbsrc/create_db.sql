-- Connect to PostgreSQL as a superuser (e.g., postgres)
\c postgres

-- Create the database
CREATE DATABASE lab_requisition_db;

-- Create the user with a password
CREATE USER admin WITH ENCRYPTED PASSWORD 'LETMEIN';

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON DATABASE lab_requisition_db TO admin;

-- Grant additional privileges
\c lab_requisition_db
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON TABLE django_migrations TO admin;