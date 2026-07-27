RetailOS — Database Design (V1)

Overview

This document defines the database structure for RetailOS v1.

The goal is to:

- support the core features
- keep the schema simple and scalable
- ensure clean relationships between entities

Core Entities

1. Users
2. Stores
3. Products
4. Sales
5. Alerts

1. 👤 Users Table

Purpose

Stores account information for each user.

Fields

- id UUID primary key
- name string
- email string unique
- password_hash string
- created_at timestamp

2. 🏪 Stores Table

Purpose

Represents a business owned by a user.

Fields

- id UUID primary key
- user_id foreign key to Users.id
- name string
- created_at timestamp

Relationship

- one user can own one or more stores
- one store has one owner for now

3. 📦 Products Table

Purpose

Stores all products in a store.

Fields

- id UUID primary key
- store_id foreign key to Stores.id
- name string
- price decimal
- stock_quantity integer
- low_stock_threshold integer optional
- created_at timestamp

Notes

- stock_quantity is updated after each sale or restock
- threshold is used for alert generation

4. 💰 Sales Table

Purpose

Records every sale transaction.

Fields

- id UUID primary key
- store_id foreign key to Stores.id
- created_at timestamp

4.1 🧾 Sale_Items Table

Purpose

Handles products within each sale and supports multiple products per sale.

Fields

- id UUID primary key
- sale_id foreign key to Sales.id
- product_id foreign key to Products.id
- quantity integer
- price_at_sale decimal
- total decimal

Why this structure?

Instead of storing one product per sale:

- it supports multiple products in a single transaction
- it is more realistic
- it scales better

5. 🚨 Alerts Table

Purpose

Stores system-generated alerts.

Fields

- id UUID primary key
- store_id foreign key to Stores.id
- product_id foreign key to Products.id, nullable
- type string
  - low_stock
  - sales_drop
  - no_sales
- message string
- is_resolved boolean default false
- created_at timestamp

🔄 Relationships Summary

- Users → Stores (1:N)
- Stores → Products (1:N)
- Stores → Sales (1:N)
- Sales → Sale_Items (1:N)
- Products → Sale_Items (1:N)
- Stores → Alerts (1:N)

⚙️ Core Data Behaviors

1. Recording a sale

When a sale is created:

- insert into Sales
- insert items into Sale_Items
- reduce product stock_quantity
- trigger alert checks

2. Updating inventory

When stock is updated:

- update product stock_quantity
- re-check low stock alerts

3. Generating alerts

The system checks:

Low stock

If product stock_quantity falls below threshold, create an alert.

Sales drop

Compare today’s total with yesterday’s total and create an alert if the drop exceeds the configured threshold.

No sales

If no sales are recorded on a day, create an alert.

📊 Derived Data

These values are calculated when needed:

- daily sales total
- sales comparison by day
- product performance trends

⚠️ Design Decisions

1. No Insights table

Insights are generated dynamically, not stored.

Reason:

- avoids stale data
- keeps the system simple

2. No Reports table

Reports are computed from sales data.

3. Keep schema minimal

Only store what is necessary for V1.

🚀 Future Extensions

- customers table
- payments table
- expenses table
- multi-user roles
- audit logs
- financial summaries

🔑 Guiding Principle

The database must answer:

«What happened in the business?»

Everything else builds from that.