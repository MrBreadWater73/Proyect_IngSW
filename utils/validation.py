"""
Validation utilities for the Clothing Store Management System.
"""


def validate_int(value):
    """
    Validate that a value is a valid integer.
    
    Args:
        value: Value to validate
        
    Returns:
        Validated integer or None
    """
    try:
        if value == "":
            return None
        return int(value)
    except (ValueError, TypeError):
        return None


def validate_float(value):
    """
    Validate that a value is a valid float.
    
    Args:
        value: Value to validate
        
    Returns:
        Validated float or None
    """
    try:
        if value == "":
            return None
        return float(value)
    except (ValueError, TypeError):
        return None


def validate_date(date_str):
    """
    Validate that a value is a valid date in ISO format (YYYY-MM-DD).
    
    Args:
        date_str: Date string to validate
        
    Returns:
        Validated date string or None
    """
    if not date_str or date_str == "":
        return None
        
    # Simple validation of format
    parts = date_str.split('-')
    if len(parts) != 3:
        return None
        
    try:
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        
        # Basic validity check
        if not (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31):
            return None
            
        # Return the original string if valid
        return date_str
    except (ValueError, IndexError):
        return None