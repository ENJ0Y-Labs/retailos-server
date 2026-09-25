# RetailOS — User Flow (V1)

## Overview

RetailOS V1 is designed around a simple operational loop:

**Sign in → check the business → manage stock → record sales → review customers → handle alerts → review the day**

The backend supports these actions through authenticated, store-scoped API workflows.

## 1. Registration and Login

### New user

1. User submits registration details.
2. Server validates the request.
3. User account and initial store are created.
4. User can log in.

### Existing user

1. User submits email and password.
2. Server verifies credentials.
3. A session is created.
4. Protected endpoints become available.

### Logout

1. User sends logout request.
2. Server clears the authenticated session.
3. Protected endpoints require authentication again.

## 2. Product Setup

After login, a retailer can create products.

### Flow

1. User opens product management.
2. User provides:
   - product name
   - price
   - opening stock
   - low-stock threshold
3. Server validates the data.
4. Product is stored.
5. Product becomes available for sales.

### Product operations

The user can later:

- view one product
- list products
- edit product information
- adjust stock
- delete a product when it has no conflicting related records

## 3. Daily Dashboard Flow

1. User opens the dashboard.
2. Server verifies store access.
3. Server calculates current dashboard metrics.
4. User sees:
   - number of products
   - low-stock products
   - open alerts
   - today's sales count
   - today's sales total
5. User can open the daily summary for individual sales.

## 4. Record Sale Flow

### User actions

1. User starts a sale.
2. User selects one or more products.
3. User enters quantities.
4. User optionally selects a customer.
5. Client sends the sale request.

### Server actions

1. Authenticate the user.
2. Verify store access.
3. Validate products and quantities.
4. Read the relevant inventory records transactionally.
5. Check stock availability.
6. Calculate item totals.
7. Calculate the complete sale total.
8. Save the sale.
9. Save sale items.
10. Reduce stock.
11. Record inventory movements.
12. Commit the transaction.

### Result

The client receives the created sale and receipt information.

## 5. Duplicate Sale Protection

A client can send a client_transaction_id.

### Flow

1. Client sends a sale with a transaction ID.
2. Server checks whether that ID was already processed.
3. If it is new, the sale is processed normally.
4. If it already exists, the existing sale is returned.
5. Inventory is not reduced a second time.

This protects against duplicate submissions caused by retries or repeated client actions.

## 6. Customer Flow

### Create customer

1. User opens customer management.
2. User enters customer name and contact.
3. Server validates store access.
4. Customer is created.

### Attach customer to sale

1. User selects an existing customer while recording a sale.
2. Server verifies that the customer belongs to the same store.
3. Sale is created with the customer reference.

### View purchase history

1. User opens a customer.
2. Server verifies store access.
3. Server loads the customer's sales.
4. Each sale's items are included in the history.

## 7. Inventory Adjustment Flow

Used for restocking, corrections, or other manual stock changes.

1. User opens a product.
2. User submits a quantity change.
3. Server validates the quantity change.
4. Server calculates the new stock.
5. Server rejects the operation if stock would become negative.
6. Server updates the product.
7. Server creates an inventory movement record.
8. Server returns the updated product.

## 8. Alert Flow

### Generate low-stock alerts

1. User requests low-stock alert generation.
2. Server checks the store's products.
3. Products at or below their configured threshold are identified.
4. Missing unresolved alerts are created.
5. Existing unresolved alerts are not duplicated.

### Review alerts

1. User requests alerts.
2. Server returns unresolved alerts for the authorized store.
3. User reviews the affected product and message.

### Resolve alert

1. User selects an alert.
2. Server verifies that the alert belongs to the store.
3. Alert is marked resolved.
4. It no longer appears in the unresolved alert list.

## 9. Receipt Flow

After a sale:

1. User receives sale/receipt data.
2. User can request the receipt endpoint.
3. Server loads the persisted sale.
4. Receipt data is generated from stored sale items and totals.

The client does not control the final receipt total.

## 10. Error Flows

### Unauthorized request

If no valid session exists:

- protected endpoints return an authentication error
- no protected store data is returned

### Unauthorized store

If the authenticated user does not own or have access to the requested store:

- the request is rejected
- store data is not returned

### Invalid data

Examples:

- missing required fields
- negative price
- invalid quantity
- malformed JSON

The API returns a validation error.

### Insufficient stock

If a sale or stock adjustment would result in negative stock:

- the operation is rejected
- inventory remains unchanged

## 11. Core Daily Loop

1. Sign in.
2. Open dashboard.
3. Review sales and stock.
4. Review open alerts.
5. Add or adjust inventory when necessary.
6. Record sales.
7. Review customers and purchase history.
8. Review the daily summary.

## 12. Navigation Model

The client can organize V1 around:

- Dashboard
- Products
- Record Sale
- Customers
- Alerts
- Daily Summary

Settings and advanced reporting can be added later.

## 13. UX Principles

- Keep common operations short.
- Use clear business language.
- Show useful results immediately.
- Avoid asking the client to calculate business totals.
- Make errors understandable.
- Keep store boundaries invisible to the user but strict in the backend.

## Final Rule

The user should always understand what operation they are performing and what changed as a result.
