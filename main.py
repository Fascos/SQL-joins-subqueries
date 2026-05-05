# main.py

import sqlite3
import pandas as pd


def get_connection(db_path='data.sqlite'):
    """
    Create and return a connection to the SQLite database.
    """
    return sqlite3.connect(db_path)


def get_all_tables(conn):
    """
    Return all tables in the database.
    """
    query = "SELECT * FROM sqlite_master;"
    return pd.read_sql(query, conn)
    

def get_boston_employees(conn):
    """
    Return employees working in the Boston office.
    """
    query = """
    SELECT firstName, lastName, jobTitle
    FROM employees
    JOIN offices 
        ON employees.officeCode = offices.officeCode
    WHERE city = 'Boston'
    """
    return pd.read_sql(query, conn)


def get_empty_offices(conn):
    """
    Return offices with zero employees.
    """
    query = """
    SELECT 
        o.officeCode,
        o.city,
        COUNT(e.employeeNumber) AS num_of_employees
    FROM offices o
    LEFT JOIN employees e
        ON o.officeCode = e.officeCode
    GROUP BY o.officeCode, o.city
    HAVING COUNT(e.employeeNumber) = 0;
    """
    return pd.read_sql(query, conn)


def get_all_employees_with_location(conn):
    """
    Return all employees with their office city and state, ordered by name.
    """
    query = """
    SELECT e.firstName, e.lastName, o.city, o.state
    FROM employees AS e
    LEFT JOIN offices AS o
        ON e.officeCode = o.officeCode
    ORDER BY e.firstName, e.lastName;
    """
    return pd.read_sql(query, conn)


def get_customers_without_orders(conn):
    """
    Return customers who have never placed an order.
    """
    query = """
    SELECT c.contactFirstName, c.contactLastName, c.phone, c.salesRepEmployeeNumber
    FROM customers AS c
    LEFT JOIN orders AS o
        ON c.customerNumber = o.customerNumber
    WHERE o.customerNumber IS NULL
    ORDER BY c.contactLastName;
    """
    return pd.read_sql(query, conn)


def get_payments(conn):
    """
    Return customer payments sorted by amount descending.
    """
    query = """
    SELECT 
        c.contactFirstName,
        c.contactLastName,
        CAST(p.amount AS INTEGER) AS amount,
        p.paymentDate
    FROM customers AS c
    JOIN payments AS p
        ON c.customerNumber = p.customerNumber
    ORDER BY amount DESC;
    """
    return pd.read_sql(query, conn)


def get_high_credit_employees(conn):
    """
    Return employees with high-value customers (avg credit limit > 90000).
    """
    query = """
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
    """
    return pd.read_sql(query, conn)


def get_product_sales(conn):
    """
    Return product sales summary sorted by total units sold.
    """
    query = """
    SELECT 
        p.productName,
        COUNT(od.orderNumber) AS numorders,
        SUM(od.quantityOrdered) AS totalunits
    FROM products AS p
    JOIN orderDetails AS od
        ON p.productCode = od.productCode
    GROUP BY p.productCode
    ORDER BY totalunits DESC;
    """
    return pd.read_sql(query, conn)


def get_product_customers(conn):
    """
    Return number of unique customers per product.
    """
    query = """
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
    """
    return pd.read_sql(query, conn)


def get_product_customers(conn):
    """
    Return number of unique customers per product.
    """
    query = """
    SELECT 
        p.productName, 
        p.productCode, 
        COUNT(DISTINCT o.customerNumber) AS numpurchasers
    FROM products AS p
    JOIN orderdetails AS od
        ON p.productCode = od.productCode
    JOIN orders AS o
        ON od.orderNumber = o.orderNumber
    GROUP BY p.productCode, p.productName
    ORDER BY numpurchasers DESC;
    """
    return pd.read_sql(query, conn)


def get_low_customer_products(conn):
    """
    Return product codes with 19 or fewer unique customers.
    """
    query = """
    SELECT od.productCode
    FROM orderdetails od
    JOIN orders o
        ON od.orderNumber = o.orderNumber
    GROUP BY od.productCode
    HAVING COUNT(DISTINCT o.customerNumber) <= 19;
    """
    return pd.read_sql(query, conn)


def get_employees_under_20_custom_products(conn):
    """
    Return employees linked to products bought by 19 or fewer unique customers.
    """
    query = """
    SELECT DISTINCT
        e.employeeNumber,
        e.firstName,
        e.lastName,
        o.city,
        o.officeCode
    FROM offices AS o
    JOIN employees AS e
        ON o.officeCode = e.officeCode
    JOIN customers AS c
        ON e.employeeNumber = c.salesRepEmployeeNumber
    JOIN orders AS a 
        ON c.customerNumber = a.customerNumber
    JOIN orderdetails AS od
        ON a.orderNumber = od.orderNumber
    WHERE od.productCode IN (
        SELECT od2.productCode
        FROM orderdetails od2
        JOIN orders o2
            ON od2.orderNumber = o2.orderNumber
        GROUP BY od2.productCode
        HAVING COUNT(DISTINCT o2.customerNumber) <= 19
    );
    """
    return pd.read_sql(query, conn)