"""
Customer view for the Clothing Store Management System.
Manages the UI for customer-related operations.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.customer import Customer


class CustomerView:
    """
    View for managing customers and their purchase history.
    """
    
    def __init__(self, parent, customer_controller, sale_controller):
        """
        Initialize the customer view.
        
        Args:
            parent: Parent widget
            customer_controller: Customer controller instance
            sale_controller: Sale controller instance for purchase history
        """
        self.parent = parent
        self.customer_controller = customer_controller
        self.sale_controller = sale_controller
        
        # Selected customer
        self.selected_customer = None
        
        # Setup UI components
        self.setup_ui()
        
        # Load initial data
        self.load_customers()
        
    def setup_ui(self):
        """
        Set up the UI components.
        """
        # Main container
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Split view - customer list and details
        self.paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - customer list
        self.customers_frame = ttk.Frame(self.paned)
        self.paned.add(self.customers_frame, weight=40)
        
        # Search frame
        self.search_frame = ttk.Frame(self.customers_frame)
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.search_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(self.search_frame, text="Buscar", command=self.search_customers).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.search_frame, text="Limpiar", command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        # Customers list
        self.customers_list_frame = ttk.Frame(self.customers_frame)
        self.customers_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Customers treeview
        self.customers_tree = ttk.Treeview(
            self.customers_list_frame,
            columns=("ID", "Nombre", "Email", "Teléfono"),
            show="headings"
        )
        self.customers_tree.heading("ID", text="ID")
        self.customers_tree.heading("Nombre", text="Nombre")
        self.customers_tree.heading("Email", text="Email")
        self.customers_tree.heading("Teléfono", text="Teléfono")
        
        self.customers_tree.column("ID", width=50, anchor=tk.CENTER)
        self.customers_tree.column("Nombre", width=150)
        self.customers_tree.column("Email", width=150)
        self.customers_tree.column("Teléfono", width=100)
        
        # Scrollbar for customers tree
        customers_scrollbar = ttk.Scrollbar(self.customers_list_frame, orient="vertical", command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=customers_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.customers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        customers_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.customers_tree.bind("<<TreeviewSelect>>", self.on_customer_selected)
        
        # Buttons frame
        self.buttons_frame = ttk.Frame(self.customers_frame)
        self.buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(self.buttons_frame, text="Nuevo", command=self.show_add_customer_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.buttons_frame, text="Editar", command=self.show_edit_customer_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.buttons_frame, text="Eliminar", command=self.delete_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.buttons_frame, text="Actualizar", command=self.load_customers).pack(side=tk.RIGHT, padx=5)
        
        # Right panel - customer details
        self.details_frame = ttk.Frame(self.paned)
        self.paned.add(self.details_frame, weight=60)
        
        # Customer info frame
        self.info_frame = ttk.LabelFrame(self.details_frame, text="Información del Cliente")
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Customer info grid
        self.info_grid = ttk.Frame(self.info_frame)
        self.info_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Row 0
        ttk.Label(self.info_grid, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.customer_id_var = tk.StringVar()
        ttk.Label(self.info_grid, textvariable=self.customer_id_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(self.info_grid, text="Nombre:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.customer_name_var = tk.StringVar()
        ttk.Label(self.info_grid, textvariable=self.customer_name_var).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Row 1
        ttk.Label(self.info_grid, text="Email:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.customer_email_var = tk.StringVar()
        ttk.Label(self.info_grid, textvariable=self.customer_email_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(self.info_grid, text="Teléfono:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.customer_phone_var = tk.StringVar()
        ttk.Label(self.info_grid, textvariable=self.customer_phone_var).grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Row 2
        ttk.Label(self.info_grid, text="Dirección:").grid(row=2, column=0, sticky=tk.NW, padx=5, pady=2)
        self.customer_address_var = tk.StringVar()
        ttk.Label(self.info_grid, textvariable=self.customer_address_var, wraplength=400).grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=5, pady=2)
        
        # Row 3
        ttk.Label(self.info_grid, text="Creado:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.customer_created_var = tk.StringVar()
        ttk.Label(self.info_grid, textvariable=self.customer_created_var).grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(self.info_grid, text="Actualizado:").grid(row=3, column=2, sticky=tk.W, padx=5, pady=2)
        self.customer_updated_var = tk.StringVar()
        ttk.Label(self.info_grid, textvariable=self.customer_updated_var).grid(row=3, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Purchase history frame
        self.history_frame = ttk.LabelFrame(self.details_frame, text="Historial de Compras")
        self.history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Purchase history treeview
        self.history_tree = ttk.Treeview(
            self.history_frame,
            columns=("ID", "Fecha", "Método de Pago", "Total"),
            show="headings"
        )
        self.history_tree.heading("ID", text="ID")
        self.history_tree.heading("Fecha", text="Fecha")
        self.history_tree.heading("Método de Pago", text="Método de Pago")
        self.history_tree.heading("Total", text="Total")
        
        self.history_tree.column("ID", width=50, anchor=tk.CENTER)
        self.history_tree.column("Fecha", width=150)
        self.history_tree.column("Método de Pago", width=150)
        self.history_tree.column("Total", width=100, anchor=tk.E)
        
        # Scrollbar for history tree
        history_scrollbar = ttk.Scrollbar(self.history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Bind double click on sales to view details
        self.history_tree.bind("<Double-1>", self.show_sale_details)
        
        # History buttons frame
        self.history_buttons_frame = ttk.Frame(self.details_frame)
        self.history_buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(
            self.history_buttons_frame, 
            text="Ver Detalles de Compra", 
            command=self.show_selected_sale_details
        ).pack(side=tk.LEFT, padx=5)
        
    def load_customers(self):
        """
        Load customers from the database and display them in the treeview.
        """
        # Clear the treeview
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
            
        try:
            # Get all customers
            customers = self.customer_controller.get_all_customers()
            
            # Insert into treeview
            for customer in customers:
                self.customers_tree.insert(
                    "", 
                    "end", 
                    values=(
                        customer.id,
                        customer.name,
                        customer.email or "",
                        customer.phone or ""
                    )
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar clientes: {str(e)}")
    
    def search_customers(self):
        """
        Search for customers by name, email, or phone.
        """
        search_term = self.search_var.get().strip()
        
        if not search_term:
            messagebox.showinfo("Información", "Ingrese un término de búsqueda")
            return
            
        try:
            # Search customers
            customers = self.customer_controller.search_customers(search_term)
            
            # Clear the treeview
            for item in self.customers_tree.get_children():
                self.customers_tree.delete(item)
                
            # Insert matching customers
            for customer in customers:
                self.customers_tree.insert(
                    "", 
                    "end", 
                    values=(
                        customer.id,
                        customer.name,
                        customer.email or "",
                        customer.phone or ""
                    )
                )
                
            if not customers:
                messagebox.showinfo("Información", "No se encontraron clientes con ese término de búsqueda")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar clientes: {str(e)}")
    
    def clear_search(self):
        """
        Clear the search field and refresh the customers list.
        """
        self.search_var.set("")
        self.load_customers()
    
    def on_customer_selected(self, event):
        """
        Handle customer selection in the treeview.
        
        Args:
            event: Tkinter event
        """
        # Get the selected item
        selected_items = self.customers_tree.selection()
        if not selected_items:
            return
            
        # Get the first selected item
        item = selected_items[0]
        customer_id = self.customers_tree.item(item, "values")[0]
        
        try:
            # Get the customer details
            customer = self.customer_controller.get_customer(customer_id)
            if not customer:
                return
                
            # Store the selected customer
            self.selected_customer = customer
            
            # Update the customer details UI
            self.update_customer_details(customer)
            
            # Load purchase history
            self.load_purchase_history(customer.id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles del cliente: {str(e)}")
    
    def update_customer_details(self, customer):
        """
        Update the customer details UI with the selected customer information.
        
        Args:
            customer: Customer object
        """
        self.customer_id_var.set(str(customer.id))
        self.customer_name_var.set(customer.name)
        self.customer_email_var.set(customer.email or "")
        self.customer_phone_var.set(customer.phone or "")
        self.customer_address_var.set(customer.address or "")
        
        # Format dates for display
        created_date = ""
        if customer.created_at:
            try:
                dt = datetime.fromisoformat(customer.created_at)
                created_date = dt.strftime("%Y-%m-%d %H:%M")
            except:
                created_date = customer.created_at
                
        updated_date = ""
        if customer.updated_at:
            try:
                dt = datetime.fromisoformat(customer.updated_at)
                updated_date = dt.strftime("%Y-%m-%d %H:%M")
            except:
                updated_date = customer.updated_at
                
        self.customer_created_var.set(created_date)
        self.customer_updated_var.set(updated_date)
    
    def load_purchase_history(self, customer_id):
        """
        Load purchase history for the selected customer.
        
        Args:
            customer_id: ID of the customer
        """
        # Clear the treeview
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        try:
            # Get purchase history
            purchase_history = self.customer_controller.get_customer_purchase_history(customer_id)
            
            # Insert into treeview
            for purchase in purchase_history:
                # Format the date
                sale_date = purchase["sale_date"]
                try:
                    dt = datetime.fromisoformat(sale_date)
                    sale_date = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
                    
                # Format payment method
                payment_method = purchase["payment_method"]
                if payment_method == "EFECTIVO":
                    payment_method = "Efectivo"
                elif payment_method == "TARJETA":
                    payment_method = "Tarjeta"
                elif payment_method == "TRANSFERENCIA":
                    payment_method = "Transferencia"
                
                self.history_tree.insert(
                    "", 
                    "end", 
                    values=(
                        purchase["id"],
                        sale_date,
                        payment_method,
                        f"${purchase['total_amount']:.2f}"
                    )
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar historial de compras: {str(e)}")
    
    def show_sale_details(self, event):
        """
        Show details of a sale when double-clicked in the history treeview.
        
        Args:
            event: Tkinter event
        """
        # Get the selected item
        selected_items = self.history_tree.selection()
        if not selected_items:
            return
            
        # Get the first selected item
        item = selected_items[0]
        sale_id = self.history_tree.item(item, "values")[0]
        
        self.show_sale_details_dialog(sale_id)
    
    def show_selected_sale_details(self):
        """
        Show details of the selected sale when the button is clicked.
        """
        # Get the selected item
        selected_items = self.history_tree.selection()
        if not selected_items:
            messagebox.showinfo("Información", "Seleccione una compra para ver sus detalles")
            return
            
        # Get the first selected item
        item = selected_items[0]
        sale_id = self.history_tree.item(item, "values")[0]
        
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
                
            # Close button
            ttk.Button(dialog, text="Cerrar", command=dialog.destroy).pack(side=tk.RIGHT, padx=10, pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles de la venta: {str(e)}")
    
    def show_add_customer_dialog(self):
        """
        Show dialog to add a new customer.
        """
        # Create a new dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Agregar Nuevo Cliente")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Customer form
        form_frame = ttk.Frame(dialog, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=email_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Phone
        ttk.Label(form_frame, text="Teléfono:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        phone_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=phone_var, width=30).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Address
        ttk.Label(form_frame, text="Dirección:").grid(row=3, column=0, sticky=tk.NW, padx=5, pady=5)
        address_text = tk.Text(form_frame, width=30, height=5)
        address_text.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_customer():
            # Validate name
            if not name_var.get().strip():
                messagebox.showerror("Error", "El nombre del cliente es obligatorio")
                return
                
            # Create customer object
            customer = Customer(
                name=name_var.get().strip(),
                email=email_var.get().strip() or None,
                phone=phone_var.get().strip() or None,
                address=address_text.get("1.0", tk.END).strip() or None
            )
            
            try:
                # Add the customer
                customer_id = self.customer_controller.add_customer(customer)
                
                # Success
                messagebox.showinfo("Éxito", f"Cliente agregado con ID: {customer_id}")
                
                # Refresh the customers list
                self.load_customers()
                
                # Close the dialog
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar cliente: {str(e)}")
        
        # Save and cancel buttons
        ttk.Button(buttons_frame, text="Guardar", command=save_customer).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def show_edit_customer_dialog(self):
        """
        Show dialog to edit the selected customer.
        """
        if not self.selected_customer:
            messagebox.showinfo("Información", "Seleccione un cliente para editar")
            return
            
        # Create a new dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Editar Cliente")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Customer form
        form_frame = ttk.Frame(dialog, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar(value=self.selected_customer.name)
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        email_var = tk.StringVar(value=self.selected_customer.email or "")
        ttk.Entry(form_frame, textvariable=email_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Phone
        ttk.Label(form_frame, text="Teléfono:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        phone_var = tk.StringVar(value=self.selected_customer.phone or "")
        ttk.Entry(form_frame, textvariable=phone_var, width=30).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Address
        ttk.Label(form_frame, text="Dirección:").grid(row=3, column=0, sticky=tk.NW, padx=5, pady=5)
        address_text = tk.Text(form_frame, width=30, height=5)
        address_text.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        if self.selected_customer.address:
            address_text.insert("1.0", self.selected_customer.address)
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_customer():
            # Validate name
            if not name_var.get().strip():
                messagebox.showerror("Error", "El nombre del cliente es obligatorio")
                return
                
            # Update customer object
            self.selected_customer.name = name_var.get().strip()
            self.selected_customer.email = email_var.get().strip() or None
            self.selected_customer.phone = phone_var.get().strip() or None
            self.selected_customer.address = address_text.get("1.0", tk.END).strip() or None
            
            try:
                # Update the customer
                self.customer_controller.update_customer(self.selected_customer)
                
                # Success
                messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
                
                # Refresh the customers list
                self.load_customers()
                
                # Update the customer details
                self.update_customer_details(self.selected_customer)
                
                # Close the dialog
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar cliente: {str(e)}")
        
        # Save and cancel buttons
        ttk.Button(buttons_frame, text="Guardar", command=save_customer).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def delete_customer(self):
        """
        Delete the selected customer.
        """
        if not self.selected_customer:
            messagebox.showinfo("Información", "Seleccione un cliente para eliminar")
            return
            
        # Confirm deletion
        if not messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar al cliente '{self.selected_customer.name}'?"):
            return
            
        try:
            # Delete the customer
            self.customer_controller.delete_customer(self.selected_customer.id)
            
            # Success
            messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
            
            # Refresh the customers list
            self.load_customers()
            
            # Clear the customer details
            self.clear_customer_details()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar cliente: {str(e)}")
    
    def clear_customer_details(self):
        """
        Clear the customer details UI.
        """
        self.selected_customer = None
        
        self.customer_id_var.set("")
        self.customer_name_var.set("")
        self.customer_email_var.set("")
        self.customer_phone_var.set("")
        self.customer_address_var.set("")
        self.customer_created_var.set("")
        self.customer_updated_var.set("")
        
        # Clear purchase history
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
