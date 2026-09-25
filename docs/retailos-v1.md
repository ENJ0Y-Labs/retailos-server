# RetailOS V1

## Core Goal

RetailOS V1 is a practical retail management backend for managing products, inventory, sales, customers, alerts, and daily business activity from one system.

The V1 foundation is intentionally focused on reliable operational workflows.

# Core Features

## 1. Authentication and Store Access

Users can:

- register
- log in
- log out

Protected operations require an authenticated session.

Store-level resources are checked against the authenticated user so one user cannot operate on another user's store.

## 2. Product Management

Users can:

- create products
- view a product
- list products
- update product details
- delete products
- adjust stock

Product data includes:

- name
- price
- stock quantity
- low-stock threshold

The backend validates product data and prevents negative prices or negative stock.

## 3. Inventory Management

Inventory changes happen through controlled operations.

Manual adjustments record an inventory movement containing:

- quantity change
- previous quantity
- new quantity
- reason
- user
- product
- store

Sales also reduce inventory and record the movement as part of the sale transaction.

## 4. Sales Processing

Users can:

- create sales
- include multiple products in one sale
- optionally attach a customer
- list sales
- retrieve a sale
- retrieve receipt data

### Sale flow

1. Select products.
2. Enter quantities.
3. Optionally select a customer.
4. Send the transaction.
5. Backend validates the request.
6. Backend checks stock.
7. Backend calculates totals.
8. Backend saves the sale and sale items.
9. Backend reduces inventory.
10. Backend records inventory movements.
11. Backend commits the transaction.

The backend is the source of truth for totals.

## 5. Duplicate Sale Protection

Sales can include a client_transaction_id.

The identifier is unique.

If a client retries a transaction that was already processed, the backend returns the existing sale instead of processing the inventory reduction again.

## 6. Customer Tracking

Users can:

- create customers
- list customers
- attach customers to sales
- view customer purchase history

Customer data includes:

- name
- contact

Purchase history is derived from the customer's sales and sale items.

## 7. Alerts

The V1 alert system currently supports low-stock alert generation.

A product is considered low stock when:

stock_quantity <= low_stock_threshold

Users can:

- generate low-stock alerts
- list unresolved alerts
- resolve alerts

The alert model also supports future alert types such as sales-drop and no-sales.

## 8. Dashboard

The dashboard provides:

- product count
- low-stock count
- open-alert count
- today's sales count
- today's sales total

The daily summary provides:

- date
- number of sales
- total sales
- individual sales with timestamps and totals

## 9. Receipt Generation

The sales service provides structured receipt data from persisted records.

Receipt information is based on:

- sale
- customer
- sale items
- quantities
- sale-time prices
- item totals
- final sale total
- timestamp

# Main API Areas

| Area | Main responsibility |
|---|---|
| /auth | Registration, login, logout |
| /product | Product and inventory management |
| /customers | Customer management and purchase history |
| /sales | Sales, sale items, and receipts |
| /alerts | Low-stock alerts and resolution |
| /dashboard | Dashboard metrics and daily summary |

# V1 Data Model

Core entities:

- User
- Store
- Product
- Customer
- Sale
- SaleItem
- InventoryMovement
- Alert

Important relationships:

- User → Stores
- Store → Products
- Store → Customers
- Store → Sales
- Customer → Sales
- Sale → SaleItems
- Product → SaleItems
- Product → InventoryMovements
- Sale → InventoryMovements
- Store → Alerts

# Data Integrity

V1 enforces important business rules:

- protected operations require authentication
- store access is verified
- prices cannot be negative
- stock cannot become negative
- sale totals are calculated server-side
- insufficient stock prevents a sale
- duplicate client transactions do not process twice
- inventory changes are recorded
- sale inventory updates are transactional

# V1 Non-Goals

The following remain outside the current V1 implementation:

- advanced AI recommendations
- automated purchasing
- payment integrations
- accounting
- expenses
- advanced analytics
- subscriptions
- full multi-store administration
- offline synchronization

# V1 Definition of Done

RetailOS V1 is functionally grounded when a user can:

1. create an account
2. authenticate
3. create and manage products
4. adjust inventory
5. record sales
6. attach customers to sales
7. inspect customer history
8. review low-stock alerts
9. resolve alerts
10. inspect dashboard metrics
11. inspect the daily summary
12. retrieve receipt information

The next development phase should extend this foundation rather than duplicate or bypass its core business rules.
