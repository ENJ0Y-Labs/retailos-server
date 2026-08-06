-- database\schema.sql
PRAGMA foreign_keys = ON;

-- 1. USERS
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash   TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 2. STORES
CREATE TABLE IF NOT EXISTS stores (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         TEXT NOT NULL,
    name            TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. PRODUCTS
CREATE TABLE IF NOT EXISTS products (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    store_id            TEXT NOT NULL,
    name                TEXT NOT NULL,
    price               NUMERIC NOT NULL CHECK (price >= 0),
    stock_quantity      INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    low_stock_threshold INTEGER,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE
);

-- 4. SALES
CREATE TABLE IF NOT EXISTS sales (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    store_id    TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE
);

-- 5. SALE ITEMS
CREATE TABLE IF NOT EXISTS sale_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id         TEXT NOT NULL,
    product_id      TEXT NOT NULL,
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    price_at_sale   NUMERIC NOT NULL CHECK (price_at_sale >= 0),
    total           NUMERIC NOT NULL CHECK (total >= 0),

    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);

-- 6. ALERTS
CREATE TABLE IF NOT EXISTS alerts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    store_id    TEXT NOT NULL,
    product_id  TEXT,
    type        TEXT NOT NULL CHECK (type IN ('low_stock', 'sales_drop', 'no_sales')),
    message     TEXT NOT NULL,
    is_resolved INTEGER NOT NULL DEFAULT 0 CHECK (is_resolved IN (0, 1)),
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_stores_user_id        ON stores(user_id);
CREATE INDEX IF NOT EXISTS idx_products_store_id     ON products(store_id);
CREATE INDEX IF NOT EXISTS idx_sales_store_id        ON sales(store_id);
CREATE INDEX IF NOT EXISTS idx_sales_created_at      ON sales(created_at);
CREATE INDEX IF NOT EXISTS idx_sale_items_sale_id    ON sale_items(sale_id);
CREATE INDEX IF NOT EXISTS idx_sale_items_product_id ON sale_items(product_id);
CREATE INDEX IF NOT EXISTS idx_alerts_store_id       ON alerts(store_id);
CREATE INDEX IF NOT EXISTS idx_alerts_product_id     ON alerts(product_id);
CREATE INDEX IF NOT EXISTS idx_alerts_type           ON alerts(type);