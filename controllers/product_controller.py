"""
Product controller for the Clothing Store Management System.
Handles business logic for products and categories.
"""
from datetime import datetime
from models.product import Product, ProductVariant, Category


class ProductController:
    """
    Controller for product-related operations.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the product controller.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        
    def add_product(self, product, variants):
        """
        Add a new product with its variants to the database.
        
        Args:
            product: Product object
            variants: List of ProductVariant objects
            
        Returns:
            ID of the newly created product
        """
        try:
            current_time = self.db.get_current_timestamp()
            
            # Insert product
            self.db.execute(
                '''
                INSERT INTO products 
                (code, name, description, category_id, price, discount_percent, 
                discount_start_date, discount_end_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (product.code, product.name, product.description, product.category_id,
                 product.price, product.discount_percent, product.discount_start_date,
                 product.discount_end_date, current_time, current_time)
            )
            
            # Get the ID of the new product
            product_id = self.db.cursor.lastrowid
            
            # Insert each variant
            for variant in variants:
                variant.product_id = product_id
                self.db.execute(
                    '''
                    INSERT INTO product_variants (product_id, size, color)
                    VALUES (?, ?, ?)
                    ''',
                    (product_id, variant.size, variant.color)
                )
                
                # Get the variant ID
                variant_id = self.db.cursor.lastrowid
                
                # Initialize inventory record for this variant
                self.db.execute(
                    '''
                    INSERT INTO inventory (product_variant_id, quantity, last_updated)
                    VALUES (?, ?, ?)
                    ''',
                    (variant_id, 0, current_time)
                )
            
            self.db.commit()
            return product_id
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error adding product: {str(e)}")
    
    def update_product(self, product):
        """
        Update an existing product.
        
        Args:
            product: Product object with updated information
            
        Returns:
            True if updated successfully
        """
        try:
            current_time = self.db.get_current_timestamp()
            
            self.db.execute(
                '''
                UPDATE products
                SET code = ?, name = ?, description = ?, category_id = ?,
                    price = ?, discount_percent = ?, discount_start_date = ?,
                    discount_end_date = ?, updated_at = ?
                WHERE id = ?
                ''',
                (product.code, product.name, product.description, product.category_id,
                 product.price, product.discount_percent, product.discount_start_date,
                 product.discount_end_date, current_time, product.id)
            )
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error updating product: {str(e)}")
    
    def delete_product(self, product_id):
        """
        Delete a product and all its variants.
        
        Args:
            product_id: ID of the product to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            # Check if the product is used in any sales
            self.db.execute(
                '''
                SELECT COUNT(*) FROM sale_items
                JOIN product_variants ON sale_items.product_variant_id = product_variants.id
                WHERE product_variants.product_id = ?
                ''',
                (product_id,)
            )
            
            count = self.db.fetchone()[0]
            if count > 0:
                raise Exception("No se puede eliminar el producto porque está asociado a ventas existentes")
                
            # Delete product (cascades to variants, which cascades to inventory)
            self.db.execute('DELETE FROM products WHERE id = ?', (product_id,))
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error deleting product: {str(e)}")
    
    def get_product(self, product_id):
        """
        Get a product by ID.
        
        Args:
            product_id: ID of the product
            
        Returns:
            Product object with variants
        """
        try:
            # Get product details
            self.db.execute(
                'SELECT * FROM products WHERE id = ?',
                (product_id,)
            )
            
            product_data = self.db.fetchone()
            if not product_data:
                return None
                
            # Create product object
            id_idx, code_idx, name_idx, desc_idx, cat_idx, price_idx = 0, 1, 2, 3, 4, 5
            disc_pct_idx, disc_start_idx, disc_end_idx, created_idx, updated_idx = 6, 7, 8, 9, 10
            
            product = Product(
                id=product_data[id_idx],
                code=product_data[code_idx],
                name=product_data[name_idx],
                description=product_data[desc_idx],
                category_id=product_data[cat_idx],
                price=product_data[price_idx],
                discount_percent=product_data[disc_pct_idx],
                discount_start_date=product_data[disc_start_idx],
                discount_end_date=product_data[disc_end_idx],
                created_at=product_data[created_idx],
                updated_at=product_data[updated_idx]
            )
            
            # Get variants with inventory
            self.db.execute(
                '''
                SELECT pv.id, pv.product_id, pv.size, pv.color, i.quantity
                FROM product_variants pv
                LEFT JOIN inventory i ON pv.id = i.product_variant_id
                WHERE pv.product_id = ?
                ''',
                (product_id,)
            )
            
            variants_data = self.db.fetchall()
            for variant_data in variants_data:
                variant = ProductVariant(
                    id=variant_data[0],
                    product_id=variant_data[1],
                    size=variant_data[2],
                    color=variant_data[3]
                )
                variant.inventory_quantity = variant_data[4]
                product.variants.append(variant)
                
            return product
            
        except Exception as e:
            raise Exception(f"Error getting product: {str(e)}")
    
    def get_all_products(self, category_id=None, include_variants=False):
        """
        Get all products, optionally filtered by category.
        
        Args:
            category_id: Optional category ID to filter by
            include_variants: Whether to include variant information
            
        Returns:
            List of Product objects
        """
        try:
            if category_id:
                self.db.execute(
                    'SELECT * FROM products WHERE category_id = ? ORDER BY name',
                    (category_id,)
                )
            else:
                self.db.execute('SELECT * FROM products ORDER BY name')
                
            products_data = self.db.fetchall()
            products = []
            
            for product_data in products_data:
                id_idx, code_idx, name_idx, desc_idx, cat_idx, price_idx = 0, 1, 2, 3, 4, 5
                disc_pct_idx, disc_start_idx, disc_end_idx, created_idx, updated_idx = 6, 7, 8, 9, 10
                
                product = Product(
                    id=product_data[id_idx],
                    code=product_data[code_idx],
                    name=product_data[name_idx],
                    description=product_data[desc_idx],
                    category_id=product_data[cat_idx],
                    price=product_data[price_idx],
                    discount_percent=product_data[disc_pct_idx],
                    discount_start_date=product_data[disc_start_idx],
                    discount_end_date=product_data[disc_end_idx],
                    created_at=product_data[created_idx],
                    updated_at=product_data[updated_idx]
                )
                
                if include_variants:
                    # Get variants with inventory
                    self.db.execute(
                        '''
                        SELECT pv.id, pv.product_id, pv.size, pv.color, i.quantity
                        FROM product_variants pv
                        LEFT JOIN inventory i ON pv.id = i.product_variant_id
                        WHERE pv.product_id = ?
                        ''',
                        (product.id,)
                    )
                    
                    variants_data = self.db.fetchall()
                    for variant_data in variants_data:
                        variant = ProductVariant(
                            id=variant_data[0],
                            product_id=variant_data[1],
                            size=variant_data[2],
                            color=variant_data[3]
                        )
                        variant.inventory_quantity = variant_data[4]
                        product.variants.append(variant)
                
                products.append(product)
                
            return products
            
        except Exception as e:
            raise Exception(f"Error getting products: {str(e)}")
    
    def get_product_variants(self, product_id):
        """
        Get all variants for a product.
        
        Args:
            product_id: ID of the product
            
        Returns:
            List of ProductVariant objects with inventory information
        """
        try:
            self.db.execute(
                '''
                SELECT pv.id, pv.product_id, pv.size, pv.color, i.quantity
                FROM product_variants pv
                LEFT JOIN inventory i ON pv.id = i.product_variant_id
                WHERE pv.product_id = ?
                ''',
                (product_id,)
            )
            
            variants_data = self.db.fetchall()
            variants = []
            
            for variant_data in variants_data:
                variant = ProductVariant(
                    id=variant_data[0],
                    product_id=variant_data[1],
                    size=variant_data[2],
                    color=variant_data[3]
                )
                variant.inventory_quantity = variant_data[4]
                variants.append(variant)
                
            return variants
            
        except Exception as e:
            raise Exception(f"Error getting product variants: {str(e)}")
    
    def add_variant(self, variant):
        """
        Add a new variant to a product.
        
        Args:
            variant: ProductVariant object
            
        Returns:
            ID of the newly created variant
        """
        try:
            current_time = self.db.get_current_timestamp()
            
            # Check if variant already exists
            self.db.execute(
                '''
                SELECT id FROM product_variants 
                WHERE product_id = ? AND size = ? AND color = ?
                ''',
                (variant.product_id, variant.size, variant.color)
            )
            
            existing = self.db.fetchone()
            if existing:
                raise Exception("Ya existe una variante con esta talla y color para este producto")
                
            # Insert the variant
            self.db.execute(
                '''
                INSERT INTO product_variants (product_id, size, color)
                VALUES (?, ?, ?)
                ''',
                (variant.product_id, variant.size, variant.color)
            )
            
            variant_id = self.db.cursor.lastrowid
            
            # Initialize inventory for this variant
            self.db.execute(
                '''
                INSERT INTO inventory (product_variant_id, quantity, last_updated)
                VALUES (?, ?, ?)
                ''',
                (variant_id, variant.inventory_quantity, current_time)
            )
            
            self.db.commit()
            return variant_id
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error adding variant: {str(e)}")
    
    def update_variant(self, variant):
        """
        Update a product variant.
        
        Args:
            variant: ProductVariant object
            
        Returns:
            True if updated successfully
        """
        try:
            # Check for duplicate
            self.db.execute(
                '''
                SELECT id FROM product_variants 
                WHERE product_id = ? AND size = ? AND color = ? AND id != ?
                ''',
                (variant.product_id, variant.size, variant.color, variant.id)
            )
            
            existing = self.db.fetchone()
            if existing:
                raise Exception("Ya existe otra variante con esta talla y color para este producto")
                
            # Update the variant
            self.db.execute(
                '''
                UPDATE product_variants
                SET size = ?, color = ?
                WHERE id = ?
                ''',
                (variant.size, variant.color, variant.id)
            )
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error updating variant: {str(e)}")
    
    def delete_variant(self, variant_id):
        """
        Delete a product variant.
        
        Args:
            variant_id: ID of the variant to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            # Check if the variant is used in any sales
            self.db.execute(
                '''
                SELECT COUNT(*) FROM sale_items
                WHERE product_variant_id = ?
                ''',
                (variant_id,)
            )
            
            count = self.db.fetchone()[0]
            if count > 0:
                raise Exception("No se puede eliminar la variante porque está asociada a ventas existentes")
                
            # Delete inventory record
            self.db.execute('DELETE FROM inventory WHERE product_variant_id = ?', (variant_id,))
            
            # Delete the variant
            self.db.execute('DELETE FROM product_variants WHERE id = ?', (variant_id,))
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error deleting variant: {str(e)}")
    
    # Category methods
    def get_all_categories(self):
        """
        Get all product categories.
        
        Returns:
            List of Category objects
        """
        try:
            self.db.execute('SELECT * FROM categories ORDER BY name')
            categories_data = self.db.fetchall()
            
            categories = []
            for cat_data in categories_data:
                category = Category(
                    id=cat_data[0],
                    name=cat_data[1],
                    description=cat_data[2]
                )
                categories.append(category)
                
            return categories
            
        except Exception as e:
            raise Exception(f"Error getting categories: {str(e)}")
    
    def add_category(self, category):
        """
        Add a new product category.
        
        Args:
            category: Category object
            
        Returns:
            ID of the newly created category
        """
        try:
            self.db.execute(
                'INSERT INTO categories (name, description) VALUES (?, ?)',
                (category.name, category.description)
            )
            
            category_id = self.db.cursor.lastrowid
            self.db.commit()
            return category_id
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error adding category: {str(e)}")
    
    def update_category(self, category):
        """
        Update an existing category.
        
        Args:
            category: Category object with updated information
            
        Returns:
            True if updated successfully
        """
        try:
            self.db.execute(
                'UPDATE categories SET name = ?, description = ? WHERE id = ?',
                (category.name, category.description, category.id)
            )
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error updating category: {str(e)}")
    
    def delete_category(self, category_id):
        """
        Delete a category if it's not used by any products.
        
        Args:
            category_id: ID of the category to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            # Check if the category is used by any products
            self.db.execute(
                'SELECT COUNT(*) FROM products WHERE category_id = ?',
                (category_id,)
            )
            
            count = self.db.fetchone()[0]
            if count > 0:
                raise Exception("No se puede eliminar la categoría porque hay productos asociados a ella")
                
            # Delete the category
            self.db.execute('DELETE FROM categories WHERE id = ?', (category_id,))
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error deleting category: {str(e)}")
    
    def get_products_on_sale(self):
        """
        Get all products with active discounts.
        
        Returns:
            List of Product objects with active discounts
        """
        try:
            current_date = datetime.now().isoformat()
            
            self.db.execute(
                '''
                SELECT * FROM products 
                WHERE discount_percent > 0
                AND (
                    (discount_start_date IS NULL OR discount_start_date <= ?)
                    AND
                    (discount_end_date IS NULL OR discount_end_date >= ?)
                )
                ORDER BY name
                ''',
                (current_date, current_date)
            )
            
            products_data = self.db.fetchall()
            products = []
            
            for product_data in products_data:
                id_idx, code_idx, name_idx, desc_idx, cat_idx, price_idx = 0, 1, 2, 3, 4, 5
                disc_pct_idx, disc_start_idx, disc_end_idx, created_idx, updated_idx = 6, 7, 8, 9, 10
                
                product = Product(
                    id=product_data[id_idx],
                    code=product_data[code_idx],
                    name=product_data[name_idx],
                    description=product_data[desc_idx],
                    category_id=product_data[cat_idx],
                    price=product_data[price_idx],
                    discount_percent=product_data[disc_pct_idx],
                    discount_start_date=product_data[disc_start_idx],
                    discount_end_date=product_data[disc_end_idx],
                    created_at=product_data[created_idx],
                    updated_at=product_data[updated_idx]
                )
                
                products.append(product)
                
            return products
            
        except Exception as e:
            raise Exception(f"Error getting products on sale: {str(e)}")
    
    def search_products(self, search_term):
        """
        Search for products by name, description, or code.
        
        Args:
            search_term: Search query
            
        Returns:
            List of matching Product objects
        """
        try:
            search_pattern = f"%{search_term}%"
            
            self.db.execute(
                '''
                SELECT * FROM products 
                WHERE name LIKE ? OR description LIKE ? OR code LIKE ?
                ORDER BY name
                ''',
                (search_pattern, search_pattern, search_pattern)
            )
            
            products_data = self.db.fetchall()
            products = []
            
            for product_data in products_data:
                id_idx, code_idx, name_idx, desc_idx, cat_idx, price_idx = 0, 1, 2, 3, 4, 5
                disc_pct_idx, disc_start_idx, disc_end_idx, created_idx, updated_idx = 6, 7, 8, 9, 10
                
                product = Product(
                    id=product_data[id_idx],
                    code=product_data[code_idx],
                    name=product_data[name_idx],
                    description=product_data[desc_idx],
                    category_id=product_data[cat_idx],
                    price=product_data[price_idx],
                    discount_percent=product_data[disc_pct_idx],
                    discount_start_date=product_data[disc_start_idx],
                    discount_end_date=product_data[disc_end_idx],
                    created_at=product_data[created_idx],
                    updated_at=product_data[updated_idx]
                )
                
                products.append(product)
                
            return products
            
        except Exception as e:
            raise Exception(f"Error searching products: {str(e)}")
