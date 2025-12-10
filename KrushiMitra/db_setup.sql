-- Create database if not exists
CREATE DATABASE IF NOT EXISTS agri_store;
USE agri_store;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    phone VARCHAR(20)
);

-- Suppliers table
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    phone VARCHAR(20)
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

-- Deliveries table
CREATE TABLE IF NOT EXISTS deliveries (
    delivery_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT,
    delivery_date DATE NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

-- Sales table
CREATE TABLE IF NOT EXISTS sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    sale_date DATE NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Sales_items table (junction table for sales and products)
CREATE TABLE IF NOT EXISTS sales_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT,
    product_id INT,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Product_Supplier relationship (junction table for many-to-many relationship)
CREATE TABLE IF NOT EXISTS product_supplier (
    product_id INT,
    supplier_id INT,
    PRIMARY KEY (product_id, supplier_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

-- Insert some sample data

-- Sample users (admin and regular user)
INSERT INTO users (username, password, role) VALUES
('admin', 'admin123', 'admin'),
('user', 'user123', 'staff');

-- Sample customers
INSERT INTO customers (name, address, phone) VALUES
('Rahul Sharma', 'Pune, Maharashtra', '9876543210'),
('Priya Patel', 'Nashik, Maharashtra', '8765432109'),
('Amit Kumar', 'Nagpur, Maharashtra', '7654321098');

-- Sample suppliers
INSERT INTO suppliers (name, address, phone) VALUES
('GreenGrow Fertilizers', 'Mumbai, Maharashtra', '9988776655'),
('FarmTech Seeds', 'Kolhapur, Maharashtra', '8877665544'),
('AgriTools Equipment', 'Aurangabad, Maharashtra', '7766554433');

-- Sample products
INSERT INTO products (name, price) VALUES
('Organic Fertilizer (50kg)', 850.00),
('Wheat Seeds (10kg)', 550.00),
('Pesticide Spray (5L)', 1200.00),
('Tractor Rental (per day)', 2500.00),
('Irrigation Pipes (100m)', 3500.00);

-- Sample deliveries
INSERT INTO deliveries (supplier_id, delivery_date, quantity) VALUES
(1, '2023-09-15', 100),
(2, '2023-09-20', 50),
(3, '2023-09-25', 30);

-- Link products to suppliers
INSERT INTO product_supplier (product_id, supplier_id) VALUES
(1, 1), -- Organic Fertilizer supplied by GreenGrow
(2, 2), -- Wheat Seeds supplied by FarmTech
(3, 1), -- Pesticide also by GreenGrow
(4, 3), -- Tractor Rental by AgriTools
(5, 3); -- Irrigation Pipes by AgriTools

-- Sample sales
INSERT INTO sales (customer_id, sale_date) VALUES
(1, '2023-10-01'),
(2, '2023-10-03'),
(3, '2023-10-05');

-- Sample sales items
INSERT INTO sales_items (sale_id, product_id, quantity, price) VALUES
(1, 1, 2, 850.00),  -- Rahul bought 2 bags of fertilizer
(1, 2, 1, 550.00),  -- and 1 bag of wheat seeds
(2, 3, 1, 1200.00), -- Priya bought pesticide
(3, 5, 2, 3500.00); -- Amit bought irrigation pipes 