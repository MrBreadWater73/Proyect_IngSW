"""
Inventory controller for the Clothing Store Management System.
Handles business logic for inventory management.
"""
from models.inventory import Inventory, InventoryTransaction


class InventoryController:
    """
    Controller for inventory-related operations.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the inventory controller.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        
    def get_inventory(self, product_variant_id):
        """
        Get inventory information for a specific product variant.
        
        Args:
            product_variant_id: ID of the product variant
            
        Returns:
            Inventory object
        """
        try:
            self.db.execute(
                'SELECT * FROM inventory WHERE product_variant_id = ?',
                (product_variant_id,)
            )
            
            inventory_data = self.db.fetchone()
            if not inventory_data:
                return None
                
            inventory = Inventory(
                id=inventory_data[0],
                product_variant_id=inventory_data[1],
                quantity=inventory_data[2],
                last_updated=inventory_data[3]
            )
            
            return inventory
            
        except Exception as e:
            raise Exception(f"Error getting inventory: {str(e)}")
    
    def update_inventory(self, product_variant_id, new_quantity, transaction_type,
                         reference_id=None, notes=None):
        """
        Update inventory quantity and record the transaction.
        
        Args:
            product_variant_id: ID of the product variant
            new_quantity: New quantity to set
            transaction_type: Type of transaction (SALE, PURCHASE, ADJUSTMENT, RETURN)
            reference_id: Reference ID for the transaction (e.g., sale ID)
            notes: Additional notes
            
        Returns:
            True if updated successfully
        """
        try:
            # Get current quantity
            current_inventory = self.get_inventory(product_variant_id)
            if not current_inventory:
                raise Exception("Inventario no encontrado para la variante de producto especificada")
                
            current_quantity = current_inventory.quantity
            quantity_change = new_quantity - current_quantity
            
            # Begin transaction
            current_time = self.db.get_current_timestamp()
            
            # Update inventory
            self.db.execute(
                '''
                UPDATE inventory 
                SET quantity = ?, last_updated = ?
                WHERE product_variant_id = ?
                ''',
                (new_quantity, current_time, product_variant_id)
            )
            
            # Record transaction
            self.db.execute(
                '''
                INSERT INTO inventory_transactions
                (product_variant_id, quantity_change, transaction_type, reference_id, 
                transaction_date, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (product_variant_id, quantity_change, transaction_type, 
                 reference_id, current_time, notes)
            )
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error updating inventory: {str(e)}")
    
    def adjust_inventory(self, product_variant_id, quantity_change, notes=None):
        """
        Adjust inventory by adding or subtracting a quantity.
        
        Args:
            product_variant_id: ID of the product variant
            quantity_change: Amount to add (positive) or subtract (negative)
            notes: Additional notes
            
        Returns:
            True if adjusted successfully
        """
        try:
            # Get current quantity
            current_inventory = self.get_inventory(product_variant_id)
            if not current_inventory:
                raise Exception("Inventario no encontrado para la variante de producto especificada")
                
            new_quantity = current_inventory.quantity + quantity_change
            if new_quantity < 0:
                raise Exception("La cantidad de inventario no puede ser negativa")
                
            # Update inventory with the adjustment
            return self.update_inventory(
                product_variant_id, 
                new_quantity,
                InventoryTransaction.ADJUSTMENT,
                notes=notes
            )
            
        except Exception as e:
            raise Exception(f"Error adjusting inventory: {str(e)}")
    
    def get_low_stock_items(self, threshold=5):
        """
        Get all product variants with low stock.
        
        Args:
            threshold: Quantity threshold for low stock
            
        Returns:
            List of tuples with product and inventory information
        """
        try:
            self.db.execute(
                '''
                SELECT p.id, p.code, p.name, pv.id, pv.size, pv.color, i.quantity
                FROM inventory i
                JOIN product_variants pv ON i.product_variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                WHERE i.quantity > 0 AND i.quantity <= ?
                ORDER BY i.quantity, p.name
                ''',
                (threshold,)
            )
            
            low_stock_data = self.db.fetchall()
            return low_stock_data
            
        except Exception as e:
            raise Exception(f"Error getting low stock items: {str(e)}")
    
    def get_out_of_stock_items(self):
        """
        Get all product variants that are out of stock.
        
        Returns:
            List of tuples with product and inventory information
        """
        try:
            self.db.execute(
                '''
                SELECT p.id, p.code, p.name, pv.id, pv.size, pv.color, i.quantity
                FROM inventory i
                JOIN product_variants pv ON i.product_variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                WHERE i.quantity = 0
                ORDER BY p.name
                '''
            )
            
            out_of_stock_data = self.db.fetchall()
            return out_of_stock_data
            
        except Exception as e:
            raise Exception(f"Error getting out of stock items: {str(e)}")
    
    def get_stock_by_category(self):
        """
        Get total stock and item count by category.
        
        Returns:
            List of tuples with category name, total items, and total stock
        """
        try:
            self.db.execute(
                '''
                SELECT c.name, COUNT(DISTINCT p.id), SUM(i.quantity)
                FROM categories c
                JOIN products p ON c.id = p.category_id
                JOIN product_variants pv ON p.id = pv.product_id
                JOIN inventory i ON pv.id = i.product_variant_id
                GROUP BY c.id
                ORDER BY c.name
                '''
            )
            
            stock_data = self.db.fetchall()
            return stock_data
            
        except Exception as e:
            raise Exception(f"Error getting stock by category: {str(e)}")
    
    def get_inventory_transactions(self, product_variant_id=None, transaction_type=None, 
                                  start_date=None, end_date=None, limit=100):
        """
        Get inventory transaction history with optional filters.
        
        Args:
            product_variant_id: Optional ID to filter by specific variant
            transaction_type: Optional type to filter by transaction type
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            limit: Maximum number of transactions to return
            
        Returns:
            List of InventoryTransaction objects
        """
        try:
            query = '''
                SELECT it.*, p.name, pv.size, pv.color
                FROM inventory_transactions it
                JOIN product_variants pv ON it.product_variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                WHERE 1=1
            '''
            
            params = []
            
            if product_variant_id:
                query += " AND it.product_variant_id = ?"
                params.append(product_variant_id)
                
            if transaction_type:
                query += " AND it.transaction_type = ?"
                params.append(transaction_type)
                
            if start_date:
                query += " AND it.transaction_date >= ?"
                params.append(start_date)
                
            if end_date:
                query += " AND it.transaction_date <= ?"
                params.append(end_date)
                
            query += " ORDER BY it.transaction_date DESC LIMIT ?"
            params.append(limit)
            
            self.db.execute(query, params)
            
            transactions_data = self.db.fetchall()
            transactions = []
            
            for tx_data in transactions_data:
                transaction = InventoryTransaction(
                    id=tx_data[0],
                    product_variant_id=tx_data[1],
                    quantity_change=tx_data[2],
                    transaction_type=tx_data[3],
                    reference_id=tx_data[4],
                    transaction_date=tx_data[5],
                    notes=tx_data[6]
                )
                
                # Add additional context data
                transaction.product_name = tx_data[7]
                transaction.size = tx_data[8]
                transaction.color = tx_data[9]
                
                transactions.append(transaction)
                
            return transactions
            
        except Exception as e:
            raise Exception(f"Error getting inventory transactions: {str(e)}")
