"""
Database manager for the Clothing Store Management System.
Handles database connection, setup, and provides methods for database operations.
"""
import os
import sqlite3
from datetime import datetime


class DatabaseManager:
    """
    Manages SQLite database operations for the application.
    """
    
    def __init__(self, db_name):
        """
        Initialize the database manager with the specified database name.
        
        Args:
            db_name: Name of the SQLite database file
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        
    def connect(self):
        """
        Establish a connection to the SQLite database.
        """
        try:
            self.conn = sqlite3.connect(self.db_name)
            # Enable foreign key support
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            raise Exception(f"Error connecting to database: {str(e)}")
    
    def close(self):
        """
        Close the database connection.
        """
        if self.conn:
            self.conn.close()
            
    def commit(self):
        """
        Commit current transaction.
        """
        if self.conn:
            self.conn.commit()
            
    def execute(self, query, params=None):
        """
        Execute a SQL query with optional parameters.
        
        Args:
            query: SQL query string
            params: Parameters for the query (optional)
            
        Returns:
            Cursor object for the executed query
        """
        try:
            if params:
                return self.cursor.execute(query, params)
            else:
                return self.cursor.execute(query)
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Error executing query: {str(e)}")
            
    def fetchall(self):
        """
        Fetch all rows from the last executed query.
        
        Returns:
            List of rows
        """
        return self.cursor.fetchall()
    
    def fetchone(self):
        """
        Fetch one row from the last executed query.
        
        Returns:
            Single row or None
        """
        return self.cursor.fetchone()
    
    def setup_database(self):
        """
        Create database tables if they don't exist.
        """
        # Products table
        self.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
        ''')
        
        # Products table
        self.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            category_id INTEGER NOT NULL,
            price REAL NOT NULL,
            discount_percent REAL DEFAULT 0,
            discount_start_date TEXT,
            discount_end_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
        ''')
        
        # Product variants (sizes, colors)
        self.execute('''
        CREATE TABLE IF NOT EXISTS product_variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            size TEXT NOT NULL,
            color TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            UNIQUE(product_id, size, color)
        )
        ''')
        
        # Inventory table
        self.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_variant_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            last_updated TEXT NOT NULL,
            FOREIGN KEY (product_variant_id) REFERENCES product_variants(id) ON DELETE CASCADE
        )
        ''')
        
        # Customers table
        self.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            address TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        # Suppliers table
        self.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_person TEXT,
            email TEXT,
            phone TEXT NOT NULL,
            address TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        # Supplier products table
        self.execute('''
        CREATE TABLE IF NOT EXISTS supplier_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            UNIQUE(supplier_id, product_id)
        )
        ''')
        
        # Sales table
        self.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            sale_date TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            total_amount REAL NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
        )
        ''')
        
        # Sale items table
        self.execute('''
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_variant_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            discount_percent REAL DEFAULT 0,
            subtotal REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
            FOREIGN KEY (product_variant_id) REFERENCES product_variants(id) ON DELETE RESTRICT
        )
        ''')
        
        # Inventory transactions table
        self.execute('''
        CREATE TABLE IF NOT EXISTS inventory_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_variant_id INTEGER NOT NULL,
            quantity_change INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            reference_id INTEGER,
            transaction_date TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (product_variant_id) REFERENCES product_variants(id) ON DELETE RESTRICT
        )
        ''')
        
        # Insert default categories if they don't exist
        default_categories = [
            ('Camisetas', 'Todo tipo de camisetas'),
            ('Pantalones', 'Pantalones para hombre y mujer'),
            ('Accesorios', 'Complementos de moda'),
            ('Vestidos', 'Vestidos para mujer'),
            ('Chaquetas', 'Chaquetas y abrigos')
        ]
        
        for category in default_categories:
            self.execute(
                'INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)',
                category
            )
            
        self.commit()
        
    def get_current_timestamp(self):
        """
        Get the current timestamp in ISO format.
        
        Returns:
            String with current timestamp
        """
        return datetime.now().isoformat()
