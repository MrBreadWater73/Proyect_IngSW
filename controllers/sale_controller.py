"""
Sale controller for the Clothing Store Management System.
Handles business logic for sales and transactions.
"""
from models.sale import Sale, SaleItem
from models.inventory import InventoryTransaction


class SaleController:
    """
    Controller for sale-related operations.
    """
    
    def __init__(self, db_manager, inventory_controller):
        """
        Initialize the sale controller.
        
        Args:
            db_manager: Database manager instance
            inventory_controller: Inventory controller instance for updating stock
        """
        self.db = db_manager
        self.inventory_controller = inventory_controller
        
    def create_sale(self, sale):
        """
        Create a new sale with the provided items.
        
        Args:
            sale: Sale object with items
            
        Returns:
            ID of the newly created sale
        """
        try:
            # Check if we can fulfill all items in the sale
            for item in sale.items:
                # Get current inventory
                self.db.execute(
                    'SELECT quantity FROM inventory WHERE product_variant_id = ?',
                    (item.product_variant_id,)
                )
                
                inventory_data = self.db.fetchone()
                if not inventory_data:
                    raise Exception(f"Producto no encontrado en el inventario")
                    
                current_quantity = inventory_data[0]
                if current_quantity < item.quantity:
                    # Get product info for the error message
                    self.db.execute(
                        '''
                        SELECT p.name, pv.size, pv.color 
                        FROM product_variants pv
                        JOIN products p ON pv.product_id = p.id
                        WHERE pv.id = ?
                        ''',
                        (item.product_variant_id,)
                    )
                    
                    product_info = self.db.fetchone()
                    product_name = product_info[0]
                    product_size = product_info[1]
                    product_color = product_info[2]
                    
                    raise Exception(
                        f"Stock insuficiente para {product_name} - {product_color} Talla {product_size}. "
                        f"Disponible: {current_quantity}, Solicitado: {item.quantity}"
                    )
            
            # Begin transaction
            # Insert the sale
            self.db.execute(
                '''
                INSERT INTO sales (customer_id, sale_date, payment_method, total_amount)
                VALUES (?, ?, ?, ?)
                ''',
                (sale.customer_id, sale.sale_date, sale.payment_method, sale.total_amount)
            )
            
            # Get the new sale ID
            sale_id = self.db.cursor.lastrowid
            
            # Insert sale items and update inventory
            for item in sale.items:
                item.sale_id = sale_id
                
                self.db.execute(
                    '''
                    INSERT INTO sale_items 
                    (sale_id, product_variant_id, quantity, unit_price, 
                    discount_percent, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    (item.sale_id, item.product_variant_id, item.quantity,
                     item.unit_price, item.discount_percent, item.subtotal)
                )
                
                # Update inventory
                self.db.execute(
                    'SELECT quantity FROM inventory WHERE product_variant_id = ?',
                    (item.product_variant_id,)
                )
                
                current_quantity = self.db.fetchone()[0]
                new_quantity = current_quantity - item.quantity
                
                self.db.execute(
                    '''
                    UPDATE inventory 
                    SET quantity = ?, last_updated = ?
                    WHERE product_variant_id = ?
                    ''',
                    (new_quantity, self.db.get_current_timestamp(), item.product_variant_id)
                )
                
                # Record inventory transaction
                self.db.execute(
                    '''
                    INSERT INTO inventory_transactions
                    (product_variant_id, quantity_change, transaction_type, 
                    reference_id, transaction_date, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    (item.product_variant_id, -item.quantity, InventoryTransaction.SALE,
                     sale_id, self.db.get_current_timestamp(), f"Venta #{sale_id}")
                )
            
            self.db.commit()
            return sale_id
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error creando la venta: {str(e)}")
    
    def get_sale(self, sale_id):
        """
        Get detailed information about a sale.
        
        Args:
            sale_id: ID of the sale
            
        Returns:
            Sale object with items
        """
        try:
            # Get sale information
            self.db.execute(
                '''
                SELECT s.*, c.name as customer_name
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.id
                WHERE s.id = ?
                ''',
                (sale_id,)
            )
            
            sale_data = self.db.fetchone()
            if not sale_data:
                return None
                
            sale = Sale(
                id=sale_data[0],
                customer_id=sale_data[1],
                sale_date=sale_data[2],
                payment_method=sale_data[3],
                total_amount=sale_data[4]
            )
            
            # Add customer name if available
            sale.customer_name = sale_data[5] if sale_data[5] else "Cliente no registrado"
            
            # Get sale items
            self.db.execute(
                '''
                SELECT si.*, p.name, p.code, pv.size, pv.color
                FROM sale_items si
                JOIN product_variants pv ON si.product_variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                WHERE si.sale_id = ?
                ''',
                (sale_id,)
            )
            
            items_data = self.db.fetchall()
            for item_data in items_data:
                item = SaleItem(
                    id=item_data[0],
                    sale_id=item_data[1],
                    product_variant_id=item_data[2],
                    quantity=item_data[3],
                    unit_price=item_data[4],
                    discount_percent=item_data[5],
                    subtotal=item_data[6]
                )
                
                # Add product information
                item.product_name = item_data[7]
                item.product_code = item_data[8]
                item.size = item_data[9]
                item.color = item_data[10]
                item.variant_info = f"{item.color} - Talla {item.size}"
                
                sale.items.append(item)
                
            return sale
            
        except Exception as e:
            raise Exception(f"Error getting sale: {str(e)}")
    
    def get_all_sales(self, start_date=None, end_date=None, limit=100):
        """
        Get all sales with optional date filtering.
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            limit: Maximum number of sales to return
            
        Returns:
            List of Sale objects (without items for efficiency)
        """
        try:
            query = '''
                SELECT s.*, c.name as customer_name
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.id
                WHERE 1=1
            '''
            
            params = []
            
            if start_date:
                query += " AND s.sale_date >= ?"
                params.append(start_date)
                
            if end_date:
                query += " AND s.sale_date <= ?"
                params.append(end_date)
                
            query += " ORDER BY s.sale_date DESC LIMIT ?"
            params.append(limit)
            
            self.db.execute(query, params)
            
            sales_data = self.db.fetchall()
            sales = []
            
            for sale_data in sales_data:
                sale = Sale(
                    id=sale_data[0],
                    customer_id=sale_data[1],
                    sale_date=sale_data[2],
                    payment_method=sale_data[3],
                    total_amount=sale_data[4]
                )
                
                # Add customer name if available
                sale.customer_name = sale_data[5] if sale_data[5] else "Cliente no registrado"
                
                sales.append(sale)
                
            return sales
            
        except Exception as e:
            raise Exception(f"Error getting sales: {str(e)}")
    
    def cancel_sale(self, sale_id):
        """
        Cancel a sale and restore inventory.
        
        Args:
            sale_id: ID of the sale to cancel
            
        Returns:
            True if cancelled successfully
        """
        try:
            # Check if the sale exists
            sale = self.get_sale(sale_id)
            if not sale:
                raise Exception("Venta no encontrada")
                
            # Begin transaction
            # Restore inventory for each item
            for item in sale.items:
                # Get current inventory
                self.db.execute(
                    'SELECT quantity FROM inventory WHERE product_variant_id = ?',
                    (item.product_variant_id,)
                )
                
                current_quantity = self.db.fetchone()[0]
                new_quantity = current_quantity + item.quantity
                
                # Update inventory
                self.db.execute(
                    '''
                    UPDATE inventory 
                    SET quantity = ?, last_updated = ?
                    WHERE product_variant_id = ?
                    ''',
                    (new_quantity, self.db.get_current_timestamp(), item.product_variant_id)
                )
                
                # Record inventory transaction
                self.db.execute(
                    '''
                    INSERT INTO inventory_transactions
                    (product_variant_id, quantity_change, transaction_type, 
                    reference_id, transaction_date, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    (item.product_variant_id, item.quantity, InventoryTransaction.RETURN,
                     sale_id, self.db.get_current_timestamp(), f"Cancelación de venta #{sale_id}")
                )
            
            # Delete sale items
            self.db.execute('DELETE FROM sale_items WHERE sale_id = ?', (sale_id,))
            
            # Delete the sale
            self.db.execute('DELETE FROM sales WHERE id = ?', (sale_id,))
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error cancelling sale: {str(e)}")
    
    def get_sales_by_payment_method(self, start_date=None, end_date=None):
        """
        Get sales statistics grouped by payment method.
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            Dictionary with payment methods as keys and total amounts as values
        """
        try:
            query = '''
                SELECT payment_method, COUNT(*) as count, SUM(total_amount) as total
                FROM sales
                WHERE 1=1
            '''
            
            params = []
            
            if start_date:
                query += " AND sale_date >= ?"
                params.append(start_date)
                
            if end_date:
                query += " AND sale_date <= ?"
                params.append(end_date)
                
            query += " GROUP BY payment_method ORDER BY total DESC"
            
            self.db.execute(query, params)
            
            results_data = self.db.fetchall()
            results = {}
            
            for data in results_data:
                method = data[0]
                count = data[1]
                total = data[2]
                
                results[method] = {
                    'count': count,
                    'total': total
                }
                
            return results
            
        except Exception as e:
            raise Exception(f"Error getting sales by payment method: {str(e)}")
    
    def get_top_selling_products(self, limit=10, start_date=None, end_date=None):
        """
        Get the top selling products by quantity.
        
        Args:
            limit: Maximum number of products to return
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of dictionaries with product and sales information
        """
        try:
            query = '''
                SELECT p.id, p.code, p.name, c.name as category, 
                       SUM(si.quantity) as total_quantity, 
                       SUM(si.subtotal) as total_amount,
                       COUNT(DISTINCT s.id) as sale_count
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                JOIN product_variants pv ON si.product_variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                JOIN categories c ON p.category_id = c.id
                WHERE 1=1
            '''
            
            params = []
            
            if start_date:
                query += " AND s.sale_date >= ?"
                params.append(start_date)
                
            if end_date:
                query += " AND s.sale_date <= ?"
                params.append(end_date)
                
            query += " GROUP BY p.id ORDER BY total_quantity DESC LIMIT ?"
            params.append(limit)
            
            self.db.execute(query, params)
            
            results_data = self.db.fetchall()
            results = []
            
            for data in results_data:
                product = {
                    'id': data[0],
                    'code': data[1],
                    'name': data[2],
                    'category': data[3],
                    'total_quantity': data[4],
                    'total_amount': data[5],
                    'sale_count': data[6]
                }
                
                results.append(product)
                
            return results
            
        except Exception as e:
            raise Exception(f"Error getting top selling products: {str(e)}")
