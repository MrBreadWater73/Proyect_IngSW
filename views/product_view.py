"""
Product view for the Clothing Store Management System.
Manages the UI for product-related operations.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.product import Product, ProductVariant, Category
from utils.validation import validate_float, validate_int


class ProductView:
    """
    View for managing products, variants, and categories.
    """
    
    def __init__(self, parent, product_controller, inventory_controller):
        """
        Initialize the product view.
        
        Args:
            parent: Parent widget
            product_controller: Product controller instance
            inventory_controller: Inventory controller instance
        """
        self.parent = parent
        self.product_controller = product_controller
        self.inventory_controller = inventory_controller
        
        # Current selected items
        self.selected_product = None
        self.selected_variant = None
        self.selected_category = None
        
        # Setup UI components
        self.setup_ui()
        
        # Load initial data
        self.load_categories()
        self.load_products()
        
    def setup_ui(self):
        """
        Set up the UI components.
        """
        # Main container
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Products tab
        self.products_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.products_frame, text="Productos")
        
        # Categories tab
        self.categories_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.categories_frame, text="Categorías")
        
        # Setup each tab
        self.setup_products_tab()
        self.setup_categories_tab()
        
    def setup_products_tab(self):
        """
        Set up the Products tab UI.
        """
        # Split into left (list) and right (details) panes
        self.products_paned = ttk.PanedWindow(self.products_frame, orient=tk.HORIZONTAL)
        self.products_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left frame - Product list
        self.products_list_frame = ttk.Frame(self.products_paned)
        self.products_paned.add(self.products_list_frame, weight=40)
        
        # Search frame
        self.search_frame = ttk.Frame(self.products_list_frame)
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.search_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(self.search_frame, text="Buscar", command=self.search_products).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.search_frame, text="Limpiar", command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        # Category filter
        self.filter_frame = ttk.Frame(self.products_list_frame)
        self.filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.filter_frame, text="Categoría:").pack(side=tk.LEFT, padx=5)
        self.category_filter_var = tk.StringVar()
        self.category_filter_combo = ttk.Combobox(self.filter_frame, textvariable=self.category_filter_var)
        self.category_filter_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.category_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_products_by_category())
        ttk.Button(self.filter_frame, text="Todos", command=self.clear_category_filter).pack(side=tk.LEFT, padx=5)
        
        # Products list
        self.products_list_frame_inner = ttk.Frame(self.products_list_frame)
        self.products_list_frame_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Products treeview
        self.products_tree = ttk.Treeview(
            self.products_list_frame_inner,
            columns=("ID", "Código", "Nombre", "Precio", "Descuento"),
            show="headings"
        )
        self.products_tree.heading("ID", text="ID")
        self.products_tree.heading("Código", text="Código")
        self.products_tree.heading("Nombre", text="Nombre")
        self.products_tree.heading("Precio", text="Precio")
        self.products_tree.heading("Descuento", text="Descuento")
        
        self.products_tree.column("ID", width=50, anchor=tk.CENTER)
        self.products_tree.column("Código", width=100)
        self.products_tree.column("Nombre", width=200)
        self.products_tree.column("Precio", width=100, anchor=tk.E)
        self.products_tree.column("Descuento", width=100, anchor=tk.E)
        
        # Scrollbar for products tree
        products_scrollbar = ttk.Scrollbar(self.products_list_frame_inner, orient="vertical", command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=products_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        products_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind the treeview selection to a handler
        self.products_tree.bind("<<TreeviewSelect>>", self.on_product_selected)
        
        # Buttons frame
        self.products_buttons_frame = ttk.Frame(self.products_list_frame)
        self.products_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(self.products_buttons_frame, text="Nuevo", command=self.show_add_product_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.products_buttons_frame, text="Editar", command=self.show_edit_product_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.products_buttons_frame, text="Eliminar", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.products_buttons_frame, text="Actualizar", command=self.load_products).pack(side=tk.RIGHT, padx=5)
        
        # Right frame - Product details
        self.product_details_frame = ttk.Frame(self.products_paned)
        self.products_paned.add(self.product_details_frame, weight=60)
        
        # Product info frame
        self.product_info_frame = ttk.LabelFrame(self.product_details_frame, text="Información del Producto")
        self.product_info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Product info grid
        self.product_info_grid = ttk.Frame(self.product_info_frame)
        self.product_info_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Row 0
        ttk.Label(self.product_info_grid, text="Código:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.product_code_var = tk.StringVar()
        ttk.Label(self.product_info_grid, textvariable=self.product_code_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(self.product_info_grid, text="Nombre:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.product_name_var = tk.StringVar()
        ttk.Label(self.product_info_grid, textvariable=self.product_name_var).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Row 1
        ttk.Label(self.product_info_grid, text="Categoría:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.product_category_var = tk.StringVar()
        ttk.Label(self.product_info_grid, textvariable=self.product_category_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(self.product_info_grid, text="Precio:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.product_price_var = tk.StringVar()
        ttk.Label(self.product_info_grid, textvariable=self.product_price_var).grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Row 2
        ttk.Label(self.product_info_grid, text="Descuento:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.product_discount_var = tk.StringVar()
        ttk.Label(self.product_info_grid, textvariable=self.product_discount_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(self.product_info_grid, text="Precio Final:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=2)
        self.product_final_price_var = tk.StringVar()
        ttk.Label(self.product_info_grid, textvariable=self.product_final_price_var).grid(row=2, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Row 3
        ttk.Label(self.product_info_grid, text="Descripción:").grid(row=3, column=0, sticky=tk.NW, padx=5, pady=2)
        self.product_description_var = tk.StringVar()
        ttk.Label(self.product_info_grid, textvariable=self.product_description_var, wraplength=400).grid(row=3, column=1, columnspan=3, sticky=tk.W, padx=5, pady=2)
        
        # Variants frame
        self.variants_frame = ttk.LabelFrame(self.product_details_frame, text="Variantes del Producto")
        self.variants_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Variants treeview
        self.variants_tree = ttk.Treeview(
            self.variants_frame,
            columns=("ID", "Talla", "Color", "Stock"),
            show="headings"
        )
        self.variants_tree.heading("ID", text="ID")
        self.variants_tree.heading("Talla", text="Talla")
        self.variants_tree.heading("Color", text="Color")
        self.variants_tree.heading("Stock", text="Stock")
        
        self.variants_tree.column("ID", width=50, anchor=tk.CENTER)
        self.variants_tree.column("Talla", width=100)
        self.variants_tree.column("Color", width=150)
        self.variants_tree.column("Stock", width=100, anchor=tk.E)
        
        # Scrollbar for variants tree
        variants_scrollbar = ttk.Scrollbar(self.variants_frame, orient="vertical", command=self.variants_tree.yview)
        self.variants_tree.configure(yscrollcommand=variants_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.variants_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        variants_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Bind the treeview selection to a handler
        self.variants_tree.bind("<<TreeviewSelect>>", self.on_variant_selected)
        
        # Variants buttons
        self.variants_buttons_frame = ttk.Frame(self.product_details_frame)
        self.variants_buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(self.variants_buttons_frame, text="Agregar Variante", command=self.show_add_variant_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.variants_buttons_frame, text="Editar Variante", command=self.show_edit_variant_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.variants_buttons_frame, text="Eliminar Variante", command=self.delete_variant).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.variants_buttons_frame, text="Ajustar Stock", command=self.show_adjust_stock_dialog).pack(side=tk.LEFT, padx=5)
    
    def setup_categories_tab(self):
        """
        Set up the Categories tab UI.
        """
        # Split into left (list) and right (details) panes
        self.categories_paned = ttk.PanedWindow(self.categories_frame, orient=tk.HORIZONTAL)
        self.categories_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left frame - Categories list
        self.categories_list_frame = ttk.Frame(self.categories_paned)
        self.categories_paned.add(self.categories_list_frame, weight=40)
        
        # Categories treeview
        self.categories_tree = ttk.Treeview(
            self.categories_list_frame,
            columns=("ID", "Nombre"),
            show="headings"
        )
        self.categories_tree.heading("ID", text="ID")
        self.categories_tree.heading("Nombre", text="Nombre")
        
        self.categories_tree.column("ID", width=50, anchor=tk.CENTER)
        self.categories_tree.column("Nombre", width=200)
        
        # Scrollbar for categories tree
        categories_scrollbar = ttk.Scrollbar(self.categories_list_frame, orient="vertical", command=self.categories_tree.yview)
        self.categories_tree.configure(yscrollcommand=categories_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.categories_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        categories_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Bind the treeview selection to a handler
        self.categories_tree.bind("<<TreeviewSelect>>", self.on_category_selected)
        
        # Buttons frame
        self.categories_buttons_frame = ttk.Frame(self.categories_list_frame)
        self.categories_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(self.categories_buttons_frame, text="Nueva", command=self.show_add_category_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.categories_buttons_frame, text="Editar", command=self.show_edit_category_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.categories_buttons_frame, text="Eliminar", command=self.delete_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.categories_buttons_frame, text="Actualizar", command=self.load_categories).pack(side=tk.RIGHT, padx=5)
        
        # Right frame - Category details
        self.category_details_frame = ttk.Frame(self.categories_paned)
        self.categories_paned.add(self.category_details_frame, weight=60)
        
        # Category info
        self.category_info_frame = ttk.LabelFrame(self.category_details_frame, text="Información de la Categoría")
        self.category_info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Category info grid
        self.category_info_grid = ttk.Frame(self.category_info_frame)
        self.category_info_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Row 0
        ttk.Label(self.category_info_grid, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.category_id_var = tk.StringVar()
        ttk.Label(self.category_info_grid, textvariable=self.category_id_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Row 1
        ttk.Label(self.category_info_grid, text="Nombre:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.category_name_var = tk.StringVar()
        ttk.Label(self.category_info_grid, textvariable=self.category_name_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Row 2
        ttk.Label(self.category_info_grid, text="Descripción:").grid(row=2, column=0, sticky=tk.NW, padx=5, pady=2)
        self.category_description_var = tk.StringVar()
        ttk.Label(self.category_info_grid, textvariable=self.category_description_var, wraplength=300).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Products in category frame
        self.category_products_frame = ttk.LabelFrame(self.category_details_frame, text="Productos en esta Categoría")
        self.category_products_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Products in category treeview
        self.category_products_tree = ttk.Treeview(
            self.category_products_frame,
            columns=("ID", "Código", "Nombre", "Precio"),
            show="headings"
        )
        self.category_products_tree.heading("ID", text="ID")
        self.category_products_tree.heading("Código", text="Código")
        self.category_products_tree.heading("Nombre", text="Nombre")
        self.category_products_tree.heading("Precio", text="Precio")
        
        self.category_products_tree.column("ID", width=50, anchor=tk.CENTER)
        self.category_products_tree.column("Código", width=100)
        self.category_products_tree.column("Nombre", width=200)
        self.category_products_tree.column("Precio", width=100, anchor=tk.E)
        
        # Scrollbar for category products tree
        category_products_scrollbar = ttk.Scrollbar(self.category_products_frame, orient="vertical", command=self.category_products_tree.yview)
        self.category_products_tree.configure(yscrollcommand=category_products_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.category_products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        category_products_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
    
    # ======= Products Tab Methods =======
    
    def load_products(self):
        """
        Load products from the database and display them in the treeview.
        """
        # Clear the treeview
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
            
        try:
            # Get all products
            products = self.product_controller.get_all_products()
            
            # Insert into treeview
            for product in products:
                current_price = product.get_current_price()
                discount_text = f"{product.discount_percent}%" if product.discount_percent > 0 else "No"
                
                self.products_tree.insert(
                    "", 
                    "end", 
                    values=(
                        product.id, 
                        product.code, 
                        product.name, 
                        f"${product.price:.2f}", 
                        discount_text
                    )
                )
                
            # Update the category filter
            self.update_category_filter()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar productos: {str(e)}")
    
    def update_category_filter(self):
        """
        Update the category filter combobox with current categories.
        """
        try:
            # Get all categories
            categories = self.product_controller.get_all_categories()
            
            # Clear the current values
            self.category_filter_combo['values'] = []
            
            # If there are categories, add them to the combobox
            if categories:
                self.category_filter_combo['values'] = ["Todas"] + [category.name for category in categories]
                self.category_filter_combo.current(0)  # Select "All" by default
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar filtro de categorías: {str(e)}")
    
    def filter_products_by_category(self):
        """
        Filter products by the selected category.
        """
        selected_category = self.category_filter_var.get()
        
        if selected_category == "Todas" or not selected_category:
            self.load_products()
            return
            
        try:
            # Get all categories to find the ID of the selected one
            categories = self.product_controller.get_all_categories()
            category_id = None
            
            for category in categories:
                if category.name == selected_category:
                    category_id = category.id
                    break
                    
            if category_id is None:
                messagebox.showerror("Error", "Categoría no encontrada")
                return
                
            # Clear the treeview
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
                
            # Get products in the selected category
            products = self.product_controller.get_all_products(category_id=category_id)
            
            # Insert into treeview
            for product in products:
                current_price = product.get_current_price()
                discount_text = f"{product.discount_percent}%" if product.discount_percent > 0 else "No"
                
                self.products_tree.insert(
                    "", 
                    "end", 
                    values=(
                        product.id, 
                        product.code, 
                        product.name, 
                        f"${product.price:.2f}", 
                        discount_text
                    )
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar productos: {str(e)}")
    
    def clear_category_filter(self):
        """
        Clear the category filter and show all products.
        """
        self.category_filter_combo.current(0)  # Select "All"
        self.load_products()
    
    def search_products(self):
        """
        Search products by name, code, or description.
        """
        search_term = self.search_var.get().strip()
        
        if not search_term:
            messagebox.showinfo("Información", "Ingrese un término de búsqueda")
            return
            
        try:
            # Clear the treeview
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
                
            # Search products
            products = self.product_controller.search_products(search_term)
            
            if not products:
                messagebox.showinfo("Información", "No se encontraron productos con ese término de búsqueda")
                return
                
            # Insert into treeview
            for product in products:
                current_price = product.get_current_price()
                discount_text = f"{product.discount_percent}%" if product.discount_percent > 0 else "No"
                
                self.products_tree.insert(
                    "", 
                    "end", 
                    values=(
                        product.id, 
                        product.code, 
                        product.name, 
                        f"${product.price:.2f}", 
                        discount_text
                    )
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar productos: {str(e)}")
    
    def clear_search(self):
        """
        Clear the search and reset the product list.
        """
        self.search_var.set("")
        self.load_products()
    
    def on_product_selected(self, event):
        """
        Handle product selection in the treeview.
        
        Args:
            event: Tkinter event
        """
        # Get the selected item
        selected_items = self.products_tree.selection()
        if not selected_items:
            return
            
        # Get the first selected item
        item = selected_items[0]
        product_id = self.products_tree.item(item, "values")[0]
        
        try:
            # Get the product details
            product = self.product_controller.get_product(product_id)
            if not product:
                return
                
            # Store the selected product
            self.selected_product = product
            
            # Update the product details UI
            self.update_product_details(product)
            
            # Load product variants
            self.load_product_variants(product)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles del producto: {str(e)}")
    
    def update_product_details(self, product):
        """
        Update the product details UI with the selected product information.
        
        Args:
            product: Product object
        """
        # Get category name
        category_name = ""
        try:
            categories = self.product_controller.get_all_categories()
            for category in categories:
                if category.id == product.category_id:
                    category_name = category.name
                    break
        except:
            pass
            
        # Update UI elements
        self.product_code_var.set(product.code)
        self.product_name_var.set(product.name)
        self.product_category_var.set(category_name)
        self.product_price_var.set(f"${product.price:.2f}")
        
        # Discount information
        if product.discount_percent > 0:
            discount_text = f"{product.discount_percent}%"
            if product.is_discount_active():
                discount_text += " (Activo)"
            else:
                discount_text += " (Inactivo)"
        else:
            discount_text = "No hay descuento"
            
        self.product_discount_var.set(discount_text)
        
        # Final price
        current_price = product.get_current_price()
        self.product_final_price_var.set(f"${current_price:.2f}")
        
        # Description
        self.product_description_var.set(product.description or "Sin descripción")
    
    def load_product_variants(self, product):
        """
        Load variants of the selected product into the variants treeview.
        
        Args:
            product: Product object
        """
        # Clear the treeview
        for item in self.variants_tree.get_children():
            self.variants_tree.delete(item)
            
        # Insert variants into treeview
        for variant in product.variants:
            self.variants_tree.insert(
                "", 
                "end", 
                values=(
                    variant.id, 
                    variant.size, 
                    variant.color, 
                    variant.inventory_quantity
                )
            )
    
    def on_variant_selected(self, event):
        """
        Handle variant selection in the treeview.
        
        Args:
            event: Tkinter event
        """
        # Get the selected item
        selected_items = self.variants_tree.selection()
        if not selected_items:
            self.selected_variant = None
            return
            
        # Get the first selected item
        item = selected_items[0]
        variant_id = self.variants_tree.item(item, "values")[0]
        
        # Find the variant in the product
        for variant in self.selected_product.variants:
            if variant.id == int(variant_id):
                self.selected_variant = variant
                break
    
    def show_add_product_dialog(self):
        """
        Show dialog to add a new product.
        """
        # Create a new dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Agregar Nuevo Producto")
        dialog.geometry("500x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Product form
        form_frame = ttk.Frame(dialog, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Code
        ttk.Label(form_frame, text="Código:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        code_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=code_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Name
        ttk.Label(form_frame, text="Nombre:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Category
        ttk.Label(form_frame, text="Categoría:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=category_var, width=27)
        category_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Price
        ttk.Label(form_frame, text="Precio:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        price_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=price_var, width=30).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Discount
        ttk.Label(form_frame, text="Descuento (%):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        discount_var = tk.StringVar(value="0")
        ttk.Entry(form_frame, textvariable=discount_var, width=30).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Discount dates frame
        discount_frame = ttk.LabelFrame(form_frame, text="Fechas de Descuento (Opcional)")
        discount_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Start date
        ttk.Label(discount_frame, text="Fecha inicio:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        start_date_var = tk.StringVar()
        ttk.Entry(discount_frame, textvariable=start_date_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(discount_frame, text="(YYYY-MM-DD)").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # End date
        ttk.Label(discount_frame, text="Fecha fin:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        end_date_var = tk.StringVar()
        ttk.Entry(discount_frame, textvariable=end_date_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(discount_frame, text="(YYYY-MM-DD)").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Description
        ttk.Label(form_frame, text="Descripción:").grid(row=6, column=0, sticky=tk.NW, padx=5, pady=5)
        description_var = tk.StringVar()
        description_text = tk.Text(form_frame, width=30, height=5)
        description_text.grid(row=6, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Variants frame
        variants_frame = ttk.LabelFrame(form_frame, text="Variantes Iniciales")
        variants_frame.grid(row=7, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Variants list
        variants_list = ttk.Frame(variants_frame)
        variants_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        variants = []
        
        def add_variant_row():
            row = len(variants)
            variant_frame = ttk.Frame(variants_list)
            variant_frame.pack(fill=tk.X, pady=2)
            
            size_var = tk.StringVar()
            color_var = tk.StringVar()
            
            ttk.Label(variant_frame, text="Talla:").pack(side=tk.LEFT, padx=5)
            ttk.Entry(variant_frame, textvariable=size_var, width=10).pack(side=tk.LEFT, padx=5)
            
            ttk.Label(variant_frame, text="Color:").pack(side=tk.LEFT, padx=5)
            ttk.Entry(variant_frame, textvariable=color_var, width=15).pack(side=tk.LEFT, padx=5)
            
            variant = {"size_var": size_var, "color_var": color_var}
            variants.append(variant)
            
            # Remove button
            ttk.Button(
                variant_frame, 
                text="X", 
                width=2,
                command=lambda v=variant: remove_variant(v)
            ).pack(side=tk.RIGHT, padx=5)
        
        def remove_variant(variant):
            if variant in variants:
                variants.remove(variant)
                # Refresh the variants list
                for widget in variants_list.winfo_children():
                    widget.destroy()
                    
                for v in variants:
                    variant_frame = ttk.Frame(variants_list)
                    variant_frame.pack(fill=tk.X, pady=2)
                    
                    ttk.Label(variant_frame, text="Talla:").pack(side=tk.LEFT, padx=5)
                    ttk.Entry(variant_frame, textvariable=v["size_var"], width=10).pack(side=tk.LEFT, padx=5)
                    
                    ttk.Label(variant_frame, text="Color:").pack(side=tk.LEFT, padx=5)
                    ttk.Entry(variant_frame, textvariable=v["color_var"], width=15).pack(side=tk.LEFT, padx=5)
                    
                    # Remove button
                    ttk.Button(
                        variant_frame, 
                        text="X", 
                        width=2,
                        command=lambda var=v: remove_variant(var)
                    ).pack(side=tk.RIGHT, padx=5)
        
        # Add a couple of variant rows by default
        add_variant_row()
        add_variant_row()
        
        # Add variant button
        ttk.Button(variants_frame, text="Agregar Variante", command=add_variant_row).pack(padx=5, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Load categories for combobox
        try:
            categories = self.product_controller.get_all_categories()
            if categories:
                category_combo['values'] = [category.name for category in categories]
                category_combo.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar categorías: {str(e)}")
        
        def save_product():
            # Validate inputs
            if not code_var.get().strip():
                messagebox.showerror("Error", "El código del producto es obligatorio")
                return
                
            if not name_var.get().strip():
                messagebox.showerror("Error", "El nombre del producto es obligatorio")
                return
                
            if not category_var.get().strip():
                messagebox.showerror("Error", "Debe seleccionar una categoría")
                return
                
            # Validate price
            try:
                price = float(price_var.get().strip())
                if price <= 0:
                    messagebox.showerror("Error", "El precio debe ser mayor que cero")
                    return
            except:
                messagebox.showerror("Error", "El precio debe ser un número válido")
                return
                
            # Validate discount
            try:
                discount = float(discount_var.get().strip())
                if discount < 0 or discount > 100:
                    messagebox.showerror("Error", "El descuento debe estar entre 0 y 100")
                    return
            except:
                messagebox.showerror("Error", "El descuento debe ser un número válido")
                return
                
            # Validate dates if provided
            start_date = None
            end_date = None
            
            if start_date_var.get().strip():
                try:
                    start_date = datetime.strptime(start_date_var.get().strip(), "%Y-%m-%d").isoformat()
                except:
                    messagebox.showerror("Error", "Formato de fecha de inicio inválido (debe ser YYYY-MM-DD)")
                    return
                    
            if end_date_var.get().strip():
                try:
                    end_date = datetime.strptime(end_date_var.get().strip(), "%Y-%m-%d").isoformat()
                except:
                    messagebox.showerror("Error", "Formato de fecha de fin inválido (debe ser YYYY-MM-DD)")
                    return
                    
            # Check if end date is after start date
            if start_date and end_date and start_date > end_date:
                messagebox.showerror("Error", "La fecha de fin debe ser posterior a la fecha de inicio")
                return
                
            # Get the category ID
            category_id = None
            for category in categories:
                if category.name == category_var.get():
                    category_id = category.id
                    break
                    
            if category_id is None:
                messagebox.showerror("Error", "Categoría no encontrada")
                return
                
            # Validate variants
            product_variants = []
            for variant in variants:
                size = variant["size_var"].get().strip()
                color = variant["color_var"].get().strip()
                
                if not size or not color:
                    messagebox.showerror("Error", "Todas las variantes deben tener talla y color")
                    return
                    
                # Check for duplicate variants
                for v in product_variants:
                    if v.size == size and v.color == color:
                        messagebox.showerror("Error", f"Variante duplicada: Talla {size}, Color {color}")
                        return
                        
                variant_obj = ProductVariant(size=size, color=color)
                product_variants.append(variant_obj)
                
            if not product_variants:
                messagebox.showerror("Error", "Debe agregar al menos una variante")
                return
                
            # Create product object
            product = Product(
                code=code_var.get().strip(),
                name=name_var.get().strip(),
                description=description_text.get("1.0", tk.END).strip(),
                category_id=category_id,
                price=price,
                discount_percent=discount,
                discount_start_date=start_date,
                discount_end_date=end_date
            )
            
            try:
                # Add the product
                product_id = self.product_controller.add_product(product, product_variants)
                
                # Success
                messagebox.showinfo("Éxito", f"Producto agregado con ID: {product_id}")
                
                # Refresh the products list
                self.load_products()
                
                # Close the dialog
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar producto: {str(e)}")
        
        # Save and cancel buttons
        ttk.Button(buttons_frame, text="Guardar", command=save_product).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def show_edit_product_dialog(self):
        """
        Show dialog to edit an existing product.
        """
        if not self.selected_product:
            messagebox.showinfo("Información", "Seleccione un producto para editar")
            return
            
        # Create a new dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Editar Producto")
        dialog.geometry("500x500")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Product form
        form_frame = ttk.Frame(dialog, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Code
        ttk.Label(form_frame, text="Código:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        code_var = tk.StringVar(value=self.selected_product.code)
        ttk.Entry(form_frame, textvariable=code_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Name
        ttk.Label(form_frame, text="Nombre:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar(value=self.selected_product.name)
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Category
        ttk.Label(form_frame, text="Categoría:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=category_var, width=27)
        category_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Price
        ttk.Label(form_frame, text="Precio:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        price_var = tk.StringVar(value=str(self.selected_product.price))
        ttk.Entry(form_frame, textvariable=price_var, width=30).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Discount
        ttk.Label(form_frame, text="Descuento (%):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        discount_var = tk.StringVar(value=str(self.selected_product.discount_percent))
        ttk.Entry(form_frame, textvariable=discount_var, width=30).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Discount dates frame
        discount_frame = ttk.LabelFrame(form_frame, text="Fechas de Descuento (Opcional)")
        discount_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Format dates for display
        start_date_str = ""
        if self.selected_product.discount_start_date:
            try:
                dt = datetime.fromisoformat(self.selected_product.discount_start_date)
                start_date_str = dt.strftime("%Y-%m-%d")
            except:
                pass
                
        end_date_str = ""
        if self.selected_product.discount_end_date:
            try:
                dt = datetime.fromisoformat(self.selected_product.discount_end_date)
                end_date_str = dt.strftime("%Y-%m-%d")
            except:
                pass
        
        # Start date
        ttk.Label(discount_frame, text="Fecha inicio:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        start_date_var = tk.StringVar(value=start_date_str)
        ttk.Entry(discount_frame, textvariable=start_date_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(discount_frame, text="(YYYY-MM-DD)").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # End date
        ttk.Label(discount_frame, text="Fecha fin:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        end_date_var = tk.StringVar(value=end_date_str)
        ttk.Entry(discount_frame, textvariable=end_date_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(discount_frame, text="(YYYY-MM-DD)").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Description
        ttk.Label(form_frame, text="Descripción:").grid(row=6, column=0, sticky=tk.NW, padx=5, pady=5)
        description_text = tk.Text(form_frame, width=30, height=5)
        description_text.grid(row=6, column=1, sticky=tk.W, padx=5, pady=5)
        description_text.insert("1.0", self.selected_product.description or "")
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Load categories for combobox
        try:
            categories = self.product_controller.get_all_categories()
            if categories:
                category_combo['values'] = [category.name for category in categories]
                
                # Set current category
                for i, category in enumerate(categories):
                    if category.id == self.selected_product.category_id:
                        category_combo.current(i)
                        break
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar categorías: {str(e)}")
        
        def save_product():
            # Validate inputs
            if not code_var.get().strip():
                messagebox.showerror("Error", "El código del producto es obligatorio")
                return
                
            if not name_var.get().strip():
                messagebox.showerror("Error", "El nombre del producto es obligatorio")
                return
                
            if not category_var.get().strip():
                messagebox.showerror("Error", "Debe seleccionar una categoría")
                return
                
            # Validate price
            try:
                price = float(price_var.get().strip())
                if price <= 0:
                    messagebox.showerror("Error", "El precio debe ser mayor que cero")
                    return
            except:
                messagebox.showerror("Error", "El precio debe ser un número válido")
                return
                
            # Validate discount
            try:
                discount = float(discount_var.get().strip())
                if discount < 0 or discount > 100:
                    messagebox.showerror("Error", "El descuento debe estar entre 0 y 100")
                    return
            except:
                messagebox.showerror("Error", "El descuento debe ser un número válido")
                return
                
            # Validate dates if provided
            start_date = None
            end_date = None
            
            if start_date_var.get().strip():
                try:
                    start_date = datetime.strptime(start_date_var.get().strip(), "%Y-%m-%d").isoformat()
                except:
                    messagebox.showerror("Error", "Formato de fecha de inicio inválido (debe ser YYYY-MM-DD)")
                    return
                    
            if end_date_var.get().strip():
                try:
                    end_date = datetime.strptime(end_date_var.get().strip(), "%Y-%m-%d").isoformat()
                except:
                    messagebox.showerror("Error", "Formato de fecha de fin inválido (debe ser YYYY-MM-DD)")
                    return
                    
            # Check if end date is after start date
            if start_date and end_date and start_date > end_date:
                messagebox.showerror("Error", "La fecha de fin debe ser posterior a la fecha de inicio")
                return
                
            # Get the category ID
            category_id = None
            for category in categories:
                if category.name == category_var.get():
                    category_id = category.id
                    break
                    
            if category_id is None:
                messagebox.showerror("Error", "Categoría no encontrada")
                return
                
            # Update product object
            self.selected_product.code = code_var.get().strip()
            self.selected_product.name = name_var.get().strip()
            self.selected_product.description = description_text.get("1.0", tk.END).strip()
            self.selected_product.category_id = category_id
            self.selected_product.price = price
            self.selected_product.discount_percent = discount
            self.selected_product.discount_start_date = start_date
            self.selected_product.discount_end_date = end_date
            
            try:
                # Update the product
                self.product_controller.update_product(self.selected_product)
                
                # Success
                messagebox.showinfo("Éxito", "Producto actualizado correctamente")
                
                # Refresh the products list
                self.load_products()
                
                # Update the product details
                self.update_product_details(self.selected_product)
                
                # Close the dialog
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar producto: {str(e)}")
        
        # Save and cancel buttons
        ttk.Button(buttons_frame, text="Guardar", command=save_product).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def delete_product(self):
        """
        Delete the selected product.
        """
        if not self.selected_product:
            messagebox.showinfo("Información", "Seleccione un producto para eliminar")
            return
            
        # Confirm deletion
        if not messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el producto '{self.selected_product.name}'?"):
            return
            
        try:
            # Delete the product
            self.product_controller.delete_product(self.selected_product.id)
            
            # Success
            messagebox.showinfo("Éxito", "Producto eliminado correctamente")
            
            # Refresh the products list
            self.load_products()
            
            # Clear the product details
            self.clear_product_details()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar producto: {str(e)}")
    
    def clear_product_details(self):
        """
        Clear the product details UI.
        """
        self.selected_product = None
        self.selected_variant = None
        
        self.product_code_var.set("")
        self.product_name_var.set("")
        self.product_category_var.set("")
        self.product_price_var.set("")
        self.product_discount_var.set("")
        self.product_final_price_var.set("")
        self.product_description_var.set("")
        
        # Clear variants treeview
        for item in self.variants_tree.get_children():
            self.variants_tree.delete(item)
    
    def show_add_variant_dialog(self):
        """
        Show dialog to add a variant to the selected product.
        """
        if not self.selected_product:
            messagebox.showinfo("Información", "Seleccione un producto para agregar variantes")
            return
            
        # Create a new dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Agregar Variante")
        dialog.geometry("300x150")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Variant form
        form_frame = ttk.Frame(dialog, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Size
        ttk.Label(form_frame, text="Talla:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        size_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=size_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Color
        ttk.Label(form_frame, text="Color:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        color_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=color_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Initial stock
        ttk.Label(form_frame, text="Stock Inicial:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        stock_var = tk.StringVar(value="0")
        ttk.Entry(form_frame, textvariable=stock_var, width=20).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_variant():
            # Validate inputs
            if not size_var.get().strip():
                messagebox.showerror("Error", "La talla es obligatoria")
                return
                
            if not color_var.get().strip():
                messagebox.showerror("Error", "El color es obligatorio")
                return
                
            # Validate stock
            try:
                stock = int(stock_var.get().strip())
                if stock < 0:
                    messagebox.showerror("Error", "El stock no puede ser negativo")
                    return
            except:
                messagebox.showerror("Error", "El stock debe ser un número entero")
                return
                
            # Create variant object
            variant = ProductVariant(
                product_id=self.selected_product.id,
                size=size_var.get().strip(),
                color=color_var.get().strip()
            )
            variant.inventory_quantity = stock
            
            try:
                # Add the variant
                variant_id = self.product_controller.add_variant(variant)
                
                # If there's initial stock, adjust it
                if stock > 0:
                    self.inventory_controller.adjust_inventory(
                        variant_id,
                        stock,
                        "Inventario inicial"
                    )
                
                # Success
                messagebox.showinfo("Éxito", "Variante agregada correctamente")
                
                # Refresh the variants list
                self.selected_product = self.product_controller.get_product(self.selected_product.id)
                self.load_product_variants(self.selected_product)
                
                # Close the dialog
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar variante: {str(e)}")
        
        # Save and cancel buttons
        ttk.Button(buttons_frame, text="Guardar", command=save_variant).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def show_edit_variant_dialog(self):
        """
        Show dialog to edit the selected variant.
        """
        if not self.selected_variant:
            messagebox.showinfo("Información", "Seleccione una variante para editar")
            return
            
        # Create a new dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Editar Variante")
        dialog.geometry("300x120")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Variant form
        form_frame = ttk.Frame(dialog, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Size
        ttk.Label(form_frame, text="Talla:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        size_var = tk.StringVar(value=self.selected_variant.size)
        ttk.Entry(form_frame, textvariable=size_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Color
        ttk.Label(form_frame, text="Color:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        color_var = tk.StringVar(value=self.selected_variant.color)
        ttk.Entry(form_frame, textvariable=color_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_variant():
            # Validate inputs
            if not size_var.get().strip():
                messagebox.showerror("Error", "La talla es obligatoria")
                return
                
            if not color_var.get().strip():
                messagebox.showerror("Error", "El color es obligatorio")
                return
                
            # Update variant object
            self.selected_variant.size = size_var.get().strip()
            self.selected_variant.color = color_var.get().strip()
            
            try:
                # Update the variant
                self.product_controller.update_variant(self.selected_variant)
                
                # Success
                messagebox.showinfo("Éxito", "Variante actualizada correctamente")
                
                # Refresh the variants list
                self.selected_product = self.product_controller.get_product(self.selected_product.id)
                self.load_product_variants(self.selected_product)
                
                # Close the dialog
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar variante: {str(e)}")
        
        # Save and cancel buttons
        ttk.Button(buttons_frame, text="Guardar", command=save_variant).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def delete_variant(self):
        """
        Delete the selected variant.
        """
        if not self.selected_variant:
            messagebox.showinfo("Información", "Seleccione una variante para eliminar")
            return
            
        # Confirm deletion
        if not messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la variante {self.selected_variant.color} - Talla {self.selected_variant.size}?"):
            return
            
        try:
            # Delete the variant
            self.product_controller.delete_variant(self.selected_variant.id)
            
            # Success
            messagebox.showinfo("Éxito", "Variante eliminada correctamente")
            
            # Refresh the variants list
            self.selected_product = self.product_controller.get_product(self.selected_product.id)
            self.load_product_variants(self.selected_product)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar variante: {str(e)}")
    
    def show_adjust_stock_dialog(self):
        """
        Show dialog to adjust the stock of the selected variant.
        """
        if not self.selected_variant:
            messagebox.showinfo("Información", "Seleccione una variante para ajustar el stock")
            return
            
        # Create a new dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Ajustar Stock")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Stock form
        form_frame = ttk.Frame(dialog, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Current stock
        ttk.Label(form_frame, text="Stock Actual:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(form_frame, text=str(self.selected_variant.inventory_quantity)).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Adjustment type
        ttk.Label(form_frame, text="Tipo de Ajuste:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        adjustment_type_var = tk.StringVar(value="add")
        ttk.Radiobutton(form_frame, text="Agregar", variable=adjustment_type_var, value="add").grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(form_frame, text="Quitar", variable=adjustment_type_var, value="remove").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Quantity
        ttk.Label(form_frame, text="Cantidad:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        quantity_var = tk.StringVar(value="1")
        ttk.Entry(form_frame, textvariable=quantity_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Notes
        ttk.Label(form_frame, text="Notas:").grid(row=3, column=0, sticky=tk.NW, padx=5, pady=5)
        notes_text = tk.Text(form_frame, width=30, height=3)
        notes_text.grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_adjustment():
            # Validate quantity
            try:
                quantity = int(quantity_var.get().strip())
                if quantity <= 0:
                    messagebox.showerror("Error", "La cantidad debe ser mayor que cero")
                    return
            except:
                messagebox.showerror("Error", "La cantidad debe ser un número entero")
                return
                
            # Calculate the actual change
            if adjustment_type_var.get() == "remove":
                quantity = -quantity
                
            if quantity < 0 and abs(quantity) > self.selected_variant.inventory_quantity:
                messagebox.showerror("Error", "No puede quitar más unidades que el stock disponible")
                return
                
            # Get notes
            notes = notes_text.get("1.0", tk.END).strip()
            
            try:
                # Adjust inventory
                self.inventory_controller.adjust_inventory(
                    self.selected_variant.id,
                    quantity,
                    notes
                )
                
                # Success
                messagebox.showinfo("Éxito", "Stock ajustado correctamente")
                
                # Refresh the variants list
                self.selected_product = self.product_controller.get_product(self.selected_product.id)
                self.load_product_variants(self.selected_product)
                
                # Close the dialog
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al ajustar stock: {str(e)}")
        
        # Save and cancel buttons
        ttk.Button(buttons_frame, text="Guardar", command=save_adjustment).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    # ======= Categories Tab Methods =======
    
    def load_categories(self):
        """
        Load categories from the database and display them in the treeview.
        """
        # Clear the treeview
        for item in self.categories_tree.get_children():
            self.categories_tree.delete(item)
            
        try:
            # Get all categories
            categories = self.product_controller.get_all_categories()
            
            # Insert into treeview
            for category in categories:
                self.categories_tree.insert(
                    "", 
                    "end", 
                    values=(
                        category.id, 
                        category.name
                    )
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar categorías: {str(e)}")
    
    def on_category_selected(self, event):
        """
        Handle category selection in the treeview.
        
        Args:
            event: Tkinter event
        """
        # Get the selected item
        selected_items = self.categories_tree.selection()
        if not selected_items:
            return
            
        # Get the first selected item
        item = selected_items[0]
        category_id = self.categories_tree.item(item, "values")[0]
        
        try:
            # Get all categories
            categories = self.product_controller.get_all_categories()
            
            # Find the selected category
            for category in categories:
                if category.id == int(category_id):
                    self.selected_category = category
                    break
                    
            if not self.selected_category:
                return
                
            # Update the category details UI
            self.update_category_details(self.selected_category)
            
            # Load products in this category
            self.load_category_products(self.selected_category.id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles de categoría: {str(e)}")
    
    def update_category_details(self, category):
        """
        Update the category details UI with the selected category information.
        
        Args:
            category: Category object
        """
        self.category_id_var.set(str(category.id))
        self.category_name_var.set(category.name)
        self.category_description_var.set(category.description or "Sin descripción")
    
    def load_category_products(self, category_id):
        """
        Load products in the selected category into the category products treeview.
        
        Args:
            category_id: ID of the category
        """
        # Clear the treeview
        for item in self.category_products_tree.get_children():
            self.category_products_tree.delete(item)
            
        try:
            # Get products in category
            products = self.product_controller.get_all_products(category_id=category_id)
            
            # Insert into treeview
            for product in products:
                self.category_products_tree.insert(
                    "", 
                    "end", 
                    values=(
                        product.id, 
                        product.code, 
                        product.name, 
                        f"${product.price:.2f}"
                    )
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar productos de la categoría: {str(e)}")
    
    def show_add_category_dialog(self):
        """
        Show dialog to add a new category.
        """
        # Create a new dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Agregar Nueva Categoría")
        dialog.geometry("400x200")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Category form
        form_frame = ttk.Frame(dialog, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Description
        ttk.Label(form_frame, text="Descripción:").grid(row=1, column=0, sticky=tk.NW, padx=5, pady=5)
        description_text = tk.Text(form_frame, width=30, height=5)
        description_text.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_category():
            # Validate name
            if not name_var.get().strip():
                messagebox.showerror("Error", "El nombre de la categoría es obligatorio")
                return
                
            # Create category object
            category = Category(
                name=name_var.get().strip(),
                description=description_text.get("1.0", tk.END).strip()
            )
            
            try:
                # Add the category
                category_id = self.product_controller.add_category(category)
                
                # Success
                messagebox.showinfo("Éxito", f"Categoría agregada con ID: {category_id}")
                
                # Refresh the categories list
                self.load_categories()
                
                # Close the dialog
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar categoría: {str(e)}")
        
        # Save and cancel buttons
        ttk.Button(buttons_frame, text="Guardar", command=save_category).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def show_edit_category_dialog(self):
        """
        Show dialog to edit the selected category.
        """
        if not self.selected_category:
            messagebox.showinfo("Información", "Seleccione una categoría para editar")
            return
            
        # Create a new dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Editar Categoría")
        dialog.geometry("400x200")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Category form
        form_frame = ttk.Frame(dialog, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar(value=self.selected_category.name)
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Description
        ttk.Label(form_frame, text="Descripción:").grid(row=1, column=0, sticky=tk.NW, padx=5, pady=5)
        description_text = tk.Text(form_frame, width=30, height=5)
        description_text.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        description_text.insert("1.0", self.selected_category.description or "")
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_category():
            # Validate name
            if not name_var.get().strip():
                messagebox.showerror("Error", "El nombre de la categoría es obligatorio")
                return
                
            # Update category object
            self.selected_category.name = name_var.get().strip()
            self.selected_category.description = description_text.get("1.0", tk.END).strip()
            
            try:
                # Update the category
                self.product_controller.update_category(self.selected_category)
                
                # Success
                messagebox.showinfo("Éxito", "Categoría actualizada correctamente")
                
                # Refresh the categories list
                self.load_categories()
                
                # Update the category details
                self.update_category_details(self.selected_category)
                
                # Close the dialog
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar categoría: {str(e)}")
        
        # Save and cancel buttons
        ttk.Button(buttons_frame, text="Guardar", command=save_category).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def delete_category(self):
        """
        Delete the selected category.
        """
        if not self.selected_category:
            messagebox.showinfo("Información", "Seleccione una categoría para eliminar")
            return
            
        # Confirm deletion
        if not messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la categoría '{self.selected_category.name}'?"):
            return
            
        try:
            # Delete the category
            self.product_controller.delete_category(self.selected_category.id)
            
            # Success
            messagebox.showinfo("Éxito", "Categoría eliminada correctamente")
            
            # Refresh the categories list
            self.load_categories()
            
            # Clear the category details
            self.clear_category_details()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar categoría: {str(e)}")
    
    def clear_category_details(self):
        """
        Clear the category details UI.
        """
        self.selected_category = None
        
        self.category_id_var.set("")
        self.category_name_var.set("")
        self.category_description_var.set("")
        
        # Clear category products treeview
        for item in self.category_products_tree.get_children():
            self.category_products_tree.delete(item)
