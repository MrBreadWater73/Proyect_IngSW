"""
Supplier controller for the Clothing Store Management System.
Handles business logic for supplier management.
"""
from models.supplier import Supplier


class SupplierController:
    """
    Controller for supplier-related operations.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the supplier controller.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        
    def add_supplier(self, supplier):
        """
        Add a new supplier to the database.
        
        Args:
            supplier: Supplier object
            
        Returns:
            ID of the newly created supplier
        """
        try:
            current_time = self.db.get_current_timestamp()
            
            # Insert supplier
            self.db.execute(
                '''
                INSERT INTO suppliers 
                (name, contact_person, email, phone, address, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''',
                (supplier.name, supplier.contact_person, supplier.email, 
                 supplier.phone, supplier.address, current_time, current_time)
            )
            
            supplier_id = self.db.cursor.lastrowid
            
            # Add supplier products if any
            if supplier.products:
                for product_id in supplier.products:
                    self.db.execute(
                        '''
                        INSERT INTO supplier_products (supplier_id, product_id)
                        VALUES (?, ?)
                        ''',
                        (supplier_id, product_id)
                    )
            
            self.db.commit()
            return supplier_id
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error adding supplier: {str(e)}")
    
    def update_supplier(self, supplier):
        """
        Update an existing supplier.
        
        Args:
            supplier: Supplier object with updated information
            
        Returns:
            True if updated successfully
        """
        try:
            current_time = self.db.get_current_timestamp()
            
            # Update supplier information
            self.db.execute(
                '''
                UPDATE suppliers
                SET name = ?, contact_person = ?, email = ?, 
                    phone = ?, address = ?, updated_at = ?
                WHERE id = ?
                ''',
                (supplier.name, supplier.contact_person, supplier.email,
                 supplier.phone, supplier.address, current_time, supplier.id)
            )
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error updating supplier: {str(e)}")
    
    def delete_supplier(self, supplier_id):
        """
        Delete a supplier if they don't have associated products.
        
        Args:
            supplier_id: ID of the supplier to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            # Delete supplier products first (cascade will handle this automatically)
            self.db.execute('DELETE FROM suppliers WHERE id = ?', (supplier_id,))
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error deleting supplier: {str(e)}")
    
    def get_supplier(self, supplier_id):
        """
        Get a supplier by ID.
        
        Args:
            supplier_id: ID of the supplier
            
        Returns:
            Supplier object with product information
        """
        try:
            # Get supplier details
            self.db.execute(
                'SELECT * FROM suppliers WHERE id = ?',
                (supplier_id,)
            )
            
            supplier_data = self.db.fetchone()
            if not supplier_data:
                return None
                
            supplier = Supplier(
                id=supplier_data[0],
                name=supplier_data[1],
                contact_person=supplier_data[2],
                email=supplier_data[3],
                phone=supplier_data[4],
                address=supplier_data[5],
                created_at=supplier_data[6],
                updated_at=supplier_data[7]
            )
            
            # Get supplier products
            self.db.execute(
                'SELECT product_id FROM supplier_products WHERE supplier_id = ?',
                (supplier_id,)
            )
            
            products_data = self.db.fetchall()
            for product_data in products_data:
                supplier.products.append(product_data[0])
                
            return supplier
            
        except Exception as e:
            raise Exception(f"Error getting supplier: {str(e)}")
    
    def get_all_suppliers(self):
        """
        Get all suppliers.
        
        Returns:
            List of Supplier objects
        """
        try:
            self.db.execute('SELECT * FROM suppliers ORDER BY name')
            suppliers_data = self.db.fetchall()
            
            suppliers = []
            for supplier_data in suppliers_data:
                supplier = Supplier(
                    id=supplier_data[0],
                    name=supplier_data[1],
                    contact_person=supplier_data[2],
                    email=supplier_data[3],
                    phone=supplier_data[4],
                    address=supplier_data[5],
                    created_at=supplier_data[6],
                    updated_at=supplier_data[7]
                )
                suppliers.append(supplier)
                
            return suppliers
            
        except Exception as e:
            raise Exception(f"Error getting suppliers: {str(e)}")
    
    def search_suppliers(self, search_term):
        """
        Search for suppliers by name, contact person, email, or phone.
        
        Args:
            search_term: Search query
            
        Returns:
            List of matching Supplier objects
        """
        try:
            search_pattern = f"%{search_term}%"
            
            self.db.execute(
                '''
                SELECT * FROM suppliers 
                WHERE name LIKE ? OR contact_person LIKE ? OR email LIKE ? OR phone LIKE ?
                ORDER BY name
                ''',
                (search_pattern, search_pattern, search_pattern, search_pattern)
            )
            
            suppliers_data = self.db.fetchall()
            
            suppliers = []
            for supplier_data in suppliers_data:
                supplier = Supplier(
                    id=supplier_data[0],
                    name=supplier_data[1],
                    contact_person=supplier_data[2],
                    email=supplier_data[3],
                    phone=supplier_data[4],
                    address=supplier_data[5],
                    created_at=supplier_data[6],
                    updated_at=supplier_data[7]
                )
                suppliers.append(supplier)
                
            return suppliers
            
        except Exception as e:
            raise Exception(f"Error searching suppliers: {str(e)}")
    
    def add_product_to_supplier(self, supplier_id, product_id):
        """
        Add a product to a supplier's offerings.
        
        Args:
            supplier_id: ID of the supplier
            product_id: ID of the product
            
        Returns:
            True if added successfully
        """
        try:
            # Check if the relationship already exists
            self.db.execute(
                '''
                SELECT 1 FROM supplier_products 
                WHERE supplier_id = ? AND product_id = ?
                ''',
                (supplier_id, product_id)
            )
            
            if self.db.fetchone():
                raise Exception("Este producto ya está asociado con este proveedor")
                
            # Add the relationship
            self.db.execute(
                '''
                INSERT INTO supplier_products (supplier_id, product_id)
                VALUES (?, ?)
                ''',
                (supplier_id, product_id)
            )
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error adding product to supplier: {str(e)}")
    
    def remove_product_from_supplier(self, supplier_id, product_id):
        """
        Remove a product from a supplier's offerings.
        
        Args:
            supplier_id: ID of the supplier
            product_id: ID of the product
            
        Returns:
            True if removed successfully
        """
        try:
            self.db.execute(
                '''
                DELETE FROM supplier_products 
                WHERE supplier_id = ? AND product_id = ?
                ''',
                (supplier_id, product_id)
            )
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error removing product from supplier: {str(e)}")
    
    def get_supplier_products(self, supplier_id):
        """
        Get all products offered by a supplier.
        
        Args:
            supplier_id: ID of the supplier
            
        Returns:
            List of dictionaries with product information
        """
        try:
            self.db.execute(
                '''
                SELECT p.id, p.code, p.name, p.description, c.name as category, p.price
                FROM supplier_products sp
                JOIN products p ON sp.product_id = p.id
                JOIN categories c ON p.category_id = c.id
                WHERE sp.supplier_id = ?
                ORDER BY p.name
                ''',
                (supplier_id,)
            )
            
            products_data = self.db.fetchall()
            
            products = []
            for product_data in products_data:
                product = {
                    'id': product_data[0],
                    'code': product_data[1],
                    'name': product_data[2],
                    'description': product_data[3],
                    'category': product_data[4],
                    'price': product_data[5]
                }
                products.append(product)
                
            return products
            
        except Exception as e:
            raise Exception(f"Error getting supplier products: {str(e)}")
    
    def get_suppliers_for_product(self, product_id):
        """
        Get all suppliers that offer a specific product.
        
        Args:
            product_id: ID of the product
            
        Returns:
            List of dictionaries with supplier information
        """
        try:
            self.db.execute(
                '''
                SELECT s.id, s.name, s.contact_person, s.phone, s.email
                FROM supplier_products sp
                JOIN suppliers s ON sp.supplier_id = s.id
                WHERE sp.product_id = ?
                ORDER BY s.name
                ''',
                (product_id,)
            )
            
            suppliers_data = self.db.fetchall()
            
            suppliers = []
            for supplier_data in suppliers_data:
                supplier = {
                    'id': supplier_data[0],
                    'name': supplier_data[1],
                    'contact_person': supplier_data[2],
                    'phone': supplier_data[3],
                    'email': supplier_data[4]
                }
                suppliers.append(supplier)
                
            return suppliers
            
        except Exception as e:
            raise Exception(f"Error getting suppliers for product: {str(e)}")
