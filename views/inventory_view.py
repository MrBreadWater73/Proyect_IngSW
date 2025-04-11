"""
Inventory view for the Clothing Store Management System.
Manages the UI for inventory-related operations.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.inventory import InventoryTransaction
from utils.validation import validate_int


class InventoryView:
    """
    View for managing inventory operations and viewing inventory data.
    """
    
    def __init__(self, parent, inventory_controller, product_controller):
        """
        Initialize the inventory view.
        
        Args:
            parent: Parent widget
            inventory_controller: Inventory controller instance
            product_controller: Product controller instance
        """
        self.parent = parent
        self.inventory_controller = inventory_controller
        self.product_controller = product_controller
        
        # Selected items
        self.selected_product_variant = None
        
        # Setup UI components
        self.setup_ui()
        
        # Load initial data
        self.load_inventory_data()
        
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
        
        # Inventory status tab
        self.status_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.status_frame, text="Estado del Inventario")
        
        # Low stock tab
        self.low_stock_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.low_stock_frame, text="Stock Bajo")
        
        # Inventory transactions tab
        self.transactions_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.transactions_frame, text="Movimientos")
        
        # Setup each tab
        self.setup_status_tab()
        self.setup_low_stock_tab()
        self.setup_transactions_tab()
        
    def setup_status_tab(self):
        """
        Set up the Inventory Status tab UI.
        """
        # Main layout - split view
        self.status_pane = ttk.PanedWindow(self.status_frame, orient=tk.HORIZONTAL)
        self.status_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - category summary
        self.category_frame = ttk.LabelFrame(self.status_pane, text="Stock por Categoría")
        self.status_pane.add(self.category_frame, weight=40)
        
        # Category summary treeview
        self.category_tree = ttk.Treeview(
            self.category_frame,
            columns=("Categoría", "Productos", "Unidades"),
            show="headings"
        )
        self.category_tree.heading("Categoría", text="Categoría")
        self.category_tree.heading("Productos", text="Productos")
        self.category_tree.heading("Unidades", text="Unidades")
        
        self.category_tree.column("Categoría", width=150)
        self.category_tree.column("Productos", width=80, anchor=tk.CENTER)
        self.category_tree.column("Unidades", width=80, anchor=tk.CENTER)
        
        # Scrollbar for category tree
        category_scrollbar = ttk.Scrollbar(self.category_frame, orient="vertical", command=self.category_tree.yview)
        self.category_tree.configure(yscrollcommand=category_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.category_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        category_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Button to refresh
        self.category_buttons_frame = ttk.Frame(self.category_frame)
        self.category_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(self.category_buttons_frame, text="Actualizar", command=self.load_inventory_data).pack(side=tk.RIGHT, padx=5)
        
        # Right panel - product inventory
        self.inventory_frame = ttk.LabelFrame(self.status_pane, text="Inventario de Productos")
        self.status_pane.add(self.inventory_frame, weight=60)
        
        # Search frame
        self.search_frame = ttk.Frame(self.inventory_frame)
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.search_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(self.search_frame, text="Buscar", command=self.search_products).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.search_frame, text="Limpiar", command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        # Products inventory treeview
        self.inventory_tree = ttk.Treeview(
            self.inventory_frame,
            columns=("ID", "Código", "Producto", "Variante", "Stock"),
            show="headings"
        )
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Código", text="Código")
        self.inventory_tree.heading("Producto", text="Producto")
        self.inventory_tree.heading("Variante", text="Variante")
        self.inventory_tree.heading("Stock", text="Stock")
        
        self.inventory_tree.column("ID", width=50, anchor=tk.CENTER)
        self.inventory_tree.column("Código", width=80)
        self.inventory_tree.column("Producto", width=150)
        self.inventory_tree.column("Variante", width=150)
        self.inventory_tree.column("Stock", width=80, anchor=tk.CENTER)
        
        # Scrollbar for inventory tree
        inventory_scrollbar = ttk.Scrollbar(self.inventory_frame, orient="vertical", command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=inventory_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.inventory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        inventory_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Bind selection event
        self.inventory_tree.bind("<<TreeviewSelect>>", self.on_inventory_item_selected)
        
        # Actions frame
        self.inventory_actions_frame = ttk.Frame(self.inventory_frame)
        self.inventory_actions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(self.inventory_actions_frame, text="Ajustar Stock", command=self.show_adjust_stock_dialog).pack(side=tk.LEFT, padx=5)
        
    def setup_low_stock_tab(self):
        """
        Set up the Low Stock tab UI.
        """
        # Layout
        self.low_stock_container = ttk.Frame(self.low_stock_frame)
        self.low_stock_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Low stock settings
        self.settings_frame = ttk.Frame(self.low_stock_container)
        self.settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.settings_frame, text="Umbral de Stock Bajo:").pack(side=tk.LEFT, padx=5)
        
        self.threshold_var = tk.StringVar(value="5")
        threshold_entry = ttk.Entry(self.settings_frame, textvariable=self.threshold_var, width=5)
        threshold_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.settings_frame, text="Aplicar", command=self.refresh_low_stock).pack(side=tk.LEFT, padx=5)
        
        # Show out of stock checkbox
        self.show_out_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.settings_frame, 
            text="Mostrar Sin Stock", 
            variable=self.show_out_var,
            command=self.refresh_low_stock
        ).pack(side=tk.LEFT, padx=20)
        
        # Low stock treeview
        self.low_stock_tree = ttk.Treeview(
            self.low_stock_container,
            columns=("ID", "Código", "Producto", "Variante", "Stock", "Estado"),
            show="headings"
        )
        self.low_stock_tree.heading("ID", text="ID")
        self.low_stock_tree.heading("Código", text="Código")
        self.low_stock_tree.heading("Producto", text="Producto")
        self.low_stock_tree.heading("Variante", text="Variante")
        self.low_stock_tree.heading("Stock", text="Stock")
        self.low_stock_tree.heading("Estado", text="Estado")
        
        self.low_stock_tree.column("ID", width=50, anchor=tk.CENTER)
        self.low_stock_tree.column("Código", width=80)
        self.low_stock_tree.column("Producto", width=150)
        self.low_stock_tree.column("Variante", width=150)
        self.low_stock_tree.column("Stock", width=80, anchor=tk.CENTER)
        self.low_stock_tree.column("Estado", width=100)
        
        # Scrollbar for low stock tree
        low_stock_scrollbar = ttk.Scrollbar(self.low_stock_container, orient="vertical", command=self.low_stock_tree.yview)
        self.low_stock_tree.configure(yscrollcommand=low_stock_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.low_stock_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        low_stock_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Bind selection event
        self.low_stock_tree.bind("<<TreeviewSelect>>", self.on_low_stock_item_selected)
        
        # Actions frame
        self.low_stock_actions_frame = ttk.Frame(self.low_stock_frame)
        self.low_stock_actions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(self.low_stock_actions_frame, text="Ajustar Stock", command=self.show_adjust_stock_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.low_stock_actions_frame, text="Actualizar", command=self.refresh_low_stock).pack(side=tk.RIGHT, padx=5)
        
    def setup_transactions_tab(self):
        """
        Set up the Inventory Transactions tab UI.
        """
        # Main layout
        self.transactions_container = ttk.Frame(self.transactions_frame)
        self.transactions_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Filter frame
        self.filter_frame = ttk.LabelFrame(self.transactions_container, text="Filtros")
        self.filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Filter grid
        filter_grid = ttk.Frame(self.filter_frame)
        filter_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Transaction type filter
        ttk.Label(filter_grid, text="Tipo:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.transaction_type_var = tk.StringVar(value="TODOS")
        type_combo = ttk.Combobox(filter_grid, textvariable=self.transaction_type_var, width=15)
        type_combo['values'] = ["TODOS", "VENTA", "COMPRA", "AJUSTE", "DEVOLUCIÓN"]
        type_combo.current(0)
        type_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Date range
        ttk.Label(filter_grid, text="Desde:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        ttk.Entry(filter_grid, textvariable=self.start_date_var, width=12).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(filter_grid, text="Hasta:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=2)
        self.end_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(filter_grid, textvariable=self.end_date_var, width=12).grid(row=0, column=5, sticky=tk.W, padx=5, pady=2)
        
        # Apply filter button
        ttk.Button(filter_grid, text="Aplicar Filtros", command=self.apply_transaction_filters).grid(row=0, column=6, sticky=tk.W, padx=5, pady=2)
        
        # Transactions treeview
        self.transactions_tree = ttk.Treeview(
            self.transactions_container,
            columns=("ID", "Fecha", "Producto", "Variante", "Cambio", "Tipo", "Referencia", "Notas"),
            show="headings"
        )
        self.transactions_tree.heading("ID", text="ID")
        self.transactions_tree.heading("Fecha", text="Fecha")
        self.transactions_tree.heading("Producto", text="Producto")
        self.transactions_tree.heading("Variante", text="Variante")
        self.transactions_tree.heading("Cambio", text="Cambio")
        self.transactions_tree.heading("Tipo", text="Tipo")
        self.transactions_tree.heading("Referencia", text="Referencia")
        self.transactions_tree.heading("Notas", text="Notas")
        
        self.transactions_tree.column("ID", width=50, anchor=tk.CENTER)
        self.transactions_tree.column("Fecha", width=120)
        self.transactions_tree.column("Producto", width=150)
        self.transactions_tree.column("Variante", width=150)
        self.transactions_tree.column("Cambio", width=80, anchor=tk.CENTER)
        self.transactions_tree.column("Tipo", width=100)
        self.transactions_tree.column("Referencia", width=100, anchor=tk.CENTER)
        self.transactions_tree.column("Notas", width=200)
        
        # Scrollbar for transactions tree
        transactions_scrollbar = ttk.Scrollbar(self.transactions_container, orient="vertical", command=self.transactions_tree.yview)
        self.transactions_tree.configure(yscrollcommand=transactions_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.transactions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        transactions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
    def load_inventory_data(self):
        """
        Load inventory data into all tabs.
        """
        self.load_categories_stock()
        self.load_inventory_products()
        self.refresh_low_stock()
        self.load_inventory_transactions()
        
    def load_categories_stock(self):
        """
        Load category stock summary into the category treeview.
        """
        # Clear the treeview
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
            
        try:
            # Get stock by category
            stock_data = self.inventory_controller.get_stock_by_category()
            
            # Insert into treeview
            for data in stock_data:
                category_name = data[0]
                item_count = data[1]
                total_stock = data[2]
                
                self.category_tree.insert(
                    "", 
                    "end", 
                    values=(
                        category_name,
                        item_count,
                        total_stock
                    )
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar stock por categorías: {str(e)}")
            
    def load_inventory_products(self):
        """
        Load product inventory into the inventory treeview.
        """
        # Clear the treeview
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
            
        try:
            # Get all products with variants
            products = self.product_controller.get_all_products(include_variants=True)
            
            # Insert into treeview
            for product in products:
                for variant in product.variants:
                    self.inventory_tree.insert(
                        "", 
                        "end", 
                        values=(
                            variant.id,
                            product.code,
                            product.name,
                            f"{variant.color} - Talla {variant.size}",
                            variant.inventory_quantity
                        )
                    )
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar inventario de productos: {str(e)}")
            
    def refresh_low_stock(self):
        """
        Refresh the low stock tab with current data.
        """
        # Clear the treeview
        for item in self.low_stock_tree.get_children():
            self.low_stock_tree.delete(item)
            
        try:
            # Get threshold value
            try:
                threshold = int(self.threshold_var.get())
                if threshold < 1:
                    threshold = 1
            except:
                threshold = 5
                self.threshold_var.set("5")
            
            # Get low stock items
            low_stock_items = self.inventory_controller.get_low_stock_items(threshold)
            
            # Insert low stock items into treeview
            for item in low_stock_items:
                product_id, product_code, product_name, variant_id, variant_size, variant_color, quantity = item
                
                self.low_stock_tree.insert(
                    "", 
                    "end", 
                    values=(
                        variant_id,
                        product_code,
                        product_name,
                        f"{variant_color} - Talla {variant_size}",
                        quantity,
                        "Stock Bajo"
                    ),
                    tags=("low",)
                )
            
            # Get out of stock items if checkbox is checked
            if self.show_out_var.get():
                out_of_stock_items = self.inventory_controller.get_out_of_stock_items()
                
                # Insert out of stock items into treeview
                for item in out_of_stock_items:
                    product_id, product_code, product_name, variant_id, variant_size, variant_color, quantity = item
                    
                    self.low_stock_tree.insert(
                        "", 
                        "end", 
                        values=(
                            variant_id,
                            product_code,
                            product_name,
                            f"{variant_color} - Talla {variant_size}",
                            quantity,
                            "Sin Stock"
                        ),
                        tags=("out",)
                    )
                    
            # Configure tag appearance
            self.low_stock_tree.tag_configure("low", background="#ffffa0")  # Light yellow for low stock
            self.low_stock_tree.tag_configure("out", background="#ffcccc")  # Light red for out of stock
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar productos con stock bajo: {str(e)}")
            
    def load_inventory_transactions(self):
        """
        Load inventory transactions into the transactions treeview.
        """
        # Clear the treeview
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
            
        try:
            # Get current filter values
            transaction_type = None if self.transaction_type_var.get() == "TODOS" else self.transaction_type_var.get()
            
            start_date = None
            if self.start_date_var.get():
                try:
                    start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d").isoformat()
                except:
                    pass
                    
            end_date = None
            if self.end_date_var.get():
                try:
                    end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d").isoformat()
                    # Set to end of day
                    end_date = datetime.fromisoformat(end_date).replace(hour=23, minute=59, second=59).isoformat()
                except:
                    pass
            
            # Get transactions with filters
            transactions = self.inventory_controller.get_inventory_transactions(
                transaction_type=transaction_type,
                start_date=start_date,
                end_date=end_date,
                limit=200  # Increase limit
            )
            
            # Insert into treeview
            for tx in transactions:
                # Format transaction date
                date_display = datetime.fromisoformat(tx.transaction_date).strftime("%Y-%m-%d %H:%M")
                
                # Format transaction type
                type_display = {
                    "SALE": "VENTA",
                    "PURCHASE": "COMPRA",
                    "ADJUSTMENT": "AJUSTE",
                    "RETURN": "DEVOLUCIÓN"
                }.get(tx.transaction_type, tx.transaction_type)
                
                # Format reference
                reference_display = f"#{tx.reference_id}" if tx.reference_id else ""
                
                # Tag based on transaction type
                tag = tx.transaction_type.lower()
                
                # Insert the transaction
                self.transactions_tree.insert(
                    "", 
                    "end", 
                    values=(
                        tx.id,
                        date_display,
                        tx.product_name,
                        f"{tx.color} - Talla {tx.size}",
                        tx.quantity_change,
                        type_display,
                        reference_display,
                        tx.notes or ""
                    ),
                    tags=(tag,)
                )
                
            # Configure tag appearance
            self.transactions_tree.tag_configure("sale", foreground="#cc0000")  # Red for sales
            self.transactions_tree.tag_configure("purchase", foreground="#009900")  # Green for purchases
            self.transactions_tree.tag_configure("adjustment", foreground="#0000cc")  # Blue for adjustments
            self.transactions_tree.tag_configure("return", foreground="#cc9900")  # Orange for returns
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar movimientos de inventario: {str(e)}")
            
    def search_products(self):
        """
        Search for products in the inventory.
        """
        search_term = self.search_var.get().strip()
        
        if not search_term:
            messagebox.showinfo("Información", "Ingrese un término de búsqueda")
            return
            
        # Clear the treeview
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
            
        try:
            # Get all products with variants
            products = self.product_controller.search_products(search_term)
            
            # Get full product details for each result
            results = []
            for product in products:
                full_product = self.product_controller.get_product(product.id)
                if full_product:
                    results.append(full_product)
            
            # Insert matching products into treeview
            for product in results:
                for variant in product.variants:
                    self.inventory_tree.insert(
                        "", 
                        "end", 
                        values=(
                            variant.id,
                            product.code,
                            product.name,
                            f"{variant.color} - Talla {variant.size}",
                            variant.inventory_quantity
                        )
                    )
                    
            if not results:
                messagebox.showinfo("Información", "No se encontraron productos con ese término de búsqueda")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar productos: {str(e)}")
            
    def clear_search(self):
        """
        Clear the search field and refresh the inventory display.
        """
        self.search_var.set("")
        self.load_inventory_products()
        
    def apply_transaction_filters(self):
        """
        Apply filters to the inventory transactions display.
        """
        # Validate dates if provided
        if self.start_date_var.get().strip():
            try:
                datetime.strptime(self.start_date_var.get().strip(), "%Y-%m-%d")
            except:
                messagebox.showerror("Error", "Formato de fecha de inicio inválido (debe ser YYYY-MM-DD)")
                return
                
        if self.end_date_var.get().strip():
            try:
                datetime.strptime(self.end_date_var.get().strip(), "%Y-%m-%d")
            except:
                messagebox.showerror("Error", "Formato de fecha de fin inválido (debe ser YYYY-MM-DD)")
                return
                
        # Check if end date is after start date
        if self.start_date_var.get().strip() and self.end_date_var.get().strip():
            start_date = datetime.strptime(self.start_date_var.get().strip(), "%Y-%m-%d")
            end_date = datetime.strptime(self.end_date_var.get().strip(), "%Y-%m-%d")
            
            if start_date > end_date:
                messagebox.showerror("Error", "La fecha de fin debe ser posterior a la fecha de inicio")
                return
        
        # Refresh the transactions display with the new filters
        self.load_inventory_transactions()
        
    def on_inventory_item_selected(self, event):
        """
        Handle inventory item selection.
        
        Args:
            event: Tkinter event
        """
        # Get the selected item
        selected_items = self.inventory_tree.selection()
        if not selected_items:
            self.selected_product_variant = None
            return
            
        # Get the first selected item
        item = selected_items[0]
        variant_id = self.inventory_tree.item(item, "values")[0]
        
        # Store the selected variant ID
        self.selected_product_variant = variant_id
        
    def on_low_stock_item_selected(self, event):
        """
        Handle low stock item selection.
        
        Args:
            event: Tkinter event
        """
        # Get the selected item
        selected_items = self.low_stock_tree.selection()
        if not selected_items:
            self.selected_product_variant = None
            return
            
        # Get the first selected item
        item = selected_items[0]
        variant_id = self.low_stock_tree.item(item, "values")[0]
        
        # Store the selected variant ID
        self.selected_product_variant = variant_id
        
    def show_adjust_stock_dialog(self):
        """
        Show dialog to adjust stock of the selected product variant.
        """
        if not self.selected_product_variant:
            messagebox.showinfo("Información", "Seleccione un producto para ajustar su stock")
            return
            
        # Get the variant ID
        variant_id = self.selected_product_variant
        
        # Get the current product and variant details
        variant_info = None
        product_name = ""
        current_stock = 0
        
        # Find the variant in all products
        products = self.product_controller.get_all_products(include_variants=True)
        for product in products:
            for variant in product.variants:
                if variant.id == int(variant_id):
                    variant_info = variant
                    product_name = product.name
                    current_stock = variant.inventory_quantity
                    break
            if variant_info:
                break
                
        if not variant_info:
            messagebox.showerror("Error", "No se encontró la variante seleccionada")
            return
            
        # Create a new dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Ajustar Stock")
        dialog.geometry("400x250")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Stock form
        form_frame = ttk.Frame(dialog, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Product info
        ttk.Label(form_frame, text="Producto:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(form_frame, text=product_name).grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Variante:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(form_frame, text=f"{variant_info.color} - Talla {variant_info.size}").grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Current stock
        ttk.Label(form_frame, text="Stock Actual:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(form_frame, text=str(current_stock)).grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Adjustment type
        ttk.Label(form_frame, text="Tipo de Ajuste:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        adjustment_type_var = tk.StringVar(value="add")
        ttk.Radiobutton(form_frame, text="Agregar", variable=adjustment_type_var, value="add").grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(form_frame, text="Quitar", variable=adjustment_type_var, value="remove").grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Quantity
        ttk.Label(form_frame, text="Cantidad:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        quantity_var = tk.StringVar(value="1")
        quantity_entry = ttk.Entry(form_frame, textvariable=quantity_var, width=10)
        quantity_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Set focus to quantity entry
        quantity_entry.focus_set()
        
        # Notes
        ttk.Label(form_frame, text="Notas:").grid(row=5, column=0, sticky=tk.NW, padx=5, pady=5)
        notes_text = tk.Text(form_frame, width=30, height=3)
        notes_text.grid(row=5, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
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
                
            if quantity < 0 and abs(quantity) > current_stock:
                messagebox.showerror("Error", "No puede quitar más unidades que el stock disponible")
                return
                
            # Get notes
            notes = notes_text.get("1.0", tk.END).strip()
            
            try:
                # Adjust inventory
                self.inventory_controller.adjust_inventory(
                    variant_id,
                    quantity,
                    notes
                )
                
                # Success
                messagebox.showinfo("Éxito", "Stock ajustado correctamente")
                
                # Refresh inventory data
                self.load_inventory_data()
                
                # Close the dialog
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al ajustar stock: {str(e)}")
        
        # Save and cancel buttons
        ttk.Button(buttons_frame, text="Guardar", command=save_adjustment).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
