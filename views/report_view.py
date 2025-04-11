"""
Report view for the Clothing Store Management System.
Manages the UI for generating and displaying reports.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class ReportView:
    """
    View for generating and displaying reports and analytics.
    """
    
    def __init__(self, parent, report_controller, product_controller, customer_controller, sale_controller):
        """
        Initialize the report view.
        
        Args:
            parent: Parent widget
            report_controller: Report controller instance
            product_controller: Product controller instance
            customer_controller: Customer controller instance
            sale_controller: Sale controller instance
        """
        self.parent = parent
        self.report_controller = report_controller
        self.product_controller = product_controller
        self.customer_controller = customer_controller
        self.sale_controller = sale_controller
        
        # Current report data
        self.current_report_data = None
        
        # Setup UI components
        self.setup_ui()
        
        # Initial reports
        self.load_sales_summary()
        
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
        
        # Sales report tab
        self.sales_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sales_frame, text="Ventas")
        
        # Inventory report tab
        self.inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.inventory_frame, text="Inventario")
        
        # Customers report tab
        self.customers_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.customers_frame, text="Clientes")
        
        # Setup each tab
        self.setup_sales_tab()
        self.setup_inventory_tab()
        self.setup_customers_tab()
        
        # Bind tab switch event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
    def setup_sales_tab(self):
        """
        Set up the Sales report tab UI.
        """
        # Main layout
        self.sales_main_frame = ttk.Frame(self.sales_frame)
        self.sales_main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top controls frame
        self.sales_controls_frame = ttk.LabelFrame(self.sales_main_frame, text="Opciones de Reporte")
        self.sales_controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Controls grid
        controls_grid = ttk.Frame(self.sales_controls_frame)
        controls_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Date range
        ttk.Label(controls_grid, text="Periodo:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        # Period options
        self.period_var = tk.StringVar(value="month")
        period_frame = ttk.Frame(controls_grid)
        period_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Radiobutton(period_frame, text="Mes Actual", variable=self.period_var, value="month").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(period_frame, text="Trimestre", variable=self.period_var, value="quarter").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(period_frame, text="Año", variable=self.period_var, value="year").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(period_frame, text="Personalizado", variable=self.period_var, value="custom").pack(side=tk.LEFT, padx=5)
        
        # Custom date range
        ttk.Label(controls_grid, text="Desde:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        
        date_frame = ttk.Frame(controls_grid)
        date_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Default to first day of current month
        today = datetime.now()
        first_day = datetime(today.year, today.month, 1)
        
        self.start_date_var = tk.StringVar(value=first_day.strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.start_date_var, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(date_frame, text="Hasta:").pack(side=tk.LEFT, padx=5)
        self.end_date_var = tk.StringVar(value=today.strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.end_date_var, width=12).pack(side=tk.LEFT, padx=5)
        
        # Report type
        ttk.Label(controls_grid, text="Tipo de Reporte:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        
        self.report_type_var = tk.StringVar(value="summary")
        report_type_frame = ttk.Frame(controls_grid)
        report_type_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Radiobutton(report_type_frame, text="Resumen", variable=self.report_type_var, value="summary").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(report_type_frame, text="Por Categoría", variable=self.report_type_var, value="category").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(report_type_frame, text="Por Método de Pago", variable=self.report_type_var, value="payment").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(report_type_frame, text="Productos Más Vendidos", variable=self.report_type_var, value="top_products").pack(side=tk.LEFT, padx=5)
        
        # Generate button
        ttk.Button(controls_grid, text="Generar Reporte", command=self.generate_sales_report).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Export buttons frame
        export_frame = ttk.Frame(controls_grid)
        export_frame.grid(row=3, column=1, sticky=tk.E, padx=5, pady=2)
        
        ttk.Button(export_frame, text="Exportar Excel", command=self.export_to_excel).pack(side=tk.LEFT, padx=5)
        
        # Report content area - split view
        self.sales_report_pane = ttk.PanedWindow(self.sales_main_frame, orient=tk.HORIZONTAL)
        self.sales_report_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side - chart area
        self.chart_frame = ttk.LabelFrame(self.sales_report_pane, text="Gráfico")
        self.sales_report_pane.add(self.chart_frame, weight=60)
        
        # Chart area (will be populated by matplotlib)
        self.chart_container = ttk.Frame(self.chart_frame)
        self.chart_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Right side - data tables
        self.data_frame = ttk.LabelFrame(self.sales_report_pane, text="Datos")
        self.sales_report_pane.add(self.data_frame, weight=40)
        
        # Notebook for different data views
        self.data_notebook = ttk.Notebook(self.data_frame)
        self.data_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Summary tab
        self.summary_frame = ttk.Frame(self.data_notebook)
        self.data_notebook.add(self.summary_frame, text="Resumen")
        
        # Details tab
        self.details_frame = ttk.Frame(self.data_notebook)
        self.data_notebook.add(self.details_frame, text="Detalles")
        
        # Setup summary frame
        self.setup_summary_frame()
        
        # Setup details frame
        self.setup_details_frame()
        
    def setup_summary_frame(self):
        """
        Set up the summary data frame.
        """
        # Summary values
        summary_grid = ttk.Frame(self.summary_frame, padding=10)
        summary_grid.pack(fill=tk.X, padx=5, pady=5)
        
        # Total sales
        ttk.Label(summary_grid, text="Total Ventas:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.total_sales_var = tk.StringVar(value="0")
        ttk.Label(summary_grid, textvariable=self.total_sales_var, font=("Arial", 10)).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Total amount
        ttk.Label(summary_grid, text="Monto Total:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.total_amount_var = tk.StringVar(value="$0.00")
        ttk.Label(summary_grid, textvariable=self.total_amount_var, font=("Arial", 10)).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Average sale
        ttk.Label(summary_grid, text="Promedio por Venta:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.average_sale_var = tk.StringVar(value="$0.00")
        ttk.Label(summary_grid, textvariable=self.average_sale_var, font=("Arial", 10)).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Payment methods frame
        payment_frame = ttk.LabelFrame(self.summary_frame, text="Métodos de Pago")
        payment_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Payment methods treeview
        self.payment_tree = ttk.Treeview(
            payment_frame,
            columns=("Método", "Cantidad", "Total", "Porcentaje"),
            show="headings"
        )
        self.payment_tree.heading("Método", text="Método")
        self.payment_tree.heading("Cantidad", text="Cantidad")
        self.payment_tree.heading("Total", text="Total")
        self.payment_tree.heading("Porcentaje", text="Porcentaje")
        
        self.payment_tree.column("Método", width=100)
        self.payment_tree.column("Cantidad", width=80, anchor=tk.CENTER)
        self.payment_tree.column("Total", width=100, anchor=tk.E)
        self.payment_tree.column("Porcentaje", width=80, anchor=tk.CENTER)
        
        # Scrollbar for payment tree
        payment_scrollbar = ttk.Scrollbar(payment_frame, orient="vertical", command=self.payment_tree.yview)
        self.payment_tree.configure(yscrollcommand=payment_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.payment_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        payment_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
    def setup_details_frame(self):
        """
        Set up the details data frame.
        """
        # Details treeview
        self.details_tree = ttk.Treeview(
            self.details_frame,
            columns=(),  # Will be set dynamically based on report type
            show="headings"
        )
        
        # Scrollbar for details tree
        details_scrollbar = ttk.Scrollbar(self.details_frame, orient="vertical", command=self.details_tree.yview)
        self.details_tree.configure(yscrollcommand=details_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.details_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
    def setup_inventory_tab(self):
        """
        Set up the Inventory report tab UI.
        """
        # Main layout
        self.inventory_main_frame = ttk.Frame(self.inventory_frame)
        self.inventory_main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top controls frame
        self.inventory_controls_frame = ttk.LabelFrame(self.inventory_main_frame, text="Opciones de Reporte")
        self.inventory_controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Controls grid
        inventory_controls_grid = ttk.Frame(self.inventory_controls_frame)
        inventory_controls_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Report type
        ttk.Label(inventory_controls_grid, text="Tipo de Reporte:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        self.inventory_report_type_var = tk.StringVar(value="value")
        inventory_report_type_frame = ttk.Frame(inventory_controls_grid)
        inventory_report_type_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Radiobutton(inventory_report_type_frame, text="Valor de Inventario", variable=self.inventory_report_type_var, value="value").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(inventory_report_type_frame, text="Stock por Categoría", variable=self.inventory_report_type_var, value="category").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(inventory_report_type_frame, text="Stock Bajo", variable=self.inventory_report_type_var, value="low_stock").pack(side=tk.LEFT, padx=5)
        
        # Generate button
        ttk.Button(inventory_controls_grid, text="Generar Reporte", command=self.generate_inventory_report).grid(row=1, column=0, columnspan=2, pady=10)
        
        # Export buttons frame
        inventory_export_frame = ttk.Frame(inventory_controls_grid)
        inventory_export_frame.grid(row=1, column=1, sticky=tk.E, padx=5, pady=2)
        
        ttk.Button(inventory_export_frame, text="Exportar Excel", command=self.export_inventory_to_excel).pack(side=tk.LEFT, padx=5)
        
        # Split view
        self.inventory_pane = ttk.PanedWindow(self.inventory_main_frame, orient=tk.HORIZONTAL)
        self.inventory_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side - chart
        self.inventory_chart_frame = ttk.LabelFrame(self.inventory_pane, text="Gráfico")
        self.inventory_pane.add(self.inventory_chart_frame, weight=60)
        
        # Chart container
        self.inventory_chart_container = ttk.Frame(self.inventory_chart_frame)
        self.inventory_chart_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Right side - data
        self.inventory_data_frame = ttk.LabelFrame(self.inventory_pane, text="Datos")
        self.inventory_pane.add(self.inventory_data_frame, weight=40)
        
        # Summary values for inventory
        inventory_summary_grid = ttk.Frame(self.inventory_data_frame, padding=10)
        inventory_summary_grid.pack(fill=tk.X, padx=5, pady=5)
        
        # Total inventory value
        ttk.Label(inventory_summary_grid, text="Valor Total de Inventario:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.inventory_value_var = tk.StringVar(value="$0.00")
        ttk.Label(inventory_summary_grid, textvariable=self.inventory_value_var, font=("Arial", 10)).grid(row=0, column=1, sticky=tk.E, padx=5, pady=5)
        
        # Total product count
        ttk.Label(inventory_summary_grid, text="Total de Productos:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.product_count_var = tk.StringVar(value="0")
        ttk.Label(inventory_summary_grid, textvariable=self.product_count_var, font=("Arial", 10)).grid(row=1, column=1, sticky=tk.E, padx=5, pady=5)
        
        # Total units
        ttk.Label(inventory_summary_grid, text="Total de Unidades:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.units_count_var = tk.StringVar(value="0")
        ttk.Label(inventory_summary_grid, textvariable=self.units_count_var, font=("Arial", 10)).grid(row=2, column=1, sticky=tk.E, padx=5, pady=5)
        
        # Configure grid columns
        inventory_summary_grid.columnconfigure(1, weight=1)
        
        # Inventory details treeview
        self.inventory_tree = ttk.Treeview(
            self.inventory_data_frame,
            columns=(),  # Will be set dynamically based on report type
            show="headings"
        )
        
        # Scrollbar for inventory tree
        inventory_scrollbar = ttk.Scrollbar(self.inventory_data_frame, orient="vertical", command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=inventory_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.inventory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        inventory_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
    def setup_customers_tab(self):
        """
        Set up the Customers report tab UI.
        """
        # Main layout
        self.customers_main_frame = ttk.Frame(self.customers_frame)
        self.customers_main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top controls frame
        self.customers_controls_frame = ttk.LabelFrame(self.customers_main_frame, text="Opciones de Reporte")
        self.customers_controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Controls grid
        customers_controls_grid = ttk.Frame(self.customers_controls_frame)
        customers_controls_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Date range
        ttk.Label(customers_controls_grid, text="Periodo:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        # Customer period options
        self.customer_period_var = tk.StringVar(value="all")
        customer_period_frame = ttk.Frame(customers_controls_grid)
        customer_period_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Radiobutton(customer_period_frame, text="Todo", variable=self.customer_period_var, value="all").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(customer_period_frame, text="Año Actual", variable=self.customer_period_var, value="year").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(customer_period_frame, text="Personalizado", variable=self.customer_period_var, value="custom").pack(side=tk.LEFT, padx=5)
        
        # Custom date range for customers
        ttk.Label(customers_controls_grid, text="Desde:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        
        customer_date_frame = ttk.Frame(customers_controls_grid)
        customer_date_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Default to first day of current year
        today = datetime.now()
        first_day_year = datetime(today.year, 1, 1)
        
        self.customer_start_date_var = tk.StringVar(value=first_day_year.strftime("%Y-%m-%d"))
        ttk.Entry(customer_date_frame, textvariable=self.customer_start_date_var, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(customer_date_frame, text="Hasta:").pack(side=tk.LEFT, padx=5)
        self.customer_end_date_var = tk.StringVar(value=today.strftime("%Y-%m-%d"))
        ttk.Entry(customer_date_frame, textvariable=self.customer_end_date_var, width=12).pack(side=tk.LEFT, padx=5)
        
        # Customer count limit
        ttk.Label(customers_controls_grid, text="Mostrar Top:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        
        limit_frame = ttk.Frame(customers_controls_grid)
        limit_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        self.customer_limit_var = tk.StringVar(value="10")
        ttk.Spinbox(limit_frame, from_=5, to=50, increment=5, textvariable=self.customer_limit_var, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(limit_frame, text="clientes").pack(side=tk.LEFT)
        
        # Generate button
        ttk.Button(customers_controls_grid, text="Generar Reporte", command=self.generate_customer_report).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Export buttons frame
        customers_export_frame = ttk.Frame(customers_controls_grid)
        customers_export_frame.grid(row=3, column=1, sticky=tk.E, padx=5, pady=2)
        
        ttk.Button(customers_export_frame, text="Exportar Excel", command=self.export_customers_to_excel).pack(side=tk.LEFT, padx=5)
        
        # Customer report content - top customers list
        self.customers_frame_inner = ttk.Frame(self.customers_main_frame)
        self.customers_frame_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top customers treeview
        self.customers_tree = ttk.Treeview(
            self.customers_frame_inner,
            columns=("Posición", "ID", "Cliente", "Email", "Teléfono", "Compras", "Total", "Última Compra"),
            show="headings"
        )
        self.customers_tree.heading("Posición", text="#")
        self.customers_tree.heading("ID", text="ID")
        self.customers_tree.heading("Cliente", text="Cliente")
        self.customers_tree.heading("Email", text="Email")
        self.customers_tree.heading("Teléfono", text="Teléfono")
        self.customers_tree.heading("Compras", text="Compras")
        self.customers_tree.heading("Total", text="Total")
        self.customers_tree.heading("Última Compra", text="Última Compra")
        
        self.customers_tree.column("Posición", width=40, anchor=tk.CENTER)
        self.customers_tree.column("ID", width=50, anchor=tk.CENTER)
        self.customers_tree.column("Cliente", width=150)
        self.customers_tree.column("Email", width=150)
        self.customers_tree.column("Teléfono", width=100)
        self.customers_tree.column("Compras", width=80, anchor=tk.CENTER)
        self.customers_tree.column("Total", width=100, anchor=tk.E)
        self.customers_tree.column("Última Compra", width=120)
        
        # Scrollbar for customers tree
        customers_scrollbar = ttk.Scrollbar(self.customers_frame_inner, orient="vertical", command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=customers_scrollbar.set)
        
        # Pack the tree and scrollbar
        self.customers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        customers_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
    def on_tab_changed(self, event):
        """
        Handle notebook tab change events.
        
        Args:
            event: Tkinter event
        """
        tab_id = self.notebook.select()
        tab_name = self.notebook.tab(tab_id, "text")
        
        if tab_name == "Ventas":
            self.load_sales_summary()
        elif tab_name == "Inventario":
            self.load_inventory_summary()
        elif tab_name == "Clientes":
            self.load_top_customers()
    
    def generate_sales_report(self):
        """
        Generate sales report based on selected options.
        """
        # Get date range
        period = self.period_var.get()
        today = datetime.now()
        
        if period == "month":
            # Current month
            start_date = datetime(today.year, today.month, 1).isoformat()
            end_date = today.isoformat()
        elif period == "quarter":
            # Current quarter
            current_quarter = (today.month - 1) // 3 + 1
            quarter_start_month = (current_quarter - 1) * 3 + 1
            start_date = datetime(today.year, quarter_start_month, 1).isoformat()
            end_date = today.isoformat()
        elif period == "year":
            # Current year
            start_date = datetime(today.year, 1, 1).isoformat()
            end_date = today.isoformat()
        else:
            # Custom range
            try:
                start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d").isoformat()
                end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d").isoformat()
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                return
        
        # Get report type
        report_type = self.report_type_var.get()
        
        try:
            # Generate report data
            if report_type == "summary":
                self.current_report_data = self.report_controller.generate_sales_report_data(start_date, end_date)
                self.display_sales_summary(self.current_report_data)
                
            elif report_type == "category":
                category_data = self.report_controller.get_sales_by_category(start_date, end_date)
                self.display_category_sales(category_data, start_date, end_date)
                
            elif report_type == "payment":
                payment_data = self.sale_controller.get_sales_by_payment_method(start_date, end_date)
                self.display_payment_method_sales(payment_data, start_date, end_date)
                
            elif report_type == "top_products":
                top_products = self.sale_controller.get_top_selling_products(10, start_date, end_date)
                self.display_top_products(top_products, start_date, end_date)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def display_sales_summary(self, report_data):
        """
        Display sales summary report.
        
        Args:
            report_data: Dictionary with sales report data
        """
        # Update summary values
        self.total_sales_var.set(str(report_data["totals"]["sale_count"]))
        self.total_amount_var.set(f"${report_data['totals']['total_amount']:.2f}")
        
        if report_data["totals"]["sale_count"] > 0:
            self.average_sale_var.set(f"${report_data['totals']['average_sale']:.2f}")
        else:
            self.average_sale_var.set("$0.00")
            
        # Update payment methods tree
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)
            
        for payment in report_data["payment_methods"]:
            self.payment_tree.insert(
                "",
                "end",
                values=(
                    payment["method"],
                    payment["count"],
                    f"${payment['total']:.2f}",
                    f"{payment['percentage']:.1f}%"
                )
            )
            
        # Update details tree - set up columns for period data
        self.details_tree["columns"] = ("Periodo", "Ventas", "Total", "Promedio")
        self.details_tree.heading("Periodo", text="Periodo")
        self.details_tree.heading("Ventas", text="Ventas")
        self.details_tree.heading("Total", text="Total")
        self.details_tree.heading("Promedio", text="Promedio")
        
        self.details_tree.column("Periodo", width=120)
        self.details_tree.column("Ventas", width=80, anchor=tk.CENTER)
        self.details_tree.column("Total", width=100, anchor=tk.E)
        self.details_tree.column("Promedio", width=100, anchor=tk.E)
        
        # Clear the details tree
        for item in self.details_tree.get_children():
            self.details_tree.delete(item)
            
        # Get period sales data
        try:
            # Get appropriate period type
            start_date = report_data["period"]["start_date"]
            end_date = report_data["period"]["end_date"]
            
            # Calculate date difference
            start_dt = datetime.fromisoformat(start_date.split("T")[0])
            end_dt = datetime.fromisoformat(end_date.split("T")[0])
            days_diff = (end_dt - start_dt).days
            
            # Choose appropriate period grouping
            if days_diff <= 31:
                period_type = "daily"
            elif days_diff <= 90:
                period_type = "weekly"
            else:
                period_type = "monthly"
                
            # Get sales by period
            period_data = self.report_controller.get_sales_by_period(period_type, start_date, end_date)
            
            # Add to details tree
            for period in period_data:
                self.details_tree.insert(
                    "",
                    "end",
                    values=(
                        period["period_label"],
                        period["sale_count"],
                        f"${period['total_sales']:.2f}",
                        f"${period['average_sale']:.2f}" if period["sale_count"] > 0 else "$0.00"
                    )
                )
                
            # Create chart
            self.create_sales_chart(period_data, "Ventas por Periodo")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos por periodo: {str(e)}")
    
    def display_category_sales(self, category_data, start_date, end_date):
        """
        Display sales by category report.
        
        Args:
            category_data: List of dictionaries with category sales data
            start_date: Start date string
            end_date: End date string
        """
        # Update summary values
        total_sales = sum(category["total_sales"] for category in category_data)
        total_count = sum(category["sale_count"] for category in category_data)
        total_units = sum(category["units_sold"] for category in category_data)
        
        self.total_sales_var.set(str(total_count))
        self.total_amount_var.set(f"${total_sales:.2f}")
        
        if total_count > 0:
            average_sale = total_sales / total_count
            self.average_sale_var.set(f"${average_sale:.2f}")
        else:
            self.average_sale_var.set("$0.00")
            
        # Update details tree - set up columns for category data
        self.details_tree["columns"] = ("Categoría", "Ventas", "Unidades", "Total", "Porcentaje")
        self.details_tree.heading("Categoría", text="Categoría")
        self.details_tree.heading("Ventas", text="Ventas")
        self.details_tree.heading("Unidades", text="Unidades")
        self.details_tree.heading("Total", text="Total")
        self.details_tree.heading("Porcentaje", text="Porcentaje")
        
        self.details_tree.column("Categoría", width=150)
        self.details_tree.column("Ventas", width=80, anchor=tk.CENTER)
        self.details_tree.column("Unidades", width=80, anchor=tk.CENTER)
        self.details_tree.column("Total", width=100, anchor=tk.E)
        self.details_tree.column("Porcentaje", width=100, anchor=tk.CENTER)
        
        # Clear the details tree
        for item in self.details_tree.get_children():
            self.details_tree.delete(item)
            
        # Add categories to tree
        for category in category_data:
            percentage = (category["total_sales"] / total_sales * 100) if total_sales > 0 else 0
            self.details_tree.insert(
                "",
                "end",
                values=(
                    category["category"],
                    category["sale_count"],
                    category["units_sold"],
                    f"${category['total_sales']:.2f}",
                    f"{percentage:.1f}%"
                )
            )
            
        # Create chart
        self.create_category_chart(category_data, "Ventas por Categoría")
        
    def display_payment_method_sales(self, payment_data, start_date, end_date):
        """
        Display sales by payment method report.
        
        Args:
            payment_data: Dictionary with payment methods as keys
            start_date: Start date string
            end_date: End date string
        """
        # Update summary values
        total_sales = sum(method_data["total"] for method_data in payment_data.values())
        total_count = sum(method_data["count"] for method_data in payment_data.values())
        
        self.total_sales_var.set(str(total_count))
        self.total_amount_var.set(f"${total_sales:.2f}")
        
        if total_count > 0:
            average_sale = total_sales / total_count
            self.average_sale_var.set(f"${average_sale:.2f}")
        else:
            self.average_sale_var.set("$0.00")
            
        # Update payment methods tree
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)
            
        for method, data in payment_data.items():
            percentage = (data["total"] / total_sales * 100) if total_sales > 0 else 0
            self.payment_tree.insert(
                "",
                "end",
                values=(
                    method,
                    data["count"],
                    f"${data['total']:.2f}",
                    f"{percentage:.1f}%"
                )
            )
            
        # Create chart
        self.create_payment_chart(payment_data, "Ventas por Método de Pago")
        
        # We don't have detailed data for this report, so clear the details tree
        self.details_tree["columns"] = ()
        for item in self.details_tree.get_children():
            self.details_tree.delete(item)
    
    def display_top_products(self, top_products, start_date, end_date):
        """
        Display top selling products report.
        
        Args:
            top_products: List of dictionaries with top products data
            start_date: Start date string
            end_date: End date string
        """
        # Update summary values
        total_sales = sum(product["total_amount"] for product in top_products)
        total_units = sum(product["total_quantity"] for product in top_products)
        
        self.total_sales_var.set(str(len(top_products)))
        self.total_amount_var.set(f"${total_sales:.2f}")
        
        average_price = total_sales / total_units if total_units > 0 else 0
        self.average_sale_var.set(f"${average_price:.2f}")
        
        # Update details tree - set up columns for products data
        self.details_tree["columns"] = ("Posición", "Código", "Producto", "Categoría", "Cantidad", "Total", "Porcentaje")
        self.details_tree.heading("Posición", text="#")
        self.details_tree.heading("Código", text="Código")
        self.details_tree.heading("Producto", text="Producto")
        self.details_tree.heading("Categoría", text="Categoría")
        self.details_tree.heading("Cantidad", text="Cantidad")
        self.details_tree.heading("Total", text="Total")
        self.details_tree.heading("Porcentaje", text="Porcentaje")
        
        self.details_tree.column("Posición", width=40, anchor=tk.CENTER)
        self.details_tree.column("Código", width=80)
        self.details_tree.column("Producto", width=150)
        self.details_tree.column("Categoría", width=100)
        self.details_tree.column("Cantidad", width=80, anchor=tk.CENTER)
        self.details_tree.column("Total", width=100, anchor=tk.E)
        self.details_tree.column("Porcentaje", width=80, anchor=tk.CENTER)
        
        # Clear the details tree
        for item in self.details_tree.get_children():
            self.details_tree.delete(item)
            
        # Add products to tree
        for i, product in enumerate(top_products, 1):
            percentage = (product["total_amount"] / total_sales * 100) if total_sales > 0 else 0
            self.details_tree.insert(
                "",
                "end",
                values=(
                    i,
                    product["code"],
                    product["name"],
                    product["category"],
                    product["total_quantity"],
                    f"${product['total_amount']:.2f}",
                    f"{percentage:.1f}%"
                )
            )
            
        # Create chart
        self.create_top_products_chart(top_products, "Productos Más Vendidos")
    
    def load_sales_summary(self):
        """
        Load and display the default sales summary.
        """
        # Default to current month
        today = datetime.now()
        start_date = datetime(today.year, today.month, 1).isoformat()
        end_date = today.isoformat()
        
        try:
            # Generate report data
            self.current_report_data = self.report_controller.generate_sales_report_data(start_date, end_date)
            self.display_sales_summary(self.current_report_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar resumen de ventas: {str(e)}")
    
    def load_inventory_summary(self):
        """
        Load and display the default inventory summary.
        """
        self.generate_inventory_report()
    
    def generate_inventory_report(self):
        """
        Generate inventory report based on selected options.
        """
        report_type = self.inventory_report_type_var.get()
        
        try:
            if report_type == "value":
                inventory_data = self.report_controller.get_inventory_value()
                self.display_inventory_value(inventory_data)
                
            elif report_type == "category":
                category_data = self.inventory_controller.get_stock_by_category()
                self.display_inventory_by_category(category_data)
                
            elif report_type == "low_stock":
                low_stock_data = self.inventory_controller.get_low_stock_items(5)
                out_of_stock_data = self.inventory_controller.get_out_of_stock_items()
                self.display_low_stock(low_stock_data, out_of_stock_data)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte de inventario: {str(e)}")
    
    def display_inventory_value(self, inventory_data):
        """
        Display inventory value report.
        
        Args:
            inventory_data: Dictionary with inventory value data
        """
        # Update summary values
        self.inventory_value_var.set(f"${inventory_data['total_value']:.2f}")
        self.product_count_var.set(str(inventory_data['product_count']))
        self.units_count_var.set(str(inventory_data['total_units']))
        
        # Configure inventory tree columns
        self.inventory_tree["columns"] = ("Categoría", "Productos", "Unidades", "Valor", "Porcentaje")
        self.inventory_tree.heading("Categoría", text="Categoría")
        self.inventory_tree.heading("Productos", text="Productos")
        self.inventory_tree.heading("Unidades", text="Unidades")
        self.inventory_tree.heading("Valor", text="Valor")
        self.inventory_tree.heading("Porcentaje", text="Porcentaje")
        
        self.inventory_tree.column("Categoría", width=150)
        self.inventory_tree.column("Productos", width=80, anchor=tk.CENTER)
        self.inventory_tree.column("Unidades", width=80, anchor=tk.CENTER)
        self.inventory_tree.column("Valor", width=100, anchor=tk.E)
        self.inventory_tree.column("Porcentaje", width=80, anchor=tk.CENTER)
        
        # Clear the inventory tree
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
            
        # Add categories to tree
        for category in inventory_data['categories']:
            percentage = (category['value'] / inventory_data['total_value'] * 100) if inventory_data['total_value'] > 0 else 0
            self.inventory_tree.insert(
                "",
                "end",
                values=(
                    category['name'],
                    category['product_count'],
                    category['units'],
                    f"${category['value']:.2f}",
                    f"{percentage:.1f}%"
                )
            )
            
        # Create chart
        self.create_inventory_value_chart(inventory_data['categories'], "Valor de Inventario por Categoría")
    
    def display_inventory_by_category(self, category_data):
        """
        Display inventory by category report.
        
        Args:
            category_data: List of tuples with category stock data
        """
        # Process data for summary
        categories = []
        total_units = 0
        total_products = 0
        
        for data in category_data:
            category_name = data[0]
            product_count = data[1]
            stock_count = data[2]
            
            categories.append({
                'name': category_name,
                'product_count': product_count,
                'units': stock_count
            })
            
            total_products += product_count
            total_units += stock_count
            
        # Update summary values
        self.product_count_var.set(str(total_products))
        self.units_count_var.set(str(total_units))
        self.inventory_value_var.set("N/A")  # We don't have value data in this report
        
        # Configure inventory tree columns
        self.inventory_tree["columns"] = ("Categoría", "Productos", "Unidades", "Porcentaje")
        self.inventory_tree.heading("Categoría", text="Categoría")
        self.inventory_tree.heading("Productos", text="Productos")
        self.inventory_tree.heading("Unidades", text="Unidades")
        self.inventory_tree.heading("Porcentaje", text="Porcentaje")
        
        self.inventory_tree.column("Categoría", width=150)
        self.inventory_tree.column("Productos", width=80, anchor=tk.CENTER)
        self.inventory_tree.column("Unidades", width=80, anchor=tk.CENTER)
        self.inventory_tree.column("Porcentaje", width=80, anchor=tk.CENTER)
        
        # Clear the inventory tree
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
            
        # Add categories to tree
        for category in categories:
            percentage = (category['units'] / total_units * 100) if total_units > 0 else 0
            self.inventory_tree.insert(
                "",
                "end",
                values=(
                    category['name'],
                    category['product_count'],
                    category['units'],
                    f"{percentage:.1f}%"
                )
            )
            
        # Create chart
        self.create_inventory_stock_chart(categories, "Stock por Categoría")
    
    def display_low_stock(self, low_stock_data, out_of_stock_data):
        """
        Display low stock report.
        
        Args:
            low_stock_data: List of tuples with low stock data
            out_of_stock_data: List of tuples with out of stock data
        """
        # Process data for display
        low_stock_items = []
        
        for data in low_stock_data:
            product_id = data[0]
            product_code = data[1]
            product_name = data[2]
            variant_id = data[3]
            size = data[4]
            color = data[5]
            quantity = data[6]
            
            low_stock_items.append({
                'product_id': product_id,
                'product_code': product_code,
                'product_name': product_name,
                'variant_id': variant_id,
                'variant': f"{color} - Talla {size}",
                'quantity': quantity,
                'status': 'Bajo'
            })
            
        for data in out_of_stock_data:
            product_id = data[0]
            product_code = data[1]
            product_name = data[2]
            variant_id = data[3]
            size = data[4]
            color = data[5]
            quantity = data[6]
            
            low_stock_items.append({
                'product_id': product_id,
                'product_code': product_code,
                'product_name': product_name,
                'variant_id': variant_id,
                'variant': f"{color} - Talla {size}",
                'quantity': quantity,
                'status': 'Agotado'
            })
            
        # Update summary values
        self.product_count_var.set(str(len(low_stock_items)))
        self.units_count_var.set(str(sum(item['quantity'] for item in low_stock_items)))
        self.inventory_value_var.set("N/A")  # We don't have value data in this report
        
        # Configure inventory tree columns
        self.inventory_tree["columns"] = ("Código", "Producto", "Variante", "Stock", "Estado")
        self.inventory_tree.heading("Código", text="Código")
        self.inventory_tree.heading("Producto", text="Producto")
        self.inventory_tree.heading("Variante", text="Variante")
        self.inventory_tree.heading("Stock", text="Stock")
        self.inventory_tree.heading("Estado", text="Estado")
        
        self.inventory_tree.column("Código", width=80)
        self.inventory_tree.column("Producto", width=150)
        self.inventory_tree.column("Variante", width=150)
        self.inventory_tree.column("Stock", width=80, anchor=tk.CENTER)
        self.inventory_tree.column("Estado", width=80)
        
        # Clear the inventory tree
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
            
        # Add items to tree
        for item in low_stock_items:
            self.inventory_tree.insert(
                "",
                "end",
                values=(
                    item['product_code'],
                    item['product_name'],
                    item['variant'],
                    item['quantity'],
                    item['status']
                )
            )
            
        # Create chart for low stock
        self.create_low_stock_chart(low_stock_items, "Productos con Stock Bajo o Agotado")
    
    def load_top_customers(self):
        """
        Load and display the default top customers report.
        """
        self.generate_customer_report()
    
    def generate_customer_report(self):
        """
        Generate customers report based on selected options.
        """
        # Get date range
        period = self.customer_period_var.get()
        today = datetime.now()
        
        if period == "all":
            # All time
            start_date = None
            end_date = None
        elif period == "year":
            # Current year
            start_date = datetime(today.year, 1, 1).isoformat()
            end_date = today.isoformat()
        else:
            # Custom range
            try:
                start_date = datetime.strptime(self.customer_start_date_var.get(), "%Y-%m-%d").isoformat()
                end_date = datetime.strptime(self.customer_end_date_var.get(), "%Y-%m-%d").isoformat()
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                return
        
        # Get customer limit
        try:
            limit = int(self.customer_limit_var.get())
        except ValueError:
            limit = 10
        
        try:
            # Get top customers
            top_customers = self.report_controller.get_top_customers(limit, start_date, end_date)
            self.display_top_customers(top_customers)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte de clientes: {str(e)}")
    
    def display_top_customers(self, customers_data):
        """
        Display top customers report.
        
        Args:
            customers_data: List of dictionaries with customer data
        """
        # Clear the customers tree
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
            
        # Add customers to tree
        for i, customer in enumerate(customers_data, 1):
            # Format date
            last_purchase = customer["last_purchase"]
            try:
                dt = datetime.fromisoformat(last_purchase)
                last_purchase = dt.strftime("%Y-%m-%d")
            except:
                pass
                
            self.customers_tree.insert(
                "",
                "end",
                values=(
                    i,
                    customer["id"],
                    customer["name"],
                    customer["email"] or "",
                    customer["phone"] or "",
                    customer["purchase_count"],
                    f"${customer['total_spent']:.2f}",
                    last_purchase
                )
            )
            
    # Chart creation methods
    def create_sales_chart(self, period_data, title):
        """
        Create a line chart for sales by period.
        
        Args:
            period_data: List of dictionaries with period sales data
            title: Chart title
        """
        # Clear previous chart
        for widget in self.chart_container.winfo_children():
            widget.destroy()
            
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Extract data
        periods = [p["period_label"] for p in period_data]
        sales = [p["total_sales"] for p in period_data]
        
        # Create line chart
        ax.plot(periods, sales, marker='o', linestyle='-', color='blue')
        
        # Set labels and title
        ax.set_xlabel('Periodo')
        ax.set_ylabel('Ventas ($)')
        ax.set_title(title)
        
        # Rotate x-axis labels for better visibility
        plt.xticks(rotation=45, ha='right')
        
        # Tight layout to ensure everything fits
        fig.tight_layout()
        
        # Add to container
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_category_chart(self, category_data, title):
        """
        Create a pie chart for sales by category.
        
        Args:
            category_data: List of dictionaries with category sales data
            title: Chart title
        """
        # Clear previous chart
        for widget in self.chart_container.winfo_children():
            widget.destroy()
            
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Extract data
        categories = [c["category"] for c in category_data]
        sales = [c["total_sales"] for c in category_data]
        
        # Create pie chart
        ax.pie(sales, labels=categories, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Set title
        ax.set_title(title)
        
        # Tight layout to ensure everything fits
        fig.tight_layout()
        
        # Add to container
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_payment_chart(self, payment_data, title):
        """
        Create a pie chart for sales by payment method.
        
        Args:
            payment_data: Dictionary with payment methods as keys
            title: Chart title
        """
        # Clear previous chart
        for widget in self.chart_container.winfo_children():
            widget.destroy()
            
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Extract data
        methods = list(payment_data.keys())
        totals = [data["total"] for data in payment_data.values()]
        
        # Create bar chart
        ax.bar(methods, totals, color='blue')
        
        # Set labels and title
        ax.set_xlabel('Método de Pago')
        ax.set_ylabel('Ventas ($)')
        ax.set_title(title)
        
        # Add value labels on top of bars
        for i, v in enumerate(totals):
            ax.text(i, v + 0.1, f"${v:.2f}", ha='center')
        
        # Tight layout to ensure everything fits
        fig.tight_layout()
        
        # Add to container
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_top_products_chart(self, top_products, title):
        """
        Create a bar chart for top selling products.
        
        Args:
            top_products: List of dictionaries with top products data
            title: Chart title
        """
        # Clear previous chart
        for widget in self.chart_container.winfo_children():
            widget.destroy()
            
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Extract data (limit to top 10 for readability)
        products = [p["name"] for p in top_products[:10]]
        quantities = [p["total_quantity"] for p in top_products[:10]]
        
        # Shorten long product names
        products = [p[:15] + '...' if len(p) > 15 else p for p in products]
        
        # Create horizontal bar chart
        ax.barh(products, quantities, color='green')
        
        # Set labels and title
        ax.set_xlabel('Unidades Vendidas')
        ax.set_ylabel('Producto')
        ax.set_title(title)
        
        # Add quantity labels
        for i, v in enumerate(quantities):
            ax.text(v + 0.1, i, str(v), va='center')
        
        # Tight layout to ensure everything fits
        fig.tight_layout()
        
        # Add to container
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_inventory_value_chart(self, categories, title):
        """
        Create a pie chart for inventory value by category.
        
        Args:
            categories: List of dictionaries with category value data
            title: Chart title
        """
        # Clear previous chart
        for widget in self.inventory_chart_container.winfo_children():
            widget.destroy()
            
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Extract data
        category_names = [c["name"] for c in categories]
        values = [c["value"] for c in categories]
        
        # Create pie chart
        ax.pie(values, labels=category_names, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Set title
        ax.set_title(title)
        
        # Tight layout to ensure everything fits
        fig.tight_layout()
        
        # Add to container
        canvas = FigureCanvasTkAgg(fig, master=self.inventory_chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_inventory_stock_chart(self, categories, title):
        """
        Create a bar chart for inventory stock by category.
        
        Args:
            categories: List of dictionaries with category stock data
            title: Chart title
        """
        # Clear previous chart
        for widget in self.inventory_chart_container.winfo_children():
            widget.destroy()
            
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Extract data
        category_names = [c["name"] for c in categories]
        units = [c["units"] for c in categories]
        
        # Create bar chart
        ax.bar(category_names, units, color='blue')
        
        # Set labels and title
        ax.set_xlabel('Categoría')
        ax.set_ylabel('Unidades en Stock')
        ax.set_title(title)
        
        # Rotate x-axis labels for better visibility
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on top of bars
        for i, v in enumerate(units):
            ax.text(i, v + 0.1, str(v), ha='center')
        
        # Tight layout to ensure everything fits
        fig.tight_layout()
        
        # Add to container
        canvas = FigureCanvasTkAgg(fig, master=self.inventory_chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_low_stock_chart(self, items, title):
        """
        Create a chart for low stock items.
        
        Args:
            items: List of dictionaries with low stock data
            title: Chart title
        """
        # Clear previous chart
        for widget in self.inventory_chart_container.winfo_children():
            widget.destroy()
            
        # Count items by status
        status_counts = {"Bajo": 0, "Agotado": 0}
        for item in items:
            status_counts[item["status"]] += 1
            
        # If no data, show message
        if sum(status_counts.values()) == 0:
            message = ttk.Label(
                self.inventory_chart_container,
                text="No hay productos con stock bajo o agotado",
                font=("Arial", 14),
                anchor=tk.CENTER
            )
            message.pack(fill=tk.BOTH, expand=True)
            return
            
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Create pie chart
        statuses = list(status_counts.keys())
        counts = list(status_counts.values())
        
        # Create pie chart
        ax.pie(counts, labels=statuses, autopct='%1.1f%%', startangle=90,
               colors=['orange', 'red'] if "Agotado" in statuses else ['orange'])
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Set title
        ax.set_title(title)
        
        # Tight layout to ensure everything fits
        fig.tight_layout()
        
        # Add to container
        canvas = FigureCanvasTkAgg(fig, master=self.inventory_chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Export methods
    def export_to_excel(self):
        """
        Export current sales report data to Excel.
        """
        if not self.current_report_data:
            messagebox.showinfo("Información", "No hay datos para exportar")
            return
            
        try:
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Guardar reporte como"
            )
            
            if not file_path:
                return
                
            # Create Excel writer
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Export summary data
                summary_data = {
                    'Métrica': ['Total Ventas', 'Monto Total', 'Promedio por Venta'],
                    'Valor': [
                        self.current_report_data["totals"]["sale_count"],
                        self.current_report_data["totals"]["total_amount"],
                        self.current_report_data["totals"]["average_sale"]
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Resumen', index=False)
                
                # Export payment methods
                payment_data = []
                for payment in self.current_report_data["payment_methods"]:
                    payment_data.append({
                        'Método': payment["method"],
                        'Cantidad': payment["count"],
                        'Total': payment["total"],
                        'Porcentaje': payment["percentage"]
                    })
                pd.DataFrame(payment_data).to_excel(writer, sheet_name='Métodos de Pago', index=False)
                
                # Export top products
                product_data = []
                for product in self.current_report_data["top_products"]:
                    product_data.append({
                        'ID': product["id"],
                        'Nombre': product["name"],
                        'Categoría': product["category"],
                        'Cantidad Vendida': product["quantity_sold"],
                        'Total Vendido': product["total_sold"]
                    })
                pd.DataFrame(product_data).to_excel(writer, sheet_name='Productos Más Vendidos', index=False)
                
                # Export category sales
                category_data = []
                for category in self.current_report_data["category_sales"]:
                    category_data.append({
                        'Categoría': category["category"],
                        'Ventas': category["sale_count"],
                        'Unidades Vendidas': category["units_sold"],
                        'Total Vendido': category["total_sales"]
                    })
                pd.DataFrame(category_data).to_excel(writer, sheet_name='Ventas por Categoría', index=False)
                
            messagebox.showinfo("Éxito", f"Reporte exportado correctamente a\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar reporte: {str(e)}")
    
    def export_inventory_to_excel(self):
        """
        Export current inventory report data to Excel.
        """
        try:
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Guardar reporte como"
            )
            
            if not file_path:
                return
                
            # Get inventory data
            inventory_data = self.report_controller.generate_inventory_report_data()
            
            # Create Excel writer
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Export summary data
                summary_data = {
                    'Métrica': ['Valor Total de Inventario', 'Total de Productos', 'Total de Unidades'],
                    'Valor': [
                        inventory_data["total_value"],
                        inventory_data["product_count"],
                        inventory_data["total_units"]
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Resumen', index=False)
                
                # Export category data
                category_data = []
                for category in inventory_data["categories"]:
                    category_data.append({
                        'Categoría': category["name"],
                        'Productos': category["product_count"],
                        'Unidades': category["units"],
                        'Valor': category["value"]
                    })
                pd.DataFrame(category_data).to_excel(writer, sheet_name='Por Categoría', index=False)
                
                # Export low stock data
                low_stock_data = []
                for item in inventory_data["low_stock"]:
                    low_stock_data.append({
                        'Código': item["code"],
                        'Producto': item["name"],
                        'Categoría': item["category"],
                        'Talla': item["size"],
                        'Color': item["color"],
                        'Stock': item["quantity"],
                        'Estado': 'Bajo'
                    })
                for item in inventory_data["out_of_stock"]:
                    low_stock_data.append({
                        'Código': item["code"],
                        'Producto': item["name"],
                        'Categoría': item["category"],
                        'Talla': item["size"],
                        'Color': item["color"],
                        'Stock': item["quantity"],
                        'Estado': 'Agotado'
                    })
                pd.DataFrame(low_stock_data).to_excel(writer, sheet_name='Stock Bajo', index=False)
                
            messagebox.showinfo("Éxito", f"Reporte exportado correctamente a\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar reporte: {str(e)}")
    
    def export_customers_to_excel(self):
        """
        Export current customers report data to Excel.
        """
        try:
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Guardar reporte como"
            )
            
            if not file_path:
                return
                
            # Get customers data
            period = self.customer_period_var.get()
            today = datetime.now()
            
            if period == "all":
                # All time
                start_date = None
                end_date = None
            elif period == "year":
                # Current year
                start_date = datetime(today.year, 1, 1).isoformat()
                end_date = today.isoformat()
            else:
                # Custom range
                try:
                    start_date = datetime.strptime(self.customer_start_date_var.get(), "%Y-%m-%d").isoformat()
                    end_date = datetime.strptime(self.customer_end_date_var.get(), "%Y-%m-%d").isoformat()
                except ValueError:
                    messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                    return
            
            # Get customer limit
            try:
                limit = int(self.customer_limit_var.get())
            except ValueError:
                limit = 10
                
            # Get top customers
            top_customers = self.report_controller.get_top_customers(limit, start_date, end_date)
            
            # Create Excel writer
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Export customers data
                customers_data = []
                for i, customer in enumerate(top_customers, 1):
                    customers_data.append({
                        'Posición': i,
                        'ID': customer["id"],
                        'Nombre': customer["name"],
                        'Email': customer["email"] or "",
                        'Teléfono': customer["phone"] or "",
                        'Compras': customer["purchase_count"],
                        'Total Gastado': customer["total_spent"],
                        'Última Compra': customer["last_purchase"]
                    })
                pd.DataFrame(customers_data).to_excel(writer, sheet_name='Top Clientes', index=False)
                
            messagebox.showinfo("Éxito", f"Reporte exportado correctamente a\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar reporte: {str(e)}")