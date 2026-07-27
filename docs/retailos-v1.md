# RetailOS v1

## Core Goal

Build a simple operating system for retailers to manage products, sales, and customers efficiently from a single platform.

The system should replace manual tracking methods and give retailers a reliable way to know:
- what products they have
- what they sell
- who buys from them

---

# Core Features (V1)

RetailOS v1 contains only three core features:

## 1. Product Management

### Purpose
Allow retailers to maintain accurate product information and inventory levels.

### Capabilities

Users can:
- Add products
- Edit product details
- View product information
- Track inventory levels

### Product Data

- Product name
- Price
- Stock quantity

### System Behavior

When a product is sold:
- inventory is automatically reduced

---

## 2. Sales Processing

### Purpose
Allow retailers to record and manage transactions.

### Capabilities

Users can:
- Select products
- Create sales transactions
- Generate receipts
- Track daily sales

### Sales Flow

1. User selects products
2. User enters quantity
3. System calculates total amount
4. Transaction is saved
5. Inventory is updated

### Sales Data

- Product sold
- Quantity
- Total amount
- Date

---

## 3. Customer Tracking

### Purpose
Help retailers maintain customer information and purchase history.

### Capabilities

Users can:
- Save customer information
- Attach customers to sales
- View customer purchase history

### Customer Data

- Name
- Contact information

---

# User Flow

## First Time Setup

1. User creates an account
2. User logs into the system
3. User adds products

---

## Daily Usage

1. User logs into the system
2. User checks products and inventory
3. User selects products to create a sale
4. System processes the transaction
5. Inventory is automatically updated
6. Customer information is saved with the transaction

---

# Basic Data Model

## Products

Stores all products available in the business.

Fields:

- id
- name
- price
- stock

---

## Customers

Stores customer information.

Fields:

- id
- name
- contact

---

## Sales

Stores transaction records.

Fields:

- id
- product_id
- customer_id
- quantity
- total
- date

---

# V1 Non-Goals

The following are not included in V1:

- Advanced analytics
- AI recommendations
- Automated business decisions
- Complex reporting
- Payment integrations
- Multi-store management

---

# Core Principle

RetailOS v1 should answer three simple questions:

1. What products do I have?
2. What have I sold?
3. Who are my customers?