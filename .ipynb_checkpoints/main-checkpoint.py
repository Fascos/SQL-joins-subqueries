 # main.py

import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('data.sqlite')


# =========================
# STEP 0 (schema check)
# =========================
schema = pd.read_sql("""SELECT * FROM sqlite_master;""", conn)


# =========================
# STEP 1
# Boston employees
# =========================
df_boston = pd.read_sql(
    '''
    SELECT 
        employees.firstName, 
        employees.lastName, 
        employees.jobTitle
    FROM employees
    JOIN offices 
        ON employees.officeCode = offices.officeCode
    WHERE offices.city = 'Boston'
    ''', conn
)

# =========================
# STEP 2
# Offices with zero employees
# =========================
df_zero_emp = pd.read_sql(
    '''
    SELECT 
        o.officeCode,
        o.city,
        COUNT(e.employeeNumber) AS num_of_employees
    FROM offices o
    LEFT JOIN employees e
        ON o.officeCode = e.officeCode
    GROUP BY o.officeCode, o.city
    HAVING COUNT(e.employeeNumber) = 0;
    ''', conn
)


# =========================
# STEP 3
# All employees with location
# =========================
df_employee = pd.read_sql(
    '''
    SELECT e.firstName, e.lastName, o.city, o.state
    FROM employees AS e
    LEFT JOIN offices AS o
        ON e.officeCode = o.officeCode
    ORDER BY e.firstName, e.lastName;
    ''', conn
)


# =========================
# STEP 4
# Customers without orders
# =========================
df_contacts = pd.read_sql(
    '''
    SELECT c.contactFirstName, c.contactLastName, c.phone, c.salesRepEmployeeNumber
    FROM customers AS c
    LEFT JOIN orders AS o
        ON c.customerNumber = o.customerNumber
    WHERE o.customerNumber IS NULL
    ORDER BY c.contactLastName;
    ''', conn
)


# =========================
# STEP 5
# Payments
# =========================
df_payment = pd.read_sql(
    '''
    SELECT 
        c.contactFirstName,
        c.contactLastName,
        CAST(p.amount AS INTEGER) AS amount,
        p.paymentDate
    FROM customers AS c
    JOIN payments AS p
        ON c.customerNumber = p.customerNumber
    ORDER BY amount DESC;
    ''', conn
)


# =========================
# STEP 6
# High credit employees
# =========================
df_credit = pd.read_sql(
    '''
    SELECT 
        e.employeeNumber,
        e.firstName,
        e.lastName,
        COUNT(c.customerNumber) AS num_of_customers
    FROM employees AS e
    JOIN customers AS c
        ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY e.employeeNumber
    HAVING AVG(c.creditLimit) > 90000
    ORDER BY num_of_customers DESC;
    ''', conn
)


# =========================
# STEP 7
# Product sales
# =========================
df_product_sold = pd.read_sql(
    '''
    SELECT 
        p.productName,
        COUNT(od.orderNumber) AS numorders,
        SUM(od.quantityOrdered) AS totalunits
    FROM products AS p
    JOIN orderdetails AS od
        ON p.productCode = od.productCode
    GROUP BY p.productCode
    ORDER BY totalunits DESC;
    ''', conn
)


# =========================
# STEP 8
# Product customers
# =========================
df_total_customers = pd.read_sql(
    '''
    SELECT 
        p.productName,
        p.productCode,
        COUNT(DISTINCT o.customerNumber) AS numpurchasers
    FROM products AS p
    JOIN orderdetails AS od
        ON p.productCode = od.productCode
    JOIN orders AS o
        ON od.orderNumber = o.orderNumber
    GROUP BY p.productCode
    ORDER BY numpurchasers DESC;
    ''', conn
)



df_customers = pd.read_sql (
    '''
    SELECT 
        o.officeCode,o.city,
        COUNT(c.customerNumber) AS n_customers
    FROM offices as o
    JOIN employees as e
        ON o.officeCode = e.officeCode
    Join customers as c
        ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY o.officeCode,o.city
    ORDER BY n_customers DESC;
    ''', conn
)



# =========================
# STEP 9 (subquery)
# Low customer products
# =========================
df_low_products = pd.read_sql(
    '''
    SELECT od.productCode
    FROM orderdetails od
    JOIN orders o
        ON od.orderNumber = o.orderNumber
    GROUP BY od.productCode
    HAVING COUNT(DISTINCT o.customerNumber) <= 19;
    ''', conn
)


# =========================
# STEP 10
# Employees linked to low-popular products
# =========================
df_under_20 = pd.read_sql(
    '''
    SELECT DISTINCT
        e.employeeNumber,
        e.firstName,
        e.lastName,
        o.city,
        o.officeCode
    FROM offices o
    JOIN employees e
        ON o.officeCode = e.officeCode
    JOIN customers c
        ON e.employeeNumber = c.salesRepEmployeeNumber
    JOIN orders ord
        ON c.customerNumber = ord.customerNumber
    JOIN orderdetails od
        ON ord.orderNumber = od.orderNumber
    WHERE od.productCode IN (
        SELECT od2.productCode
        FROM orderdetails od2
        JOIN orders ord2
            ON od2.orderNumber = ord2.orderNumber
        GROUP BY od2.productCode
        HAVING COUNT(DISTINCT ord2.customerNumber) <= 19
    );
    ''', conn
)