"""
Product model for the Clothing Store Management System.
"""
from datetime import datetime


class Product:
    """
    Represents a product in the clothing store.
    """
    
    def __init__(self, id=None, code="", name="", description="", category_id=None,
                 price=0.0, discount_percent=0.0, discount_start_date=None,
                 discount_end_date=None, created_at=None, updated_at=None):
        """
        Initialize a product instance.
        
        Args:
            id: Product ID (None for new products)
            code: Unique product code
            name: Product name
            description: Product description
            category_id: Category ID
            price: Product price
            discount_percent: Discount percentage (0-100)
            discount_start_date: Start date for discount
            discount_end_date: End date for discount
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self.id = id
        self.code = code
        self.name = name
        self.description = description
        self.category_id = category_id
        self.price = price
        self.discount_percent = discount_percent
        self.discount_start_date = discount_start_date
        self.discount_end_date = discount_end_date
        self.created_at = created_at
        self.updated_at = updated_at
        self.variants = []
        
    def get_current_price(self):
        """
        Calculate the current price considering any active discounts.
        
        Returns:
            The current price with discount applied if active
        """
        if self.is_discount_active():
            return self.price * (1 - self.discount_percent / 100)
        return self.price
        
    def is_discount_active(self):
        """
        Check if the product has an active discount.
        
        Returns:
            True if discount is active, False otherwise
        """
        if self.discount_percent <= 0:
            return False
            
        now = datetime.now()
        
        # Check if discount has start and end dates
        if self.discount_start_date and self.discount_end_date:
            start = datetime.fromisoformat(self.discount_start_date)
            end = datetime.fromisoformat(self.discount_end_date)
            return start <= now <= end
            
        # If only start date is specified
        if self.discount_start_date and not self.discount_end_date:
            start = datetime.fromisoformat(self.discount_start_date)
            return start <= now
            
        # If only end date is specified
        if not self.discount_start_date and self.discount_end_date:
            end = datetime.fromisoformat(self.discount_end_date)
            return now <= end
            
        # If no dates are specified but there is a discount
        return self.discount_percent > 0


class ProductVariant:
    """
    Represents a specific variant of a product (size + color).
    """
    
    def __init__(self, id=None, product_id=None, size="", color=""):
        """
        Initialize a product variant.
        
        Args:
            id: Variant ID (None for new variants)
            product_id: Parent product ID
            size: Size of the product
            color: Color of the product
        """
        self.id = id
        self.product_id = product_id
        self.size = size
        self.color = color
        self.inventory_quantity = 0
        
    def __str__(self):
        """
        String representation of the product variant.
        
        Returns:
            A string describing the variant
        """
        return f"{self.color} - Talla {self.size}"


class Category:
    """
    Represents a product category.
    """
    
    def __init__(self, id=None, name="", description=""):
        """
        Initialize a category.
        
        Args:
            id: Category ID
            name: Category name
            description: Category description
        """
        self.id = id
        self.name = name
        self.description = description
        
    def __str__(self):
        """
        String representation of the category.
        
        Returns:
            Category name
        """
        return self.name
