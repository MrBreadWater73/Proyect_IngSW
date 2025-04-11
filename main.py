#!/usr/bin/env python3
"""
Main entry point for the Clothing Store Management System.
This standalone application manages products, inventory, customers,
sales, and suppliers for a clothing retail store without internet connectivity.
"""
import os
import sys
import tkinter as tk
from tkinter import messagebox

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from views.main_view import MainView


def main():
    """
    Initialize the database and launch the main application window.
    """
    try:
        # Create or connect to the database
        db_manager = DatabaseManager('clothing_store.db')
        db_manager.setup_database()
        
        # Initialize the Tkinter application
        root = tk.Tk()
        root.title("Sistema de Gestión - Tienda de Ropa")
        root.geometry("1200x700")  # Set initial window size
        root.minsize(800, 600)  # Set minimum window size
        
        # Create the main application view
        app = MainView(root, db_manager)
        
        # Start the application main loop
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error de Inicialización", 
                            f"No se pudo iniciar la aplicación: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
