# RetailOS v1

## Core Goal
Build a simple operating system for retailers to manage products, sales, and customers efficiently from a single platform.

## 3 Features Only
1. **Product Management**
   - Add products
   - Edit product details
   - Track inventory levels

2. **Sales Processing**
   - Record transactions
   - Generate receipts
   - Track daily sales

3. **Customer Tracking**
   - Store customer information
   - Track purchase history

## User Flow
1. User logs into the system  
2. User adds or updates products  
3. User selects products to create a sale  
4. System processes the transaction  
5. Inventory is automatically updated  
6. Customer information is saved with the transaction  

## Basic Data Model

### Products
- id
- name
- price
- stock

### Customers
- id
- name
- contact

### Sales
- id
- product_id
- customer_id
- quantity
- total
- date