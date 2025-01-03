CREATE DATABASE qr_data;

USE qr_data;

CREATE TABLE scan_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone_model VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    qr_data TEXT NOT NULL,
    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);