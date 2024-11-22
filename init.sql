-- Create user if not exists
CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED WITH mysql_native_password BY 'app_password';

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS logistics_db;

-- Grant privileges
GRANT ALL PRIVILEGES ON logistics_db.* TO 'app_user'@'%';

-- In case the user already exists, update the password
ALTER USER 'app_user'@'%' IDENTIFIED WITH mysql_native_password BY 'app_password';

-- Make sure privileges are applied
FLUSH PRIVILEGES;

-- Switch to the database
USE logistics_db;

-- You can add any initial table creation or seed data below this line
-- For example:
-- CREATE TABLE IF NOT EXISTS example_table (
--     id INT PRIMARY KEY AUTO_INCREMENT,
--     name VARCHAR(255) NOT NULL
-- ); 