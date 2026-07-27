RetailOS — User Flow (V1)

Overview

This document defines how a user interacts with RetailOS step by step.

The focus is simplicity, clarity, and daily usage.

Primary goal:

Make it effortless for the user to understand their business and take action.

1. 👤 User Type

Primary user

Retail business owner

Behavior

- opens the app once or multiple times daily
- wants quick answers, not deep analysis
- has limited time and attention

2. 🔐 Entry Flow

Step 1: User opens the app

Options:

- Login for existing users
- Register for new users

Step 2: Registration flow

User enters:

- name
- email
- password
- store name

Step 3: Initial setup

User adds at least one product:

- product name
- price
- stock quantity

Goal: get the user to a usable state quickly.

3. 🏠 Core Flow: Daily Usage

Step 1: User opens the app

User is taken directly to:

Your Business Today

Step 2: View Daily Business Brief

Section A: Sales summary

- Today’s Sales: ₦X
- Change from yesterday: +X% or -X%

Section B: Alerts

- low stock
- sales drop
- no activity

User actions:

- click an alert to view details
- mark as seen, if supported

Section C: Insights

- Restock Product A
- Sales declining for Product B

Step 3: Take action

From the dashboard, the user can:

Action 1: Record sale

- select products
- enter quantity
- confirm sale

Action 2: Update inventory

- increase or decrease stock
- used when restocking or correcting errors

Action 3: View product details

- see product performance
- view stock level

4. ➕ Secondary Flows

4.1 Record Sale Flow

1. User clicks Record Sale
2. Selects product
3. Enters quantity
4. System calculates total
5. User confirms

System:

- updates sales records
- reduces inventory
- re-evaluates alerts

4.2 Inventory Update Flow

1. User selects product
2. Updates stock quantity
3. Saves changes

System:

- updates inventory
- re-checks low stock alerts

4.3 View Alerts Flow

1. User clicks an alert
2. Sees:
   - description
   - affected product
   - suggested action

5. 🔁 System Flow Behind the Scenes

On login or dashboard load, the system:

1. calculates today’s sales
2. compares with previous sales
3. runs alert rules
4. generates insights
5. prepares the Daily Business Brief

6. ⚠️ Edge Flows

No data scenario

Show:

- No data available yet

Prompt the user to:

- add a product
- record first sale

First day usage

Show:

- Start recording sales to see insights

No alerts

Show:

- No issues detected today

7. 🎯 UX Principles

Fast access

The user should see value within 5 seconds of opening the app.

Minimal steps

No unnecessary screens.

Clear language

Avoid technical terms.

Action-oriented

Every screen should lead to an action.

8. 🧭 Navigation Structure

Simple structure:

- Dashboard
- Products
- Record Sale

Optional later:

- Reports
- Settings

9. 🧬 Core Loop

1. User opens the app
2. Sees Daily Business Brief
3. Notices an alert or insight
4. Takes action
5. Business improves
6. Returns the next day

10. 🔑 Final Rule

The user should never ask:

«What do I do here?»

The app should make the next step obvious.