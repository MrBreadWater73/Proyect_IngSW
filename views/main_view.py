"""
Main view for the Clothing Store Management System.
Provides the main application window and navigation framework.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controllers.product_controller import ProductController
from controllers.inventory_controller import InventoryController
from controllers.customer_controller import CustomerController
from controllers.sale_controller import SaleController
from controllers.supplier_controller import SupplierController
from controllers.report_controller import ReportController

from views.product_view import ProductView
from views.inventory_view import InventoryView
from views.customer_view import CustomerView
from views.sale_view import SaleView
from views.supplier_view import SupplierView
from views.report_view import ReportView


class MainView:
    """
    Main application view that manages the UI framework and navigation.
    """
    
    def __init__(self, root, db_manager):
        """
        Initialize the main application view.
        
        Args:
            root: Tkinter root window
            db_manager: Database manager instance
        """
        self.root = root
        self.db_manager = db_manager
        self.active_view = None
        
        # Set up controllers
        self.product_controller = ProductController(db_manager)
        self.inventory_controller = InventoryController(db_manager)
        self.customer_controller = CustomerController(db_manager)
        self.sale_controller = SaleController(db_manager, self.inventory_controller)
        self.supplier_controller = SupplierController(db_manager)
        self.report_controller = ReportController(db_manager)
        
        # Configure the root window
        self.setup_ui()
        
        # Load the default view (sales)
        self.show_view("sales")
        
    def setup_ui(self):
        """
        Set up the UI framework including navigation and content areas.
        """
        # Configure root window styling
        self.root.configure(bg="#f0f0f0")
        self.root.option_add("*Font", "Arial 10")
        
        # Create a style for ttk widgets
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", padding=6, relief="flat", background="#f0f0f0")
        self.style.configure("TNotebook", background="#f0f0f0", borderwidth=0)
        self.style.configure("TNotebook.Tab", padding=[12, 4], font=("Arial", 10, "bold"))
        
        # Main layout frames
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header frame
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Logo/title
        self.title_label = ttk.Label(
            self.header_frame, 
            text="Sistema de Gestión - Tienda de Ropa",
            font=("Arial", 16, "bold"),
            background="#f0f0f0"
        )
        self.title_label.pack(side=tk.LEFT, padx=5)
        
        # Navigation frame
        self.nav_frame = ttk.Frame(self.main_frame)
        self.nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Navigation buttons
        self.buttons = []
        
        self.create_nav_button("Ventas", lambda: self.show_view("sales"))
        self.create_nav_button("Productos", lambda: self.show_view("products"))
        self.create_nav_button("Inventario", lambda: self.show_view("inventory"))
        self.create_nav_button("Clientes", lambda: self.show_view("customers"))
        self.create_nav_button("Proveedores", lambda: self.show_view("suppliers"))
        self.create_nav_button("Reportes", lambda: self.show_view("reports"))
        
        # Content frame (will be populated by specific views)
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(
            self.status_frame, 
            text="Listo",
            background="#f0f0f0",
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Version info
        self.version_label = ttk.Label(
            self.status_frame, 
            text="v1.0.0",
            background="#f0f0f0"
        )
        self.version_label.pack(side=tk.RIGHT, padx=5)
        
    def create_nav_button(self, text, command):
        """
        Create a navigation button.
        
        Args:
            text: Button text
            command: Function to execute when button is clicked
        """
        style_name = f"{text.lower()}.TButton"
        self.style.configure(style_name, font=("Arial", 10), padding=8)
        
        button = ttk.Button(
            self.nav_frame,
            text=text,
            command=command,
            style=style_name
        )
        button.pack(side=tk.LEFT, padx=5)
        self.buttons.append((text.lower(), button))
        
    def show_view(self, view_name):
        """
        Switch to the specified view.
        
        Args:
            view_name: Name of the view to display
        """
        # Clear the content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Highlight the active button
        for name, button in self.buttons:
            if name == view_name:
                button.state(["pressed"])
            else:
                button.state(["!pressed"])
        
        # Display the selected view
        if view_name == "sales":
            self.active_view = SaleView(
                self.content_frame, 
                self.sale_controller,
                self.product_controller,
                self.customer_controller
            )
        elif view_name == "products":
            self.active_view = ProductView(
                self.content_frame, 
                self.product_controller,
                self.inventory_controller
            )
        elif view_name == "inventory":
            self.active_view = InventoryView(
                self.content_frame, 
                self.inventory_controller,
                self.product_controller
            )
        elif view_name == "customers":
            self.active_view = CustomerView(
                self.content_frame, 
                self.customer_controller,
                self.sale_controller
            )
        elif view_name == "suppliers":
            self.active_view = SupplierView(
                self.content_frame, 
                self.supplier_controller,
                self.product_controller
            )
        elif view_name == "reports":
            self.active_view = ReportView(
                self.content_frame, 
                self.report_controller,
                self.product_controller,
                self.customer_controller,
                self.sale_controller
            )
            
        # Update status bar
        self.update_status(f"Vista: {view_name.capitalize()}")
        
    def update_status(self, message):
        """
        Update the status bar message.
        
        Args:
            message: New status message
        """
        self.status_label.config(text=message)
