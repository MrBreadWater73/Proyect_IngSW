"""
Customer model for the Clothing Store Management System.
"""
from datetime import datetime


class Customer:
    """
    Represents a customer in the clothing store.
    """
    
    def __init__(self, id=None, name="", email=None, phone=None, address=None, 
                 created_at=None, updated_at=None):
        """
        Initialize a customer.
        
        Args:
            id: Customer ID (None for new customers)
            name: Customer's full name
            email: Customer's email address (optional)
            phone: Customer's phone number (optional)
            address: Customer's address (optional)
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
        self.purchase_history = []  # Will store Sale objects
        
    def get_total_purchases(self):
        """
        Calculate the total amount of all purchases made by the customer.
        
        Returns:
            Total purchase amount
        """
        return sum(sale.total_amount for sale in self.purchase_history)
        
    def get_purchase_count(self):
        """
        Get the number of purchases made by the customer.
        
        Returns:
            Count of purchases
        """
        return len(self.purchase_history)
        
    def __str__(self):
        """
        String representation of the customer.
        
        Returns:
            Customer name and ID
        """
        return f"{self.name} (ID: {self.id})"
