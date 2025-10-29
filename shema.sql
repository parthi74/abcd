-- Compatible Schema for MySQL 5.5+ (InnoDB for FKs, inline indexes)
CREATE DATABASE IF NOT EXISTS amconnect_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE amconnect_db;

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Surveys table
CREATE TABLE IF NOT EXISTS surveys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    answers TEXT NOT NULL,
    score INT NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    INDEX idx_company_id (company_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Contacts table
CREATE TABLE IF NOT EXISTS contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Verify
SHOW TABLES;
DESCRIBE companies;
DESCRIBE surveys;
DESCRIBE contacts;

-- Samples
-- INSERT INTO companies (name, email, phone, category) VALUES ('Test Corp', 'test@example.com', '123-456-7890', 'startup');
-- SELECT * FROM surveys WHERE company_id = 1;
-- SELECT * FROM contacts JOIN companies ON contacts.company_id = companies.id;
-- UPDATE surveys SET score = 85 WHERE id = 1;
-- DELETE FROM surveys WHERE completed_at < DATE_SUB(NOW(), INTERVAL 30 DAY);