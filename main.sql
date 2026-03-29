CREATE TABLE products (
    product_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(140) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    PRIMARY KEY (product_id)
);