-- Create schemas for donor and hospital services
CREATE SCHEMA IF NOT EXISTS donor_schema;
CREATE SCHEMA IF NOT EXISTS hospital_schema;

-- Grant privileges to the blood_user
GRANT ALL PRIVILEGES ON SCHEMA donor_schema TO blood_user;
GRANT ALL PRIVILEGES ON SCHEMA hospital_schema TO blood_user;