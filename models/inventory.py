"""
Inventory model for the Clothing Store Management System.
"""
from datetime import datetime


class Inventory:
    """
    Represents inventory information for a product variant.
    """
    
    def __init__(self, id=None, product_variant_id=None, quantity=0, last_updated=None):
        """
        Initialize an inventory entry.
        
        Args:
            id: Inventory entry ID
            product_variant_id: ID of the associated product variant
            quantity: Current stock quantity
            last_updated: Last update timestamp
        """
        self.id = id
        self.product_variant_id = product_variant_id
        self.quantity = quantity
        self.last_updated = last_updated or datetime.now().isoformat()
        
    def is_in_stock(self):
        """
        Check if the item is in stock.
        
        Returns:
            True if quantity > 0, False otherwise
        """
        return self.quantity > 0
        
    def has_low_stock(self, threshold=5):
        """
        Check if the item has low stock.
        
        Args:
            threshold: The quantity threshold for low stock
            
        Returns:
            True if quantity is below threshold but above 0
        """
        return 0 < self.quantity < threshold


class InventoryTransaction:
    """
    Represents a transaction affecting inventory.
    """
    
    # Transaction types
    SALE = "SALE"
    PURCHASE = "PURCHASE"
    ADJUSTMENT = "ADJUSTMENT"
    RETURN = "RETURN"
    
    def __init__(self, id=None, product_variant_id=None, quantity_change=0, 
                 transaction_type=None, reference_id=None, transaction_date=None, notes=None):
        """
        Initialize an inventory transaction.
        
        Args:
            id: Transaction ID
            product_variant_id: ID of the associated product variant
            quantity_change: Change in quantity (positive for increases, negative for decreases)
            transaction_type: Type of transaction (SALE, PURCHASE, ADJUSTMENT, RETURN)
            reference_id: Reference to related entity (e.g., sale ID for sale transactions)
            transaction_date: Date and time of the transaction
            notes: Additional notes about the transaction
        """
        self.id = id
        self.product_variant_id = product_variant_id
        self.quantity_change = quantity_change
        self.transaction_type = transaction_type
        self.reference_id = reference_id
        self.transaction_date = transaction_date or datetime.now().isoformat()
        self.notes = notes
