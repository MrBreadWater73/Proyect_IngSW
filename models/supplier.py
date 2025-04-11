"""
Supplier model for the Clothing Store Management System.
"""
from datetime import datetime


class Supplier:
    """
    Represents a supplier for the clothing store.
    """
    
    def __init__(self, id=None, name="", contact_person="", email="", phone="", 
                 address="", created_at=None, updated_at=None):
        """
        Initialize a supplier.
        
        Args:
            id: Supplier ID (None for new suppliers)
            name: Company name
            contact_person: Name of the main contact person
            email: Email address
            phone: Phone number
            address: Physical address
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self.id = id
        self.name = name
        self.contact_person = contact_person
        self.email = email
        self.phone = phone
        self.address = address
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
        self.products = []  # Will hold product IDs supplied by this supplier
        
    def add_product(self, product_id):
        """
        Add a product to the supplier's catalog.
        
        Args:
            product_id: ID of the product
            
        Returns:
            True if added, False if already in list
        """
        if product_id not in self.products:
            self.products.append(product_id)
            return True
        return False
        
    def remove_product(self, product_id):
        """
        Remove a product from the supplier's catalog.
        
        Args:
            product_id: ID of the product
            
        Returns:
            True if removed, False if not in list
        """
        if product_id in self.products:
            self.products.remove(product_id)
            return True
        return False
        
    def __str__(self):
        """
        String representation of the supplier.
        
        Returns:
            Supplier name
        """
        return self.name
