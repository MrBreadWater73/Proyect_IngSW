"""
Customer controller for the Clothing Store Management System.
Handles business logic for customer management.
"""
from models.customer import Customer


class CustomerController:
    """
    Controller for customer-related operations.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the customer controller.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        
    def add_customer(self, customer):
        """
        Add a new customer to the database.
        
        Args:
            customer: Customer object
            
        Returns:
            ID of the newly created customer
        """
        try:
            # Check if email already exists (if provided)
            if customer.email:
                self.db.execute(
                    'SELECT id FROM customers WHERE email = ?',
                    (customer.email,)
                )
                existing = self.db.fetchone()
                if existing:
                    raise Exception("Ya existe un cliente con este correo electrónico")
            
            current_time = self.db.get_current_timestamp()
            
            self.db.execute(
                '''
                INSERT INTO customers 
                (name, email, phone, address, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (customer.name, customer.email, customer.phone, 
                 customer.address, current_time, current_time)
            )
            
            customer_id = self.db.cursor.lastrowid
            self.db.commit()
            return customer_id
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error adding customer: {str(e)}")
    
    def update_customer(self, customer):
        """
        Update an existing customer.
        
        Args:
            customer: Customer object with updated information
            
        Returns:
            True if updated successfully
        """
        try:
            # Check if email is already used by another customer
            if customer.email:
                self.db.execute(
                    'SELECT id FROM customers WHERE email = ? AND id != ?',
                    (customer.email, customer.id)
                )
                existing = self.db.fetchone()
                if existing:
                    raise Exception("Ya existe otro cliente con este correo electrónico")
            
            current_time = self.db.get_current_timestamp()
            
            self.db.execute(
                '''
                UPDATE customers
                SET name = ?, email = ?, phone = ?, address = ?, updated_at = ?
                WHERE id = ?
                ''',
                (customer.name, customer.email, customer.phone, 
                 customer.address, current_time, customer.id)
            )
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error updating customer: {str(e)}")
    
    def delete_customer(self, customer_id):
        """
        Delete a customer if they don't have associated sales.
        
        Args:
            customer_id: ID of the customer to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            # Check if customer has sales
            self.db.execute(
                'SELECT COUNT(*) FROM sales WHERE customer_id = ?',
                (customer_id,)
            )
            
            count = self.db.fetchone()[0]
            if count > 0:
                # Set customer_id to NULL in sales rather than preventing deletion
                self.db.execute(
                    'UPDATE sales SET customer_id = NULL WHERE customer_id = ?',
                    (customer_id,)
                )
                
            # Delete the customer
            self.db.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error deleting customer: {str(e)}")
    
    def get_customer(self, customer_id):
        """
        Get a customer by ID.
        
        Args:
            customer_id: ID of the customer
            
        Returns:
            Customer object
        """
        try:
            self.db.execute(
                'SELECT * FROM customers WHERE id = ?',
                (customer_id,)
            )
            
            customer_data = self.db.fetchone()
            if not customer_data:
                return None
                
            customer = Customer(
                id=customer_data[0],
                name=customer_data[1],
                email=customer_data[2],
                phone=customer_data[3],
                address=customer_data[4],
                created_at=customer_data[5],
                updated_at=customer_data[6]
            )
            
            # Load purchase history
            self.db.execute(
                '''
                SELECT s.id, s.sale_date, s.payment_method, s.total_amount
                FROM sales s
                WHERE s.customer_id = ?
                ORDER BY s.sale_date DESC
                ''',
                (customer_id,)
            )
            
            sales_data = self.db.fetchall()
            for sale_data in sales_data:
                sale = {
                    'id': sale_data[0],
                    'sale_date': sale_data[1],
                    'payment_method': sale_data[2],
                    'total_amount': sale_data[3]
                }
                customer.purchase_history.append(sale)
                
            return customer
            
        except Exception as e:
            raise Exception(f"Error getting customer: {str(e)}")
    
    def get_all_customers(self):
        """
        Get all customers.
        
        Returns:
            List of Customer objects
        """
        try:
            self.db.execute('SELECT * FROM customers ORDER BY name')
            customers_data = self.db.fetchall()
            
            customers = []
            for customer_data in customers_data:
                customer = Customer(
                    id=customer_data[0],
                    name=customer_data[1],
                    email=customer_data[2],
                    phone=customer_data[3],
                    address=customer_data[4],
                    created_at=customer_data[5],
                    updated_at=customer_data[6]
                )
                customers.append(customer)
                
            return customers
            
        except Exception as e:
            raise Exception(f"Error getting customers: {str(e)}")
    
    def search_customers(self, search_term):
        """
        Search for customers by name, email, or phone.
        
        Args:
            search_term: Search query
            
        Returns:
            List of matching Customer objects
        """
        try:
            search_pattern = f"%{search_term}%"
            
            self.db.execute(
                '''
                SELECT * FROM customers 
                WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?
                ORDER BY name
                ''',
                (search_pattern, search_pattern, search_pattern)
            )
            
            customers_data = self.db.fetchall()
            
            customers = []
            for customer_data in customers_data:
                customer = Customer(
                    id=customer_data[0],
                    name=customer_data[1],
                    email=customer_data[2],
                    phone=customer_data[3],
                    address=customer_data[4],
                    created_at=customer_data[5],
                    updated_at=customer_data[6]
                )
                customers.append(customer)
                
            return customers
            
        except Exception as e:
            raise Exception(f"Error searching customers: {str(e)}")
    
    def get_customer_purchase_history(self, customer_id):
        """
        Get detailed purchase history for a customer.
        
        Args:
            customer_id: ID of the customer
            
        Returns:
            List of dictionaries with sale information and items
        """
        try:
            # Get sales for the customer
            self.db.execute(
                '''
                SELECT s.id, s.sale_date, s.payment_method, s.total_amount
                FROM sales s
                WHERE s.customer_id = ?
                ORDER BY s.sale_date DESC
                ''',
                (customer_id,)
            )
            
            sales_data = self.db.fetchall()
            purchase_history = []
            
            for sale_data in sales_data:
                sale = {
                    'id': sale_data[0],
                    'sale_date': sale_data[1],
                    'payment_method': sale_data[2],
                    'total_amount': sale_data[3],
                    'items': []
                }
                
                # Get items for this sale
                self.db.execute(
                    '''
                    SELECT si.id, si.quantity, si.unit_price, si.discount_percent, si.subtotal,
                           p.name, p.code, pv.size, pv.color
                    FROM sale_items si
                    JOIN product_variants pv ON si.product_variant_id = pv.id
                    JOIN products p ON pv.product_id = p.id
                    WHERE si.sale_id = ?
                    ''',
                    (sale['id'],)
                )
                
                items_data = self.db.fetchall()
                for item_data in items_data:
                    item = {
                        'id': item_data[0],
                        'quantity': item_data[1],
                        'unit_price': item_data[2],
                        'discount_percent': item_data[3],
                        'subtotal': item_data[4],
                        'product_name': item_data[5],
                        'product_code': item_data[6],
                        'size': item_data[7],
                        'color': item_data[8]
                    }
                    sale['items'].append(item)
                
                purchase_history.append(sale)
                
            return purchase_history
            
        except Exception as e:
            raise Exception(f"Error getting customer purchase history: {str(e)}")
