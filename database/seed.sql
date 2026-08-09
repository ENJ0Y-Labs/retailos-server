-- database/seed.sql
BEGIN TRANSACTION;

-- USERS
INSERT INTO users (name, email, password_hash, created_at) VALUES
('John Adeyemi', 'john@retailos.test', '$2b$12$MOCKHASHnotarealbcrypt0000000000000000000000', '2026-07-20 08:00:00'),
('Amaka Obi', 'amaka@retailos.test', '$2b$12$MOCKHASHnotarealbcrypt1111111111111111111111', '2026-07-21 09:30:00')
ON CONFLICT(id) DO UPDATE SET
name = excluded.name,
email = excluded.email,
password_hash = excluded.password_hash,
created_at = excluded.created_at;

-- STORES
INSERT INTO stores (user_id, name, created_at) VALUES
(1, 'Adeyemi General Store', '2026-07-20 08:05:00'),
(2, 'Amaka Mini Mart', '2026-07-21 09:35:00')
ON CONFLICT(id) DO UPDATE SET
user_id = excluded.user_id,
name = excluded.name,
created_at = excluded.created_at;

-- PRODUCTS
INSERT INTO products (store_id, name, price, stock_quantity, low_stock_threshold, created_at, updated_at) VALUES
(1, 'Rice (50kg bag)', 45000.00, 20, 5, '2026-07-20 08:10:00', '2026-07-20 08:10:00'),
(1, 'Vegetable Oil (5L)', 12000.00, 15, 4, '2026-07-20 08:11:00', '2026-07-20 08:11:00'),
(1, 'Coca-Cola (35cl)', 350.00, 100, 20, '2026-07-20 08:12:00', '2026-07-20 08:12:00'),
(2, 'Bread (loaf)', 1200.00, 30, 8, '2026-07-21 09:40:00', '2026-07-21 09:40:00'),
(2, 'Eggs (crate)', 3500.00, 2, 5, '2026-07-21 09:41:00', '2026-07-21 09:41:00'),
(2, 'Milk (1L)', 1500.00, 25, 5, '2026-07-21 09:42:00', '2026-07-21 09:42:00')
ON CONFLICT(id) DO UPDATE SET
store_id = excluded.store_id,
name = excluded.name,
price = excluded.price,
stock_quantity = excluded.stock_quantity,
low_stock_threshold = excluded.low_stock_threshold,
created_at = excluded.created_at,
updated_at = excluded.updated_at;

-- SALES
INSERT INTO sales (store_id, created_at) VALUES
(1, '2026-07-28 10:15:00'),
(1, '2026-07-29 09:00:00'),
(2, '2026-07-29 08:20:00')
ON CONFLICT(id) DO UPDATE SET
store_id = excluded.store_id,
created_at = excluded.created_at;

-- SALE ITEMS
INSERT INTO sale_items (sale_id, product_id, quantity, price_at_sale, total) VALUES
(1, 2, 3, 12000.00, 36000.00),
(2, 1, 2, 45000.00, 90000.00),
(2, 3, 5, 350.00, 1750.00),
(3, 5, 1, 3500.00, 3500.00),
(3, 4, 4, 1200.00, 4800.00)
ON CONFLICT(id) DO UPDATE SET
sale_id = excluded.sale_id,
product_id = excluded.product_id,
quantity = excluded.quantity,
price_at_sale = excluded.price_at_sale,
total = excluded.total;

-- ALERTS
INSERT INTO alerts (store_id, product_id, type, message, is_resolved, created_at) VALUES
(2, 5, 'low_stock', 'Eggs (crate) stock is below threshold (2 left, threshold 5)', 0, '2026-07-29 07:05:00'),
(1, NULL, 'no_sales', 'No sales recorded on 2026-07-27', 1, '2026-07-27 23:59:00')
ON CONFLICT(id) DO UPDATE SET
store_id = excluded.store_id,
product_id = excluded.product_id,
type = excluded.type,
message = excluded.message,
is_resolved = excluded.is_resolved,
created_at = excluded.created_at;

COMMIT;