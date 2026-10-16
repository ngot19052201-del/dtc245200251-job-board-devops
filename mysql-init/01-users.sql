-- MySQL User Grants & Database Initialization
-- Student: Truong Thi Bich Ngoc - DTC245200251

CREATE DATABASE IF NOT EXISTS `jobboard_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Application User (Non-root)
CREATE USER IF NOT EXISTS 'jobuser'@'%' IDENTIFIED BY 'JobPass@2026_Secure';
GRANT ALL PRIVILEGES ON `jobboard_db`.* TO 'jobuser'@'%';

-- Prometheus MySQL Exporter User
CREATE USER IF NOT EXISTS 'exporter'@'%' IDENTIFIED BY 'ExporterPass@2026' WITH MAX_USER_CONNECTIONS 3;
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'exporter'@'%';

FLUSH PRIVILEGES;
