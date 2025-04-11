"""
Supplier view for the Clothing Store Management System.
Manages the UI for supplier-related operations.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.supplier import Supplier


class SupplierView:
    """
    View for managing suppliers and their associated products.
    """
    
    def __init__(self, parent, supplier_controller, product_controller):
        """
        Initialize the supplier view.
        
        Args:
            parent: Parent widget
            supplier_controller: Supplier controller instance
            product_controller: Product controller instance for product associations
        """
        self.parent = parent
        self.supplier_controller = supplier_controller
        self.product_controller = product_controller
        
        # Selected supplier
        self.selected_supplier = None
        
        # Setup UI components
        self.setup_ui()
        
        # Load initial data
        self.load_suppliers()
        
    def setup_ui(self):
        """
        Set up the UI components.
        """
        # Main container
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Split view - supplier list and details
        self.paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - supplier list
        self.suppliers_frame = ttk.Frame(self.paned)
        self.paned.add(self.suppliers_frame, weight=40)
        
        # Search frame
        self.search_frame = ttk.Frame(self.suppliers_frame)
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.search_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(self.search_frame, text="Buscar", command=self.search_suppliers).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.search_frame, text="Limpiar", command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        # Suppliers list
        self.suppliers_list_frame = ttk.Frame(self.suppliers_frame)
        self.suppliers_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Suppliers treeview
        self.suppliers_tree = ttk.Treeview(
            self.suppliers_list_frame,
            columns=("ID", "Nombre", "Contacto", "Teléfono"),
            show="headings"
        )
        self.suppliers_tree.heading("ID", text="ID")
        self.suppliers_tree.heading("Nombre", text="Nombre")
        self.suppliers_tree.heading("Contacto", text="Contacto")
        self.suppliers_tree.heading("Teléfono", text="Teléfono")
        
        self.suppliers_tree.column("ID", width=50, anchor=tk.CENTER)
        self.suppliers_tree.column("Nombre", width=150)
        self.suppliers_tree.column("Contacto", width=150)
        self.suppliers_tree.column("Teléfono", width=100)
        
        # Scrollbar for suppliers tree
        suppliers_scrollbar = ttk.Scrollbar(self.suppliers_list_frame, orient="vertical", command=self.suppliers_tree.yview)
        self.suppliers_tree.configure(yscrollcommand=suppliers_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.suppliers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        suppliers_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.suppliers_tree.bind("<<TreeviewSelect>>", self.on_supplier_selected)
        
        # Buttons frame
        self.buttons_frame = ttk.Frame(self.suppliers_frame)
        self.buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(self.buttons_frame, text="Nuevo", command=self.show_add_supplier_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.buttons_frame, text="Editar", command=self.show_edit_supplier_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.buttons_frame, text="Eliminar", command=self.delete_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.buttons_frame, text="Actualizar", command=self.load_suppliers).pack(side=tk.RIGHT, padx=5)
        
        # Right panel - supplier details
        self.details_frame = ttk.Frame(self.paned)
        self.paned.add(self.details_frame, weight=60)
        
        # Supplier info frame
        self.info_frame = ttk.LabelFrame(self.details_frame, text="Información del Proveedor")
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Supplier info grid
        self.info_grid = ttk.Frame(self.info_frame)
        self.info_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Row 0
        ttk.Label(self.info_grid, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.supplier_id_var = tk.StringVar()
        ttk.Label(self.info_grid, textvariable=self.supplier_id_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(self.info_grid, text="Nombre:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.supplier_name_var = tk.StringVar()
        ttk.Label(self.info_grid, textvariable=self.supplier_name_var).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Row 1
        ttk.Label(self.info_grid, text="Contacto:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.supplier_contact_var = tk.StringVar()
        ttk.Label(self.info_grid, textvariable=self.supplier_contact_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(self.info_grid, text="Email:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.supplier_email_var = tk.StringVar()
        ttk.Label(self.info_grid, textvariable=self.supplier_email_var).grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Row 2
        ttk.Label(self.info_grid, text="Teléfono:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.supplier_phone_var = tk.StringVar()
        ttk.Label(self.info_grid, textvariable=self.supplier_phone_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Row 3
        ttk.Label(self.info_grid, text="Dirección:").grid(row=3, column=0, sticky=tk.NW, padx=5, pady=2)
        self.supplier_address_var = tk.StringVar()
        ttk.Label(self.info_grid, textvariable=self.supplier_address_var, wraplength=400).grid(row=3, column=1, columnspan=3, sticky=tk.W, padx=5, pady=2)
        
        # Supplier products frame
        self.products_frame = ttk.LabelFrame(self.details_frame, text="Productos del Proveedor")
        self.products_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Products treeview
        self.products_tree = ttk.Treeview(
            self.products_frame,
            columns=("ID", "Código", "Nombre", "Categoría", "Precio"),
            show="headings"
        )
        self.products_tree.heading("ID", text="ID")
        self.products_tree.heading("Código", text="Código")
        self.products_tree.heading("Nombre", text="Nombre")
        self.products_tree.heading("Categoría", text="Categoría")
        self.products_tree.heading("Precio", text="Precio")
        
        self.products_tree.column("ID", width=50, anchor=tk.CENTER)
        self.products_tree.column("Código", width=100)
        self.products_tree.column("Nombre", width=200)
        self.products_tree.column("Categoría", width=150)
        self.products_tree.column("Precio", width=100, anchor=tk.E)
        
        # Scrollbar for products tree
        products_scrollbar = ttk.Scrollbar(self.products_frame, orient="vertical", command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=products_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        products_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Products buttons frame
        self.products_buttons_frame = ttk.Frame(self.details_frame)
        self.products_buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(self.products_buttons_frame, text="Agregar Producto", command=self.show_add_product_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.products_buttons_frame, text="Quitar Producto", command=self.remove_product).pack(side=tk.LEFT, padx=5)
        
    def load_suppliers(self):
        """
        Load suppliers from the database and display them in the treeview.
        """
        # Clear the treeview
        for item in self.suppliers_tree.get_children():
            self.suppliers_tree.delete(item)
            
        try:
            # Get all suppliers
            suppliers = self.supplier_controller.get_all_suppliers()
            
            # Insert into treeview
            for supplier in suppliers:
                self.suppliers_tree.insert(
                    "", 
                    "end", 
                    values=(
                        supplier.id,
                        supplier.name,
                        supplier.contact_person,
                        supplier.phone or ""
                    )
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar proveedores: {str(e)}")
    
    def search_suppliers(self):
        """
        Search for suppliers by name, contact person, email, or phone.
        """
        search_term = self.search_var.get().strip()
        
        if not search_term:
            messagebox.showinfo("Información", "Ingrese un término de búsqueda")
            return
            
        try:
            # Search suppliers
            suppliers = self.supplier_controller.search_suppliers(search_term)
            
            # Clear the treeview
            for item in self.suppliers_tree.get_children():
                self.suppliers_tree.delete(item)
                
            # Insert matching suppliers
            for supplier in suppliers:
                self.suppliers_tree.insert(
                    "", 
                    "end", 
                    values=(
                        supplier.id,
                        supplier.name,
                        supplier.contact_person,
                        supplier.phone or ""
                    )
                )
                
            if not suppliers:
                messagebox.showinfo("Información", "No se encontraron proveedores con ese término de búsqueda")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar proveedores: {str(e)}")
    
    def clear_search(self):
        """
        Clear the search field and refresh the suppliers list.
        """
        self.search_var.set("")
        self.load_suppliers()
    
    def on_supplier_selected(self, event):
        """
        Handle supplier selection in the treeview.
        
        Args:
            event: Tkinter event
        """
        # Get the selected item
        selected_items = self.suppliers_tree.selection()
        if not selected_items:
            return
            
        # Get the first selected item
        item = selected_items[0]
        supplier_id = self.suppliers_tree.item(item, "values")[0]
        
        try:
            # Get the supplier details
            supplier = self.supplier_controller.get_supplier(supplier_id)
            if not supplier:
                return
                
            # Store the selected supplier
            self.selected_supplier = supplier
            
            # Update the supplier details UI
            self.update_supplier_details(supplier)
            
            # Load supplier products
            self.load_supplier_products(supplier.id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles del proveedor: {str(e)}")
    
    def update_supplier_details(self, supplier):
        """
        Update the supplier details UI with the selected supplier information.
        
        Args:
            supplier: Supplier object
        """
        self.supplier_id_var.set(str(supplier.id))
        self.supplier_name_var.set(supplier.name)
        self.supplier_contact_var.set(supplier.contact_person or "")
        self.supplier_email_var.set(supplier.email or "")
        self.supplier_phone_var.set(supplier.phone or "")
        self.supplier_address_var.set(supplier.address or "")
    
    def load_supplier_products(self, supplier_id):
        """
        Load products for the selected supplier.
        
        Args:
            supplier_id: ID of the supplier
        """
        # Clear the treeview
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
            
        try:
            # Get supplier products
            products = self.supplier_controller.get_supplier_products(supplier_id)
            
            # Insert into treeview
            for product in products:
                self.products_tree.insert(
                    "", 
                    "end", 
                    values=(
                        product["id"],
                        product["code"],
                        product["name"],
                        product["category"],
                        f"${product['price']:.2f}"
                    )
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar productos del proveedor: {str(e)}")
    
    def show_add_supplier_dialog(self):
        """
        Show dialog to add a new supplier.
        """
        # Create a new dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Agregar Nuevo Proveedor")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Supplier form
        form_frame = ttk.Frame(dialog, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Contact person
        ttk.Label(form_frame, text="Persona de Contacto:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        contact_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=contact_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=email_var, width=30).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Phone
        ttk.Label(form_frame, text="Teléfono:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        phone_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=phone_var, width=30).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Address
        ttk.Label(form_frame, text="Dirección:").grid(row=4, column=0, sticky=tk.NW, padx=5, pady=5)
        address_text = tk.Text(form_frame, width=30, height=3)
        address_text.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_supplier():
            # Validate name
            if not name_var.get().strip():
                messagebox.showerror("Error", "El nombre del proveedor es obligatorio")
                return
                
            # Create supplier object
            supplier = Supplier(
                name=name_var.get().strip(),
                contact_person=contact_var.get().strip(),
                email=email_var.get().strip(),
                phone=phone_var.get().strip(),
                address=address_text.get("1.0", tk.END).strip()
            )
            
            try:
                # Add supplier to database
                supplier_id = self.supplier_controller.add_supplier(supplier)
                
                # Refresh the suppliers list
                self.load_suppliers()
                
                # Close the dialog
                dialog.destroy()
                
                # Show success message
                messagebox.showinfo("Éxito", "Proveedor agregado correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar proveedor: {str(e)}")
        
        ttk.Button(buttons_frame, text="Guardar", command=save_supplier).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def show_edit_supplier_dialog(self):
        """
        Show dialog to edit the selected supplier.
        """
        # Check if a supplier is selected
        if not self.selected_supplier:
            messagebox.showinfo("Información", "Seleccione un proveedor para editar")
            return
            
        # Create a new dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Editar Proveedor")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Supplier form
        form_frame = ttk.Frame(dialog, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar(value=self.selected_supplier.name)
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Contact person
        ttk.Label(form_frame, text="Persona de Contacto:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        contact_var = tk.StringVar(value=self.selected_supplier.contact_person or "")
        ttk.Entry(form_frame, textvariable=contact_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        email_var = tk.StringVar(value=self.selected_supplier.email or "")
        ttk.Entry(form_frame, textvariable=email_var, width=30).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Phone
        ttk.Label(form_frame, text="Teléfono:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        phone_var = tk.StringVar(value=self.selected_supplier.phone or "")
        ttk.Entry(form_frame, textvariable=phone_var, width=30).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Address
        ttk.Label(form_frame, text="Dirección:").grid(row=4, column=0, sticky=tk.NW, padx=5, pady=5)
        address_text = tk.Text(form_frame, width=30, height=3)
        address_text.insert("1.0", self.selected_supplier.address or "")
        address_text.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_supplier():
            # Validate name
            if not name_var.get().strip():
                messagebox.showerror("Error", "El nombre del proveedor es obligatorio")
                return
                
            # Update supplier object
            self.selected_supplier.name = name_var.get().strip()
            self.selected_supplier.contact_person = contact_var.get().strip()
            self.selected_supplier.email = email_var.get().strip()
            self.selected_supplier.phone = phone_var.get().strip()
            self.selected_supplier.address = address_text.get("1.0", tk.END).strip()
            
            try:
                # Update supplier in database
                self.supplier_controller.update_supplier(self.selected_supplier)
                
                # Refresh the suppliers list
                self.load_suppliers()
                
                # Update the supplier details UI
                self.update_supplier_details(self.selected_supplier)
                
                # Close the dialog
                dialog.destroy()
                
                # Show success message
                messagebox.showinfo("Éxito", "Proveedor actualizado correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar proveedor: {str(e)}")
        
        ttk.Button(buttons_frame, text="Guardar", command=save_supplier).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def delete_supplier(self):
        """
        Delete the selected supplier.
        """
        # Check if a supplier is selected
        if not self.selected_supplier:
            messagebox.showinfo("Información", "Seleccione un proveedor para eliminar")
            return
            
        # Confirm deletion
        if not messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el proveedor '{self.selected_supplier.name}'?"):
            return
            
        try:
            # Delete supplier from database
            self.supplier_controller.delete_supplier(self.selected_supplier.id)
            
            # Refresh the suppliers list
            self.load_suppliers()
            
            # Clear the selection
            self.selected_supplier = None
            
            # Clear the supplier details UI
            self.supplier_id_var.set("")
            self.supplier_name_var.set("")
            self.supplier_contact_var.set("")
            self.supplier_email_var.set("")
            self.supplier_phone_var.set("")
            self.supplier_address_var.set("")
            
            # Clear the products treeview
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
                
            # Show success message
            messagebox.showinfo("Éxito", "Proveedor eliminado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar proveedor: {str(e)}")
    
    def show_add_product_dialog(self):
        """
        Show dialog to add a product to the supplier.
        """
        # Check if a supplier is selected
        if not self.selected_supplier:
            messagebox.showinfo("Información", "Seleccione un proveedor para agregar productos")
            return
            
        # Create a new dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Agregar Producto al Proveedor")
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Product selection frame
        selection_frame = ttk.Frame(dialog, padding=10)
        selection_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search frame
        search_frame = ttk.Frame(selection_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Buscar Producto:").pack(side=tk.LEFT, padx=5)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        def search_products():
            # Get the search term
            search_term = search_var.get().strip()
            
            # Clear the treeview
            for item in products_tree.get_children():
                products_tree.delete(item)
                
            try:
                # Search products
                if search_term:
                    products = self.product_controller.search_products(search_term)
                else:
                    products = self.product_controller.get_all_products()
                
                # Get current supplier products
                supplier_products = self.supplier_controller.get_supplier_products(self.selected_supplier.id)
                supplier_product_ids = [p["id"] for p in supplier_products]
                
                # Insert products not already associated with the supplier
                for product in products:
                    if product.id not in supplier_product_ids:
                        products_tree.insert(
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
                messagebox.showerror("Error", f"Error al buscar productos: {str(e)}")
        
        ttk.Button(search_frame, text="Buscar", command=search_products).pack(side=tk.LEFT, padx=5)
        
        # Products treeview
        products_tree = ttk.Treeview(
            selection_frame,
            columns=("ID", "Código", "Nombre", "Precio"),
            show="headings"
        )
        products_tree.heading("ID", text="ID")
        products_tree.heading("Código", text="Código")
        products_tree.heading("Nombre", text="Nombre")
        products_tree.heading("Precio", text="Precio")
        
        products_tree.column("ID", width=50, anchor=tk.CENTER)
        products_tree.column("Código", width=100)
        products_tree.column("Nombre", width=200)
        products_tree.column("Precio", width=100, anchor=tk.E)
        
        # Scrollbar for products tree
        products_scrollbar = ttk.Scrollbar(selection_frame, orient="vertical", command=products_tree.yview)
        products_tree.configure(yscrollcommand=products_scrollbar.set)
        
        # Pack the tree and scrollbar
        products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        products_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Load products initially
        search_products()
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def add_product():
            # Check if a product is selected
            selected_items = products_tree.selection()
            if not selected_items:
                messagebox.showinfo("Información", "Seleccione un producto para agregar")
                return
                
            # Get the selected product ID
            product_id = products_tree.item(selected_items[0], "values")[0]
            
            try:
                # Add product to supplier
                self.supplier_controller.add_product_to_supplier(self.selected_supplier.id, product_id)
                
                # Refresh the supplier products
                self.load_supplier_products(self.selected_supplier.id)
                
                # Close the dialog
                dialog.destroy()
                
                # Show success message
                messagebox.showinfo("Éxito", "Producto agregado al proveedor correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar producto al proveedor: {str(e)}")
        
        ttk.Button(buttons_frame, text="Agregar", command=add_product).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def remove_product(self):
        """
        Remove a product from the supplier.
        """
        # Check if a supplier is selected
        if not self.selected_supplier:
            messagebox.showinfo("Información", "Seleccione un proveedor")
            return
            
        # Check if a product is selected
        selected_items = self.products_tree.selection()
        if not selected_items:
            messagebox.showinfo("Información", "Seleccione un producto para quitar")
            return
            
        # Get the selected product ID
        product_id = self.products_tree.item(selected_items[0], "values")[0]
        product_name = self.products_tree.item(selected_items[0], "values")[2]
        
        # Confirm removal
        if not messagebox.askyesno("Confirmar", f"¿Está seguro de quitar el producto '{product_name}' de este proveedor?"):
            return
            
        try:
            # Remove product from supplier
            self.supplier_controller.remove_product_from_supplier(self.selected_supplier.id, product_id)
            
            # Refresh the supplier products
            self.load_supplier_products(self.selected_supplier.id)
            
            # Show success message
            messagebox.showinfo("Éxito", "Producto quitado del proveedor correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al quitar producto del proveedor: {str(e)}")