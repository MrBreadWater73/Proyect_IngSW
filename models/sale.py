"""
Sale model for the Clothing Store Management System.
"""
from datetime import datetime


class Sale:
    """
    Represents a sale in the clothing store.
    """
    
    # Payment method constants
    CASH = "EFECTIVO"
    CREDIT_CARD = "TARJETA"
    TRANSFER = "TRANSFERENCIA"
    
    def __init__(self, id=None, customer_id=None, sale_date=None, 
                 payment_method=CASH, total_amount=0.0):
        """
        Initialize a sale.
        
        Args:
            id: Sale ID (None for new sales)
            customer_id: Customer ID (can be None for anonymous sales)
            sale_date: Date and time of the sale
            payment_method: Method of payment (CASH, CREDIT_CARD, TRANSFER)
            total_amount: Total amount of the sale
        """
        self.id = id
        self.customer_id = customer_id
        self.sale_date = sale_date or datetime.now().isoformat()
        self.payment_method = payment_method
        self.total_amount = total_amount
        self.items = []  # Will hold SaleItem objects
        
    def add_item(self, sale_item):
        """
        Add an item to the sale.
        
        Args:
            sale_item: SaleItem object to add
            
        Returns:
            True if item was added, False otherwise
        """
        # Check if the same product variant is already in the sale
        for item in self.items:
            if item.product_variant_id == sale_item.product_variant_id:
                # Update existing item quantity and recalculate subtotal
                item.quantity += sale_item.quantity
                item.recalculate_subtotal()
                self.recalculate_total()
                return True
                
        # Add as a new item
        self.items.append(sale_item)
        self.recalculate_total()
        return True
        
    def remove_item(self, item_index):
        """
        Remove an item from the sale.
        
        Args:
            item_index: Index of the item to remove
            
        Returns:
            True if removed, False if index is invalid
        """
        if 0 <= item_index < len(self.items):
            del self.items[item_index]
            self.recalculate_total()
            return True
        return False
        
    def recalculate_total(self):
        """
        Recalculate the total amount of the sale.
        """
        self.total_amount = sum(item.subtotal for item in self.items)
        
    def get_payment_methods(self):
        """
        Get available payment methods.
        
        Returns:
            List of payment method options
        """
        return [self.CASH, self.CREDIT_CARD, self.TRANSFER]


class SaleItem:
    """
    Represents an item in a sale.
    """
    
    def __init__(self, id=None, sale_id=None, product_variant_id=None, 
                 quantity=1, unit_price=0.0, discount_percent=0.0, subtotal=0.0):
        """
        Initialize a sale item.
        
        Args:
            id: Sale item ID (None for new items)
            sale_id: ID of the parent sale
            product_variant_id: ID of the product variant
            quantity: Quantity sold
            unit_price: Price per unit
            discount_percent: Discount percentage applied
            subtotal: Total for this item (quantity * unit_price * (1 - discount_percent/100))
        """
        self.id = id
        self.sale_id = sale_id
        self.product_variant_id = product_variant_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.discount_percent = discount_percent
        self.subtotal = subtotal if subtotal > 0 else self.calculate_subtotal()
        
        # These will be populated from product data when needed
        self.product_name = ""
        self.variant_info = ""
        
    def calculate_subtotal(self):
        """
        Calculate the subtotal for this item.
        
        Returns:
            Subtotal amount
        """
        return self.quantity * self.unit_price * (1 - self.discount_percent / 100)
        
    def recalculate_subtotal(self):
        """
        Recalculate and update the subtotal.
        """
        self.subtotal = self.calculate_subtotal()
