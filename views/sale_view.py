"""
Sale view for the Clothing Store Management System.
Manages the UI for sale-related operations.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.sale import Sale, SaleItem
from utils.validation import validate_float, validate_int


class SaleView:
    """
    View for managing sales and transactions.
    """
    
    def __init__(self, parent, sale_controller, product_controller, customer_controller):
        """
        Initialize the sale view.
        
        Args:
            parent: Parent widget
            sale_controller: Sale controller instance
            product_controller: Product controller instance
            customer_controller: Customer controller instance
        """
        self.parent = parent
        self.sale_controller = sale_controller
        self.product_controller = product_controller
        self.customer_controller = customer_controller
        
        # Selected sale
        self.selected_sale = None
        
        # Current sale in progress
        self.current_sale = None
        self.current_sale_items = []
        
        # Setup UI components
        self.setup_ui()
        
        # Load initial data
        self.load_sales()
        
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
        
        # New sale tab
        self.new_sale_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.new_sale_frame, text="Nueva Venta")
        
        # Sales history tab
        self.sales_history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sales_history_frame, text="Historial de Ventas")
        
        # Setup each tab
        self.setup_new_sale_tab()
        self.setup_sales_history_tab()
        
    def setup_new_sale_tab(self):
        """
        Set up the New Sale tab UI.
        """
        # Main layout - split view
        self.new_sale_pane = ttk.PanedWindow(self.new_sale_frame, orient=tk.HORIZONTAL)
        self.new_sale_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - products
        self.products_frame = ttk.Frame(self.new_sale_pane)
        self.new_sale_pane.add(self.products_frame, weight=50)
        
        # Product search frame
        self.product_search_frame = ttk.LabelFrame(self.products_frame, text="Buscar Productos")
        self.product_search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Product search grid
        search_grid = ttk.Frame(self.product_search_frame)
        search_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Row 0 - Search bar
        ttk.Label(search_grid, text="Buscar:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.product_search_var = tk.StringVar()
        product_search_entry = ttk.Entry(search_grid, textvariable=self.product_search_var, width=20)
        product_search_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
        product_search_entry.bind("<Return>", lambda e: self.search_products())
        
        ttk.Button(search_grid, text="Buscar", command=self.search_products).grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        
        # Row 1 - Category filter
        ttk.Label(search_grid, text="Categoría:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.category_filter_var = tk.StringVar()
        self.category_combo = ttk.Combobox(search_grid, textvariable=self.category_filter_var, width=20)
        self.category_combo.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_products_by_category())
        
        ttk.Button(search_grid, text="Todos", command=self.clear_product_filters).grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        
        # Configure grid columns
        search_grid.columnconfigure(1, weight=1)
        
        # Products list frame
        self.products_list_frame = ttk.LabelFrame(self.products_frame, text="Productos")
        self.products_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Products treeview
        self.products_tree = ttk.Treeview(
            self.products_list_frame,
            columns=("ID", "Código", "Nombre", "Precio", "Descuento", "Stock"),
            show="headings"
        )
        self.products_tree.heading("ID", text="ID")
        self.products_tree.heading("Código", text="Código")
        self.products_tree.heading("Nombre", text="Nombre")
        self.products_tree.heading("Precio", text="Precio")
        self.products_tree.heading("Descuento", text="Descuento")
        self.products_tree.heading("Stock", text="Stock")
        
        self.products_tree.column("ID", width=50, anchor=tk.CENTER)
        self.products_tree.column("Código", width=80)
        self.products_tree.column("Nombre", width=150)
        self.products_tree.column("Precio", width=80, anchor=tk.E)
        self.products_tree.column("Descuento", width=80, anchor=tk.E)
        self.products_tree.column("Stock", width=60, anchor=tk.CENTER)
        
        # Scrollbar for products tree
        products_scrollbar = ttk.Scrollbar(self.products_list_frame, orient="vertical", command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=products_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        products_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Bind double click to add product
        self.products_tree.bind("<Double-1>", self.on_product_double_click)
        
        # Add product button
        self.product_buttons_frame = ttk.Frame(self.products_frame)
        self.product_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            self.product_buttons_frame, 
            text="Agregar Producto", 
            command=self.show_add_product_to_sale_dialog
        ).pack(side=tk.LEFT, padx=5)
        
        # Right panel - current sale
        self.current_sale_frame = ttk.Frame(self.new_sale_pane)
        self.new_sale_pane.add(self.current_sale_frame, weight=50)
        
        # Customer frame
        self.customer_frame = ttk.LabelFrame(self.current_sale_frame, text="Cliente")
        self.customer_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Customer grid
        customer_grid = ttk.Frame(self.customer_frame)
        customer_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Row 0 - Customer search
        ttk.Label(customer_grid, text="Buscar Cliente:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.customer_search_var = tk.StringVar()
        customer_search_entry = ttk.Entry(customer_grid, textvariable=self.customer_search_var, width=20)
        customer_search_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
        customer_search_entry.bind("<Return>", lambda e: self.search_customers())
        
        ttk.Button(customer_grid, text="Buscar", command=self.search_customers).grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        
        # Row 1 - Selected customer
        ttk.Label(customer_grid, text="Cliente Seleccionado:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.selected_customer_var = tk.StringVar(value="Cliente no registrado")
        ttk.Label(customer_grid, textvariable=self.selected_customer_var).grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=2)
        
        # Configure grid columns
        customer_grid.columnconfigure(1, weight=1)
        
        # Sale items frame
        self.sale_items_frame = ttk.LabelFrame(self.current_sale_frame, text="Productos en esta Venta")
        self.sale_items_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sale items treeview
        self.sale_items_tree = ttk.Treeview(
            self.sale_items_frame,
            columns=("Producto", "Variante", "Cantidad", "Precio", "Descuento", "Subtotal"),
            show="headings"
        )
        self.sale_items_tree.heading("Producto", text="Producto")
        self.sale_items_tree.heading("Variante", text="Variante")
        self.sale_items_tree.heading("Cantidad", text="Cantidad")
        self.sale_items_tree.heading("Precio", text="Precio")
        self.sale_items_tree.heading("Descuento", text="Descuento")
        self.sale_items_tree.heading("Subtotal", text="Subtotal")
        
        self.sale_items_tree.column("Producto", width=120)
        self.sale_items_tree.column("Variante", width=120)
        self.sale_items_tree.column("Cantidad", width=60, anchor=tk.CENTER)
        self.sale_items_tree.column("Precio", width=80, anchor=tk.E)
        self.sale_items_tree.column("Descuento", width=80, anchor=tk.E)
        self.sale_items_tree.column("Subtotal", width=80, anchor=tk.E)
        
        # Scrollbar for sale items tree
        sale_items_scrollbar = ttk.Scrollbar(self.sale_items_frame, orient="vertical", command=self.sale_items_tree.yview)
        self.sale_items_tree.configure(yscrollcommand=sale_items_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.sale_items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        sale_items_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Sale items buttons
        self.sale_items_buttons_frame = ttk.Frame(self.current_sale_frame)
        self.sale_items_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            self.sale_items_buttons_frame, 
            text="Editar Cantidad", 
            command=self.edit_sale_item_quantity
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            self.sale_items_buttons_frame, 
            text="Eliminar Producto", 
            command=self.remove_sale_item
        ).pack(side=tk.LEFT, padx=5)
        
        # Sale totals frame
        self.sale_totals_frame = ttk.LabelFrame(self.current_sale_frame, text="Totales")
        self.sale_totals_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Totals grid
        totals_grid = ttk.Frame(self.sale_totals_frame)
        totals_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Row 0 - Total items
        ttk.Label(totals_grid, text="Total Productos:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.total_items_var = tk.StringVar(value="0")
        ttk.Label(totals_grid, textvariable=self.total_items_var).grid(row=0, column=1, sticky=tk.E, padx=5, pady=2)
        
        # Row 1 - Total amount
        ttk.Label(totals_grid, text="Total a Pagar:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.total_amount_var = tk.StringVar(value="$0.00")
        ttk.Label(
            totals_grid, 
            textvariable=self.total_amount_var, 
            font=("Arial", 12, "bold")
        ).grid(row=1, column=1, sticky=tk.E, padx=5, pady=2)
        
        # Configure grid columns
        totals_grid.columnconfigure(1, weight=1)
        
        # Payment method frame
        self.payment_frame = ttk.LabelFrame(self.current_sale_frame, text="Método de Pago")
        self.payment_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Payment method options
        payment_methods = [("Efectivo", "EFECTIVO"), ("Tarjeta", "TARJETA"), ("Transferencia", "TRANSFERENCIA")]
        
        self.payment_method_var = tk.StringVar(value="EFECTIVO")
        payment_frame_inner = ttk.Frame(self.payment_frame)
        payment_frame_inner.pack(padx=10, pady=10)
        
        for text, value in payment_methods:
            ttk.Radiobutton(
                payment_frame_inner, 
                text=text, 
                variable=self.payment_method_var, 
                value=value
            ).pack(side=tk.LEFT, padx=10)
        
        # Finalize sale buttons
        self.finalize_buttons_frame = ttk.Frame(self.current_sale_frame)
        self.finalize_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            self.finalize_buttons_frame, 
            text="Finalizar Venta", 
            command=self.finalize_sale,
            style="Accent.TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            self.finalize_buttons_frame, 
            text="Cancelar Venta", 
            command=self.cancel_current_sale
        ).pack(side=tk.RIGHT, padx=5)
        
        # Create custom style for the finalize button
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))
        
        # Initialize a new sale
        self.start_new_sale()
        
    def setup_sales_history_tab(self):
        """
        Set up the Sales History tab UI.
        """
        # Main layout - split view
        self.history_pane = ttk.PanedWindow(self.sales_history_frame, orient=tk.VERTICAL)
        self.history_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Filter frame
        self.filter_frame = ttk.LabelFrame(self.history_pane, text="Filtros")
        self.history_pane.add(self.filter_frame, weight=20)
        
        # Filter grid
        filter_grid = ttk.Frame(self.filter_frame)
        filter_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Row 0 - Date range
        ttk.Label(filter_grid, text="Desde:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.start_date_var = tk.StringVar()
        
        # Set default to 30 days ago
        start_date = (datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        self.start_date_var.set(start_date)
        
        ttk.Entry(filter_grid, textvariable=self.start_date_var, width=12).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(filter_grid, text="Hasta:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.end_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(filter_grid, textvariable=self.end_date_var, width=12).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        ttk.Button(filter_grid, text="Aplicar Filtros", command=self.apply_sales_filters).grid(row=0, column=4, sticky=tk.W, padx=5, pady=2)
        ttk.Button(filter_grid, text="Limpiar Filtros", command=self.clear_sales_filters).grid(row=0, column=5, sticky=tk.W, padx=5, pady=2)
        
        # Sales list frame
        self.sales_list_frame = ttk.LabelFrame(self.history_pane, text="Historial de Ventas")
        self.history_pane.add(self.sales_list_frame, weight=80)
        
        # Sales treeview
        self.sales_tree = ttk.Treeview(
            self.sales_list_frame,
            columns=("ID", "Fecha", "Cliente", "Método de Pago", "Total"),
            show="headings"
        )
        self.sales_tree.heading("ID", text="ID")
        self.sales_tree.heading("Fecha", text="Fecha")
        self.sales_tree.heading("Cliente", text="Cliente")
        self.sales_tree.heading("Método de Pago", text="Método de Pago")
        self.sales_tree.heading("Total", text="Total")
        
        self.sales_tree.column("ID", width=50, anchor=tk.CENTER)
        self.sales_tree.column("Fecha", width=150)
        self.sales_tree.column("Cliente", width=200)
        self.sales_tree.column("Método de Pago", width=120)
        self.sales_tree.column("Total", width=100, anchor=tk.E)
        
        # Scrollbar for sales tree
        sales_scrollbar = ttk.Scrollbar(self.sales_list_frame, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=sales_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.sales_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        sales_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Bind double click to view sale details
        self.sales_tree.bind("<Double-1>", self.on_sale_double_click)
        
        # Actions frame
        self.actions_frame = ttk.Frame(self.sales_history_frame)
        self.actions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            self.actions_frame, 
            text="Ver Detalles", 
            command=self.show_sale_details
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            self.actions_frame, 
            text="Cancelar Venta", 
            command=self.cancel_sale
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            self.actions_frame, 
            text="Actualizar", 
            command=self.load_sales
        ).pack(side=tk.RIGHT, padx=5)
        
        # Load categories for filter
        self.load_categories()
        
        # Load products
        self.load_products()
    
    def load_sales(self):
        """
        Load sales from the database based on current filters.
        """
        # Clear the treeview
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
            
        try:
            # Get filter values
            start_date = None
            end_date = None
            
            if self.start_date_var.get().strip():
                try:
                    start_date = datetime.strptime(self.start_date_var.get().strip(), "%Y-%m-%d").isoformat()
                except:
                    pass
                    
            if self.end_date_var.get().strip():
                try:
                    # Set to end of day
                    end_date = datetime.strptime(self.end_date_var.get().strip(), "%Y-%m-%d")
                    end_date = end_date.replace(hour=23, minute=59, second=59).isoformat()
                except:
                    pass
            
            # Get all sales with filters
            sales = self.sale_controller.get_all_sales(start_date, end_date)
            
            # Insert into treeview
            for sale in sales:
                # Format the date
                sale_date = sale.sale_date
                try:
                    dt = datetime.fromisoformat(sale_date)
                    sale_date = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
                    
                # Format payment method
                payment_method = sale.payment_method
                if payment_method == "EFECTIVO":
                    payment_method = "Efectivo"
                elif payment_method == "TARJETA":
                    payment_method = "Tarjeta"
                elif payment_method == "TRANSFERENCIA":
                    payment_method = "Transferencia"
                
                self.sales_tree.insert(
                    "", 
                    "end", 
                    values=(
                        sale.id,
                        sale_date,
                        sale.customer_name,
                        payment_method,
                        f"${sale.total_amount:.2f}"
                    )
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar ventas: {str(e)}")
    
    def load_categories(self):
        """
        Load categories for the filter combobox.
        """
        try:
            # Get all categories
            categories = self.product_controller.get_all_categories()
            
            # Clear the combo
            self.category_combo['values'] = []
            
            # Add "All" option
            values = ["Todas las categorías"]
            
            # Add categories to the list
            for category in categories:
                values.append(category.name)
                
            # Set values
            self.category_combo['values'] = values
            
            # Select "All" by default
            self.category_combo.current(0)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar categorías: {str(e)}")
    
    def load_products(self, category_id=None, search_term=None):
        """
        Load products into the products treeview.
        
        Args:
            category_id: Optional category ID to filter by
            search_term: Optional search term to filter by
        """
        # Clear the treeview
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
            
        try:
            products = []
            
            # Get products with filters
            if search_term:
                products = self.product_controller.search_products(search_term)
            elif category_id:
                products = self.product_controller.get_all_products(category_id=category_id, include_variants=True)
            else:
                products = self.product_controller.get_all_products(include_variants=True)
            
            # Insert into treeview
            for product in products:
                # Calculate current price
                current_price = product.get_current_price()
                
                # Format discount
                discount_text = f"{product.discount_percent}%" if product.discount_percent > 0 else ""
                if product.discount_percent > 0 and not product.is_discount_active():
                    discount_text += " (Inactivo)"
                
                # Calculate total stock across all variants
                total_stock = sum(variant.inventory_quantity for variant in product.variants)
                
                # Insert product
                self.products_tree.insert(
                    "", 
                    "end", 
                    values=(
                        product.id,
                        product.code,
                        product.name,
                        f"${current_price:.2f}",
                        discount_text,
                        total_stock
                    )
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar productos: {str(e)}")
    
    def search_products(self):
        """
        Search for products by the entered search term.
        """
        search_term = self.product_search_var.get().strip()
        
        if not search_term:
            messagebox.showinfo("Información", "Ingrese un término de búsqueda")
            return
            
        # Load products with search term
        self.load_products(search_term=search_term)
    
    def filter_products_by_category(self):
        """
        Filter products by the selected category.
        """
        category_name = self.category_filter_var.get()
        
        if category_name == "Todas las categorías":
            # Load all products
            self.load_products()
            return
            
        try:
            # Find the category ID
            categories = self.product_controller.get_all_categories()
            category_id = None
            
            for category in categories:
                if category.name == category_name:
                    category_id = category.id
                    break
                    
            if category_id is None:
                messagebox.showerror("Error", "Categoría no encontrada")
                return
                
            # Load products filtered by category
            self.load_products(category_id=category_id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar productos: {str(e)}")
    
    def clear_product_filters(self):
        """
        Clear product filters and show all products.
        """
        self.product_search_var.set("")
        self.category_combo.current(0)
        self.load_products()
    
    def on_product_double_click(self, event):
        """
        Handle double click on a product in the products treeview.
        
        Args:
            event: Tkinter event
        """
        # Get the selected item
        selected_items = self.products_tree.selection()
        if not selected_items:
            return
            
        # Get the product ID
        item = selected_items[0]
        product_id = self.products_tree.item(item, "values")[0]
        
        # Show dialog to add the product to the sale
        self.show_add_product_to_sale_dialog()
    
    def show_add_product_to_sale_dialog(self):
        """
        Show dialog to add a product to the current sale.
        """
        # Get the selected product
        selected_items = self.products_tree.selection()
        if not selected_items:
            messagebox.showinfo("Información", "Seleccione un producto para agregar a la venta")
            return
            
        # Get the product ID
        item = selected_items[0]
        product_id = self.products_tree.item(item, "values")[0]
        
        try:
            # Get the product details
            product = self.product_controller.get_product(product_id)
            if not product:
                messagebox.showerror("Error", "Producto no encontrado")
                return
                
            if not product.variants:
                messagebox.showerror("Error", "El producto no tiene variantes disponibles")
                return
                
            # Filter variants with stock > 0
            variants_with_stock = [v for v in product.variants if v.inventory_quantity > 0]
                
            if not variants_with_stock:
                messagebox.showerror("Error", "El producto no tiene stock disponible")
                return
                
            # Create a new dialog
            dialog = tk.Toplevel(self.parent)
            dialog.title(f"Agregar {product.name} a la Venta")
            dialog.geometry("400x250")
            dialog.transient(self.parent)
            dialog.grab_set()
            
            # Product form
            form_frame = ttk.Frame(dialog, padding=10)
            form_frame.pack(fill=tk.BOTH, expand=True)
            
            # Current price
            current_price = product.get_current_price()
            
            # Product info
            ttk.Label(form_frame, text="Producto:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            ttk.Label(form_frame, text=product.name).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
            
            ttk.Label(form_frame, text="Precio:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            ttk.Label(form_frame, text=f"${current_price:.2f}").grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
            
            # Variant selection
            ttk.Label(form_frame, text="Variante:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
            
            variant_options = [f"{v.color} - Talla {v.size} (Stock: {v.inventory_quantity})" for v in variants_with_stock]
            variant_var = tk.StringVar()
            variant_combo = ttk.Combobox(form_frame, textvariable=variant_var, values=variant_options, width=30)
            variant_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
            variant_combo.current(0)
            
            # Quantity
            ttk.Label(form_frame, text="Cantidad:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
            quantity_var = tk.StringVar(value="1")
            quantity_entry = ttk.Entry(form_frame, textvariable=quantity_var, width=10)
            quantity_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
            
            # Set focus to quantity entry
            quantity_entry.focus_set()
            
            # Buttons frame
            buttons_frame = ttk.Frame(dialog)
            buttons_frame.pack(fill=tk.X, padx=10, pady=10)
            
            def add_to_sale():
                # Validate quantity
                try:
                    quantity = int(quantity_var.get().strip())
                    if quantity <= 0:
                        messagebox.showerror("Error", "La cantidad debe ser mayor que cero")
                        return
                except:
                    messagebox.showerror("Error", "La cantidad debe ser un número entero")
                    return
                    
                # Get selected variant
                selected_variant_idx = variant_combo.current()
                if selected_variant_idx < 0:
                    messagebox.showerror("Error", "Seleccione una variante")
                    return
                    
                selected_variant = variants_with_stock[selected_variant_idx]
                
                # Check stock
                if quantity > selected_variant.inventory_quantity:
                    messagebox.showerror("Error", f"Stock insuficiente. Disponible: {selected_variant.inventory_quantity}")
                    return
                    
                # Create sale item
                sale_item = SaleItem(
                    product_variant_id=selected_variant.id,
                    quantity=quantity,
                    unit_price=current_price,
                    discount_percent=product.discount_percent if product.is_discount_active() else 0
                )
                
                # Add product information for display
                sale_item.product_name = product.name
                sale_item.variant_info = f"{selected_variant.color} - Talla {selected_variant.size}"
                
                # Add to sale
                self.add_item_to_sale(sale_item)
                
                # Close the dialog
                dialog.destroy()
            
            # Save and cancel buttons
            ttk.Button(buttons_frame, text="Agregar", command=add_to_sale).pack(side=tk.RIGHT, padx=5)
            ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar producto: {str(e)}")
    
    def add_item_to_sale(self, sale_item):
        """
        Add an item to the current sale.
        
        Args:
            sale_item: SaleItem object to add
        """
        # Check if we already have this variant in the sale
        for i, item in enumerate(self.current_sale_items):
            if item.product_variant_id == sale_item.product_variant_id:
                # Update existing item
                item.quantity += sale_item.quantity
                item.recalculate_subtotal()
                
                # Update the display
                self.update_sale_items_display()
                self.update_sale_totals()
                return
        
        # Add as a new item
        self.current_sale_items.append(sale_item)
        
        # Update the display
        self.update_sale_items_display()
        self.update_sale_totals()
    
    def update_sale_items_display(self):
        """
        Update the sale items treeview with current items.
        """
        # Clear the treeview
        for item in self.sale_items_tree.get_children():
            self.sale_items_tree.delete(item)
            
        # Insert current items
        for item in self.current_sale_items:
            self.sale_items_tree.insert(
                "", 
                "end", 
                values=(
                    item.product_name,
                    item.variant_info,
                    item.quantity,
                    f"${item.unit_price:.2f}",
                    f"{item.discount_percent}%" if item.discount_percent > 0 else "No",
                    f"${item.subtotal:.2f}"
                )
            )
    
    def update_sale_totals(self):
        """
        Update the sale totals display.
        """
        # Calculate totals
        total_items = sum(item.quantity for item in self.current_sale_items)
        total_amount = sum(item.subtotal for item in self.current_sale_items)
        
        # Update display
        self.total_items_var.set(str(total_items))
        self.total_amount_var.set(f"${total_amount:.2f}")
        
        # Update the current sale object
        if self.current_sale:
            self.current_sale.total_amount = total_amount
    
    def edit_sale_item_quantity(self):
        """
        Edit the quantity of the selected sale item.
        """
        # Get the selected item
        selected_items = self.sale_items_tree.selection()
        if not selected_items:
            messagebox.showinfo("Información", "Seleccione un producto para editar su cantidad")
            return
            
        # Get the index of the selected item
        item_idx = self.sale_items_tree.index(selected_items[0])
        
        # Get the sale item
        sale_item = self.current_sale_items[item_idx]
        
        # Show a dialog to edit the quantity
        new_quantity = tk.simpledialog.askinteger(
            "Editar Cantidad", 
            f"Nueva cantidad para {sale_item.product_name} - {sale_item.variant_info}:",
            initialvalue=sale_item.quantity,
            minvalue=1,
            parent=self.parent
        )
        
        if new_quantity is None:
            return  # User cancelled
            
        # Check stock
        try:
            # Get product variant
            product_variant = None
            product = None
            
            # Find the variant in all products
            products = self.product_controller.get_all_products(include_variants=True)
            for p in products:
                for v in p.variants:
                    if v.id == sale_item.product_variant_id:
                        product_variant = v
                        product = p
                        break
                if product_variant:
                    break
                    
            if not product_variant:
                messagebox.showerror("Error", "Variante no encontrada")
                return
                
            if new_quantity > product_variant.inventory_quantity:
                messagebox.showerror("Error", f"Stock insuficiente. Disponible: {product_variant.inventory_quantity}")
                return
                
            # Update the quantity
            sale_item.quantity = new_quantity
            
            # Recalculate subtotal
            sale_item.recalculate_subtotal()
            
            # Update the display
            self.update_sale_items_display()
            self.update_sale_totals()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar cantidad: {str(e)}")
    
    def remove_sale_item(self):
        """
        Remove the selected item from the sale.
        """
        # Get the selected item
        selected_items = self.sale_items_tree.selection()
        if not selected_items:
            messagebox.showinfo("Información", "Seleccione un producto para eliminarlo de la venta")
            return
            
        # Get the index of the selected item
        item_idx = self.sale_items_tree.index(selected_items[0])
        
        # Remove the item
        del self.current_sale_items[item_idx]
        
        # Update the display
        self.update_sale_items_display()
        self.update_sale_totals()
    
    def search_customers(self):
        """
        Search for customers to associate with the sale.
        """
        search_term = self.customer_search_var.get().strip()
        
        if not search_term:
            messagebox.showinfo("Información", "Ingrese un término de búsqueda")
            return
            
        try:
            # Search customers
            customers = self.customer_controller.search_customers(search_term)
            
            if not customers:
                messagebox.showinfo("Información", "No se encontraron clientes con ese término de búsqueda")
                return
                
            # If there's only one result, select it automatically
            if len(customers) == 1:
                self.select_customer(customers[0])
                return
                
            # If there are multiple results, show a dialog to select one
            self.show_customer_selection_dialog(customers)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar clientes: {str(e)}")
    
    def show_customer_selection_dialog(self, customers):
        """
        Show a dialog to select a customer from search results.
        
        Args:
            customers: List of Customer objects
        """
        # Create a new dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Seleccionar Cliente")
        dialog.geometry("500x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Customers list frame
        list_frame = ttk.Frame(dialog, padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Customers treeview
        customers_tree = ttk.Treeview(
            list_frame,
            columns=("ID", "Nombre", "Email", "Teléfono"),
            show="headings"
        )
        customers_tree.heading("ID", text="ID")
        customers_tree.heading("Nombre", text="Nombre")
        customers_tree.heading("Email", text="Email")
        customers_tree.heading("Teléfono", text="Teléfono")
        
        customers_tree.column("ID", width=50, anchor=tk.CENTER)
        customers_tree.column("Nombre", width=150)
        customers_tree.column("Email", width=150)
        customers_tree.column("Teléfono", width=100)
        
        # Scrollbar for customers tree
        customers_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=customers_tree.yview)
        customers_tree.configure(yscrollcommand=customers_scrollbar.set)
        
        # Pack the tree and scrollbar
        customers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        customers_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insert customers
        for customer in customers:
            customers_tree.insert(
                "", 
                "end", 
                values=(
                    customer.id,
                    customer.name,
                    customer.email or "",
                    customer.phone or ""
                )
            )
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def select():
            # Get the selected item
            selected_items = customers_tree.selection()
            if not selected_items:
                messagebox.showinfo("Información", "Seleccione un cliente")
                return
                
            # Get the customer ID
            item = selected_items[0]
            customer_id = customers_tree.item(item, "values")[0]
            
            # Find the customer
            for customer in customers:
                if customer.id == int(customer_id):
                    self.select_customer(customer)
                    break
                    
            # Close the dialog
            dialog.destroy()
        
        # Select and cancel buttons
        ttk.Button(buttons_frame, text="Seleccionar", command=select).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Bind double click to select
        customers_tree.bind("<Double-1>", lambda e: select())
    
    def select_customer(self, customer):
        """
        Associate a customer with the current sale.
        
        Args:
            customer: Customer object
        """
        if not self.current_sale:
            return
            
        # Set the customer ID
        self.current_sale.customer_id = customer.id
        
        # Update the display
        self.selected_customer_var.set(f"{customer.name} (ID: {customer.id})")
    
    def start_new_sale(self):
        """
        Start a new sale.
        """
        # Create a new sale object
        self.current_sale = Sale(
            sale_date=datetime.now().isoformat(),
            payment_method=self.payment_method_var.get()
        )
        
        # Clear the list of items
        self.current_sale_items = []
        
        # Reset customer
        self.customer_search_var.set("")
        self.selected_customer_var.set("Cliente no registrado")
        
        # Reset payment method
        self.payment_method_var.set("EFECTIVO")
        
        # Update the display
        self.update_sale_items_display()
        self.update_sale_totals()
    
    def cancel_current_sale(self):
        """
        Cancel the current sale.
        """
        if not self.current_sale_items:
            messagebox.showinfo("Información", "No hay productos en la venta actual")
            return
            
        # Confirm cancellation
        if not messagebox.askyesno("Confirmar", "¿Está seguro que desea cancelar la venta actual?"):
            return
            
        # Start a new sale
        self.start_new_sale()
    
    def finalize_sale(self):
        """
        Finalize the current sale.
        """
        if not self.current_sale_items:
            messagebox.showinfo("Información", "No hay productos en la venta actual")
            return
            
        try:
            # Update the payment method
            self.current_sale.payment_method = self.payment_method_var.get()
            
            # Set the items
            self.current_sale.items = self.current_sale_items
            
            # Create the sale
            sale_id = self.sale_controller.create_sale(self.current_sale)
            
            # Success
            messagebox.showinfo("Éxito", f"Venta finalizada correctamente. ID: {sale_id}")
            
            # Show the sale details
            self.show_sale_details_dialog(sale_id)
            
            # Start a new sale
            self.start_new_sale()
            
            # Refresh the sales list
            self.load_sales()
            
            # Refresh products to update stock
            self.load_products()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al finalizar venta: {str(e)}")
    
    def apply_sales_filters(self):
        """
        Apply filters to the sales history.
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
        
        # Load sales with filters
        self.load_sales()
    
    def clear_sales_filters(self):
        """
        Clear sales history filters.
        """
        # Set default dates (30 days ago to today)
        start_date = (datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        self.start_date_var.set(start_date)
        self.end_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        
        # Load sales
        self.load_sales()
    
    def on_sale_double_click(self, event):
        """
        Handle double click on a sale in the sales treeview.
        
        Args:
            event: Tkinter event
        """
        self.show_sale_details()
    
    def show_sale_details(self):
        """
        Show details of the selected sale.
        """
        # Get the selected item
        selected_items = self.sales_tree.selection()
        if not selected_items:
            messagebox.showinfo("Información", "Seleccione una venta para ver sus detalles")
            return
            
        # Get the sale ID
        item = selected_items[0]
        sale_id = self.sales_tree.item(item, "values")[0]
        
        self.show_sale_details_dialog(sale_id)
    
    def show_sale_details_dialog(self, sale_id):
        """
        Show dialog with sale details.
        
        Args:
            sale_id: ID of the sale
        """
        try:
            # Get the sale details
            sale = self.sale_controller.get_sale(sale_id)
            if not sale:
                messagebox.showerror("Error", "No se encontró la venta")
                return
                
            # Create a new dialog
            dialog = tk.Toplevel(self.parent)
            dialog.title(f"Detalles de Venta #{sale_id}")
            dialog.geometry("600x400")
            dialog.transient(self.parent)
            dialog.grab_set()
            
            # Sale info frame
            info_frame = ttk.LabelFrame(dialog, text="Información de la Venta")
            info_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Sale info grid
            info_grid = ttk.Frame(info_frame)
            info_grid.pack(fill=tk.X, padx=10, pady=10)
            
            # Format the date
            sale_date = sale.sale_date
            try:
                dt = datetime.fromisoformat(sale_date)
                sale_date = dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass
                
            # Format payment method
            payment_method = sale.payment_method
            if payment_method == "EFECTIVO":
                payment_method = "Efectivo"
            elif payment_method == "TARJETA":
                payment_method = "Tarjeta"
            elif payment_method == "TRANSFERENCIA":
                payment_method = "Transferencia"
            
            # Row 0
            ttk.Label(info_grid, text="Venta ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(info_grid, text=str(sale.id)).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
            
            ttk.Label(info_grid, text="Fecha:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
            ttk.Label(info_grid, text=sale_date).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
            
            # Row 1
            ttk.Label(info_grid, text="Cliente:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(info_grid, text=sale.customer_name).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
            
            ttk.Label(info_grid, text="Método de Pago:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
            ttk.Label(info_grid, text=payment_method).grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
            
            # Row 2
            ttk.Label(info_grid, text="Total:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(info_grid, text=f"${sale.total_amount:.2f}").grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
            
            # Sale items frame
            items_frame = ttk.LabelFrame(dialog, text="Productos")
            items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Sale items treeview
            items_tree = ttk.Treeview(
                items_frame,
                columns=("Producto", "Variante", "Cantidad", "Precio", "Descuento", "Subtotal"),
                show="headings"
            )
            items_tree.heading("Producto", text="Producto")
            items_tree.heading("Variante", text="Variante")
            items_tree.heading("Cantidad", text="Cantidad")
            items_tree.heading("Precio", text="Precio Unit.")
            items_tree.heading("Descuento", text="Descuento")
            items_tree.heading("Subtotal", text="Subtotal")
            
            items_tree.column("Producto", width=150)
            items_tree.column("Variante", width=150)
            items_tree.column("Cantidad", width=80, anchor=tk.CENTER)
            items_tree.column("Precio", width=80, anchor=tk.E)
            items_tree.column("Descuento", width=80, anchor=tk.CENTER)
            items_tree.column("Subtotal", width=80, anchor=tk.E)
            
            # Scrollbar for items tree
            items_scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=items_tree.yview)
            items_tree.configure(yscrollcommand=items_scrollbar.set)
            
            # Pack the tree and scrollbar
            items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            items_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
            
            # Insert sale items
            for item in sale.items:
                items_tree.insert(
                    "", 
                    "end", 
                    values=(
                        item.product_name,
                        item.variant_info,
                        item.quantity,
                        f"${item.unit_price:.2f}",
                        f"{item.discount_percent}%" if item.discount_percent > 0 else "No",
                        f"${item.subtotal:.2f}"
                    )
                )
                
            # Buttons frame
            buttons_frame = ttk.Frame(dialog)
            buttons_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Close button
            ttk.Button(buttons_frame, text="Cerrar", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles de la venta: {str(e)}")
    
    def cancel_sale(self):
        """
        Cancel the selected sale.
        """
        # Get the selected item
        selected_items = self.sales_tree.selection()
        if not selected_items:
            messagebox.showinfo("Información", "Seleccione una venta para cancelar")
            return
            
        # Get the sale ID
        item = selected_items[0]
        sale_id = self.sales_tree.item(item, "values")[0]
        
        # Confirm cancellation
        if not messagebox.askyesno(
            "Confirmar Cancelación", 
            f"¿Está seguro que desea cancelar la venta #{sale_id}?\n\n"
            "Esta acción devolverá los productos al inventario y eliminará la venta."
        ):
            return
            
        try:
            # Cancel the sale
            self.sale_controller.cancel_sale(sale_id)
            
            # Success
            messagebox.showinfo("Éxito", "Venta cancelada correctamente")
            
            # Refresh the sales list
            self.load_sales()
            
            # Refresh products to update stock
            self.load_products()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cancelar venta: {str(e)}")
