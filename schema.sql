CREATE DATABASE IF NOT EXISTS ewaste_blockchain CHARACTER SET utf8mb4;
USE ewaste_blockchain;
CREATE TABLE IF NOT EXISTS blocks (
 block_index INT PRIMARY KEY,
 timestamp DATETIME(6) NOT NULL,
 proof BIGINT NOT NULL,
 previous_hash VARCHAR(64) NOT NULL,
 block_hash VARCHAR(64) NOT NULL
);
CREATE TABLE IF NOT EXISTS transactions (
 id BIGINT AUTO_INCREMENT PRIMARY KEY,
 block_index INT NOT NULL,
 timestamp DATETIME(6) NOT NULL,
 sender VARCHAR(255) NOT NULL,
 recipient VARCHAR(255) NOT NULL,
 ewaste_type VARCHAR(100) NOT NULL,
 condition_status VARCHAR(100) NOT NULL,
 serial_number VARCHAR(255) NOT NULL,
 hazardous_materials TEXT,
 INDEX (block_index),
 FOREIGN KEY (block_index) REFERENCES blocks(block_index)
);
