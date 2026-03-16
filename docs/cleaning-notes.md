# Data Cleaning Notes

## Objective
The goal of the data cleaning process was to prepare the UK online retail transactional dataset for reliable sales, customer, and returns analysis in Power BI.

The raw dataset contained several issues that needed to be addressed before building visuals and measures, including cancelled invoices, returned transactions, missing customer IDs, and non-product records.

## Main Data Quality Issues Identified
The dataset included the following challenges:
- Cancelled invoices
- Returned transactions reflected through negative quantities
- Missing customer identifiers
- Non-product or special-code records
- Inconsistent record types for business analysis
- Need for a proper date dimension for time-based reporting

## Cleaning and Preparation Steps

### 1. Standardized data types
Column types were reviewed and adjusted to ensure correct modeling and calculations. This included fields such as:
- Invoice / order ID
- Product code
- Product description
- Quantity
- Unit price
- Customer ID
- Country
- Transaction date

### 2. Identified cancelled invoices
Cancelled transactions were identified and flagged so they could be analyzed separately or excluded from specific business views when needed.

This helped distinguish:
- normal sales activity
- cancelled activity
- returned value and net sales behavior

### 3. Flagged returned transactions
Returned transactions were identified using business logic based on transaction behavior, especially negative quantities.

This step was important for:
- calculating return value
- estimating return rate
- comparing sales vs returns
- understanding product-level return behavior

### 4. Classified line types
A line classification approach was used to separate valid product rows from non-product or special records.

This allowed the dashboard to distinguish between:
- core product sales
- special or administrative lines
- records that should not be treated as standard product transactions

The resulting classification supports the **Line Type** filter used in the report.

### 5. Reviewed missing values
Special attention was given to missing values, especially in customer-related fields.

Key decision:
- Missing `Customer_ID` values were important to identify because they affect customer-level analysis.
- These records may still be useful for transaction-level sales analysis, but they should be treated carefully in customer ranking visuals and customer-based KPIs.

### 6. Created business logic flags
Additional flags were created to support filtering and analysis, including logic related to:
- cancelled activity
- returned transactions
- valid product rows
- customer availability

These flags improved transparency and made DAX calculations easier to control.

### 7. Built a calendar table
A dedicated calendar table was created to support time intelligence and trend analysis.

This enabled:
- monthly trend visuals
- yearly filtering
- chronological sorting of time labels
- cleaner report design

### 8. Prepared fields for reporting
The cleaned dataset was structured to support key report metrics such as:
- total sales
- net sales
- orders
- unique customers
- average order value
- return value
- return rate

## Data Modeling Notes
The report model is centered on:
- an **Online Retail** transactional table
- a **Calendar** dimension table for time analysis

This structure supports trend analysis, KPI reporting, and interactive slicing by year.

## Assumptions Used
The cleaning process relied on the following analytical assumptions:
- Negative quantity transactions represent returns or reverse movements.
- Cancelled invoices should be identified separately from regular completed sales.
- Missing customer IDs reduce the reliability of customer-level analysis.
- Non-product or special-code rows should not always be treated as normal product sales.
- A separate calendar table is required for proper time-based reporting in Power BI.

## Reporting Impact
The cleaning process directly improved:
- consistency of KPI calculations
- accuracy of sales and returns comparisons
- quality of customer analysis
- usability of filters
- reliability of monthly reporting
