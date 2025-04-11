"""
Report controller for the Clothing Store Management System.
Handles business logic for generating reports and statistics.
"""
import pandas as pd
from datetime import datetime, timedelta


class ReportController:
    """
    Controller for report-related operations.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the report controller.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        
    def get_sales_by_period(self, period_type, start_date=None, end_date=None):
        """
        Get sales statistics grouped by a time period.
        
        Args:
            period_type: 'daily', 'weekly', or 'monthly'
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of dictionaries with period and sales information
        """
        try:
            # Default date range if not provided
            if not end_date:
                end_date = datetime.now().isoformat()
                
            if not start_date:
                if period_type == 'daily':
                    start_date = (datetime.fromisoformat(end_date) - timedelta(days=30)).isoformat()
                elif period_type == 'weekly':
                    start_date = (datetime.fromisoformat(end_date) - timedelta(days=90)).isoformat()
                else:  # monthly
                    start_date = (datetime.fromisoformat(end_date) - timedelta(days=365)).isoformat()
            
            # Construct the query based on period type
            if period_type == 'daily':
                date_format = '%Y-%m-%d'
                group_by = "strftime('%Y-%m-%d', sale_date)"
            elif period_type == 'weekly':
                date_format = '%Y-%W'
                group_by = "strftime('%Y-%W', sale_date)"
            else:  # monthly
                date_format = '%Y-%m'
                group_by = "strftime('%Y-%m', sale_date)"
                
            query = f'''
                SELECT 
                    {group_by} as period,
                    COUNT(*) as sale_count,
                    SUM(total_amount) as total_sales,
                    AVG(total_amount) as average_sale
                FROM sales
                WHERE sale_date BETWEEN ? AND ?
                GROUP BY period
                ORDER BY period
            '''
            
            self.db.execute(query, (start_date, end_date))
            
            results_data = self.db.fetchall()
            results = []
            
            for data in results_data:
                period = data[0]
                
                # Format period for better readability
                if period_type == 'weekly':
                    year, week = period.split('-')
                    period_label = f"Semana {week}, {year}"
                elif period_type == 'monthly':
                    year, month = period.split('-')
                    month_names = [
                        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
                    ]
                    period_label = f"{month_names[int(month)-1]} {year}"
                else:
                    period_label = period
                
                result = {
                    'period': period,
                    'period_label': period_label,
                    'sale_count': data[1],
                    'total_sales': data[2],
                    'average_sale': data[3]
                }
                
                results.append(result)
                
            return results
            
        except Exception as e:
            raise Exception(f"Error getting sales by period: {str(e)}")
    
    def get_sales_by_category(self, start_date=None, end_date=None):
        """
        Get sales statistics grouped by product category.
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of dictionaries with category and sales information
        """
        try:
            query = '''
                SELECT 
                    c.name as category,
                    COUNT(DISTINCT s.id) as sale_count,
                    SUM(si.quantity) as units_sold,
                    SUM(si.subtotal) as total_sales
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                JOIN product_variants pv ON si.product_variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                JOIN categories c ON p.category_id = c.id
                WHERE 1=1
            '''
            
            params = []
            
            if start_date:
                query += " AND s.sale_date >= ?"
                params.append(start_date)
                
            if end_date:
                query += " AND s.sale_date <= ?"
                params.append(end_date)
                
            query += " GROUP BY c.id ORDER BY total_sales DESC"
            
            self.db.execute(query, params)
            
            results_data = self.db.fetchall()
            results = []
            
            for data in results_data:
                result = {
                    'category': data[0],
                    'sale_count': data[1],
                    'units_sold': data[2],
                    'total_sales': data[3]
                }
                
                results.append(result)
                
            return results
            
        except Exception as e:
            raise Exception(f"Error getting sales by category: {str(e)}")
    
    def get_inventory_value(self):
        """
        Calculate the current value of inventory.
        
        Returns:
            Dictionary with total value and breakdown by category
        """
        try:
            # Get total inventory value
            self.db.execute(
                '''
                SELECT 
                    SUM(i.quantity * p.price) as total_value,
                    COUNT(DISTINCT p.id) as product_count,
                    SUM(i.quantity) as total_units
                FROM inventory i
                JOIN product_variants pv ON i.product_variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                WHERE i.quantity > 0
                '''
            )
            
            total_data = self.db.fetchone()
            
            # Get value by category
            self.db.execute(
                '''
                SELECT 
                    c.name as category,
                    SUM(i.quantity * p.price) as category_value,
                    COUNT(DISTINCT p.id) as product_count,
                    SUM(i.quantity) as total_units
                FROM inventory i
                JOIN product_variants pv ON i.product_variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                JOIN categories c ON p.category_id = c.id
                WHERE i.quantity > 0
                GROUP BY c.id
                ORDER BY category_value DESC
                '''
            )
            
            category_data = self.db.fetchall()
            
            result = {
                'total_value': total_data[0] if total_data[0] else 0,
                'product_count': total_data[1] if total_data[1] else 0,
                'total_units': total_data[2] if total_data[2] else 0,
                'categories': []
            }
            
            for data in category_data:
                category = {
                    'name': data[0],
                    'value': data[1],
                    'product_count': data[2],
                    'units': data[3]
                }
                result['categories'].append(category)
                
            return result
            
        except Exception as e:
            raise Exception(f"Error calculating inventory value: {str(e)}")
    
    def get_top_customers(self, limit=10, start_date=None, end_date=None):
        """
        Get the top customers by purchase amount.
        
        Args:
            limit: Maximum number of customers to return
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of dictionaries with customer and purchase information
        """
        try:
            query = '''
                SELECT 
                    c.id, c.name, c.email, c.phone,
                    COUNT(s.id) as purchase_count,
                    SUM(s.total_amount) as total_spent,
                    MAX(s.sale_date) as last_purchase
                FROM customers c
                JOIN sales s ON c.id = s.customer_id
                WHERE 1=1
            '''
            
            params = []
            
            if start_date:
                query += " AND s.sale_date >= ?"
                params.append(start_date)
                
            if end_date:
                query += " AND s.sale_date <= ?"
                params.append(end_date)
                
            query += " GROUP BY c.id ORDER BY total_spent DESC LIMIT ?"
            params.append(limit)
            
            self.db.execute(query, params)
            
            results_data = self.db.fetchall()
            results = []
            
            for data in results_data:
                customer = {
                    'id': data[0],
                    'name': data[1],
                    'email': data[2],
                    'phone': data[3],
                    'purchase_count': data[4],
                    'total_spent': data[5],
                    'last_purchase': data[6]
                }
                
                results.append(customer)
                
            return results
            
        except Exception as e:
            raise Exception(f"Error getting top customers: {str(e)}")
    
    def generate_sales_report_data(self, start_date=None, end_date=None):
        """
        Generate comprehensive sales report data.
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            Dictionary with various sales statistics
        """
        try:
            # If no dates provided, use last 30 days
            if not end_date:
                end_date = datetime.now().isoformat()
                
            if not start_date:
                start_date = (datetime.fromisoformat(end_date) - timedelta(days=30)).isoformat()
                
            # Get total sales
            self.db.execute(
                '''
                SELECT 
                    COUNT(*) as total_sales,
                    SUM(total_amount) as total_amount,
                    AVG(total_amount) as average_sale
                FROM sales
                WHERE sale_date BETWEEN ? AND ?
                ''',
                (start_date, end_date)
            )
            
            totals_data = self.db.fetchone()
            
            # Get sales by payment method
            self.db.execute(
                '''
                SELECT 
                    payment_method,
                    COUNT(*) as count,
                    SUM(total_amount) as total
                FROM sales
                WHERE sale_date BETWEEN ? AND ?
                GROUP BY payment_method
                ORDER BY total DESC
                ''',
                (start_date, end_date)
            )
            
            payment_data = self.db.fetchall()
            payment_methods = []
            
            for data in payment_data:
                payment = {
                    'method': data[0],
                    'count': data[1],
                    'total': data[2],
                    'percentage': (data[2] / totals_data[1] * 100) if totals_data[1] else 0
                }
                payment_methods.append(payment)
                
            # Get top selling products
            self.db.execute(
                '''
                SELECT 
                    p.id, p.name, c.name as category,
                    SUM(si.quantity) as quantity_sold,
                    SUM(si.subtotal) as total_sold
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                JOIN product_variants pv ON si.product_variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                JOIN categories c ON p.category_id = c.id
                WHERE s.sale_date BETWEEN ? AND ?
                GROUP BY p.id
                ORDER BY quantity_sold DESC
                LIMIT 10
                ''',
                (start_date, end_date)
            )
            
            top_products_data = self.db.fetchall()
            top_products = []
            
            for data in top_products_data:
                product = {
                    'id': data[0],
                    'name': data[1],
                    'category': data[2],
                    'quantity_sold': data[3],
                    'total_sold': data[4]
                }
                top_products.append(product)
                
            # Get sales by category
            category_sales = self.get_sales_by_category(start_date, end_date)
            
            # Assemble the final report
            report = {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'totals': {
                    'sale_count': totals_data[0],
                    'total_amount': totals_data[1],
                    'average_sale': totals_data[2]
                },
                'payment_methods': payment_methods,
                'top_products': top_products,
                'category_sales': category_sales
            }
            
            return report
            
        except Exception as e:
            raise Exception(f"Error generating sales report: {str(e)}")
    
    def generate_inventory_report_data(self):
        """
        Generate comprehensive inventory report data.
        
        Returns:
            Dictionary with various inventory statistics
        """
        try:
            # Get inventory summary
            self.db.execute(
                '''
                SELECT 
                    COUNT(DISTINCT p.id) as product_count,
                    COUNT(pv.id) as variant_count,
                    SUM(i.quantity) as total_units,
                    SUM(i.quantity * p.price) as total_value
                FROM inventory i
                JOIN product_variants pv ON i.product_variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                '''
            )
            
            summary_data = self.db.fetchone()
            
            # Get low stock items
            self.db.execute(
                '''
                SELECT 
                    p.id, p.code, p.name, c.name as category,
                    pv.id as variant_id, pv.size, pv.color, i.quantity
                FROM inventory i
                JOIN product_variants pv ON i.product_variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                JOIN categories c ON p.category_id = c.id
                WHERE i.quantity > 0 AND i.quantity <= 5
                ORDER BY i.quantity, p.name
                '''
            )
            
            low_stock_data = self.db.fetchall()
            low_stock_items = []
            
            for data in low_stock_data:
                item = {
                    'id': data[0],
                    'code': data[1],
                    'name': data[2],
                    'category': data[3],
                    'variant_id': data[4],
                    'size': data[5],
                    'color': data[6],
                    'quantity': data[7]
                }
                low_stock_items.append(item)
                
            # Get out of stock items
            self.db.execute(
                '''
                SELECT 
                    p.id, p.code, p.name, c.name as category,
                    pv.id as variant_id, pv.size, pv.color
                FROM inventory i
                JOIN product_variants pv ON i.product_variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                JOIN categories c ON p.category_id = c.id
                WHERE i.quantity = 0
                ORDER BY p.name
                '''
            )
            
            out_of_stock_data = self.db.fetchall()
            out_of_stock_items = []
            
            for data in out_of_stock_data:
                item = {
                    'id': data[0],
                    'code': data[1],
                    'name': data[2],
                    'category': data[3],
                    'variant_id': data[4],
                    'size': data[5],
                    'color': data[6]
                }
                out_of_stock_items.append(item)
                
            # Get inventory by category
            self.db.execute(
                '''
                SELECT 
                    c.name as category,
                    COUNT(DISTINCT p.id) as product_count,
                    SUM(i.quantity) as total_units,
                    SUM(i.quantity * p.price) as total_value
                FROM inventory i
                JOIN product_variants pv ON i.product_variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                JOIN categories c ON p.category_id = c.id
                GROUP BY c.id
                ORDER BY total_value DESC
                '''
            )
            
            category_data = self.db.fetchall()
            categories = []
            
            for data in category_data:
                category = {
                    'name': data[0],
                    'product_count': data[1],
                    'total_units': data[2],
                    'total_value': data[3]
                }
                categories.append(category)
                
            # Get products with active discounts
            self.db.execute(
                '''
                SELECT 
                    p.id, p.code, p.name, c.name as category,
                    p.price, p.discount_percent,
                    p.discount_start_date, p.discount_end_date,
                    SUM(i.quantity) as total_stock
                FROM products p
                JOIN categories c ON p.category_id = c.id
                JOIN product_variants pv ON p.id = pv.product_id
                JOIN inventory i ON pv.id = i.product_variant_id
                WHERE p.discount_percent > 0
                  AND (
                    (p.discount_start_date IS NULL OR p.discount_start_date <= datetime('now'))
                    AND 
                    (p.discount_end_date IS NULL OR p.discount_end_date >= datetime('now'))
                  )
                GROUP BY p.id
                ORDER BY p.discount_percent DESC
                '''
            )
            
            discounted_data = self.db.fetchall()
            discounted_products = []
            
            for data in discounted_data:
                product = {
                    'id': data[0],
                    'code': data[1],
                    'name': data[2],
                    'category': data[3],
                    'regular_price': data[4],
                    'discount_percent': data[5],
                    'discount_start_date': data[6],
                    'discount_end_date': data[7],
                    'total_stock': data[8],
                    'discounted_price': data[4] * (1 - data[5] / 100)
                }
                discounted_products.append(product)
                
            # Assemble the final report
            report = {
                'summary': {
                    'product_count': summary_data[0],
                    'variant_count': summary_data[1],
                    'total_units': summary_data[2],
                    'total_value': summary_data[3]
                },
                'low_stock': low_stock_items,
                'out_of_stock': out_of_stock_items,
                'categories': categories,
                'discounted_products': discounted_products
            }
            
            return report
            
        except Exception as e:
            raise Exception(f"Error generating inventory report: {str(e)}")
