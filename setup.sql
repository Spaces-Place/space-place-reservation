CREATE TABLE IF NOT EXISTS reservation (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_number VARCHAR(20),
    space_id VARCHAR(255),
    space_name VARCHAR(255),
    user_id VARCHAR(255),
    user_name VARCHAR(255),
    payment_id INT,
    r_status ENUM('PENDING', 'COMPLETED', 'FAILED', 'CANCELED'),
    reservation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    use_date DATETIME,
    start_time DATETIME,
    end_time DATETIME,
    INDEX idx_reservation_order_number (order_number)
);