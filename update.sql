UPDATE products
SET 
    stock_quantity = stock_quantity + 17,
    price = price * 1.05
WHERE 
    name LIKE '%Mouse%';