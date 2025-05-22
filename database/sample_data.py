"""
Script para insertar datos de prueba en la base de datos.
"""
import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import DatabaseManager

def insert_sample_data():
    """Insert sample data into the database."""
    db = DatabaseManager('clothing_store.db')
    
    try:
        # Limpiar datos existentes
        tables = [
            "sale_items",
            "sales",
            "inventory",
            "product_variants",
            "products",
            "categories",
            "customers"
        ]
        
        for table in tables:
            db.execute(f"DELETE FROM {table}")
            
        # Reiniciar los contadores de autoincremento
        for table in tables:
            db.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
            
        # Insertar categorías
        categories = [
            ("Camisetas", "Camisetas y playeras casuales"),
            ("Pantalones", "Jeans y pantalones casuales"),
            ("Vestidos", "Vestidos para toda ocasión"),
            ("Accesorios", "Cinturones, bufandas y más"),
            ("Calzado", "Zapatos y tenis")
        ]
        
        category_ids = {}
        for name, description in categories:
            db.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name, description))
            category_ids[name] = db.cursor.lastrowid
            
        # Insertar productos
        products = [
            # Camisetas
            ("TSH001", "Camiseta Básica", "Camiseta de algodón", category_ids["Camisetas"], 199.99),
            ("TSH002", "Playera Polo", "Playera tipo polo", category_ids["Camisetas"], 299.99),
            ("TSH003", "Camiseta Estampada", "Camiseta con diseño", category_ids["Camisetas"], 249.99),
            
            # Pantalones
            ("PNT001", "Jean Clásico", "Jean corte recto", category_ids["Pantalones"], 599.99),
            ("PNT002", "Pantalón Casual", "Pantalón de vestir", category_ids["Pantalones"], 699.99),
            
            # Vestidos
            ("DRS001", "Vestido Casual", "Vestido para el día", category_ids["Vestidos"], 799.99),
            ("DRS002", "Vestido de Noche", "Vestido elegante", category_ids["Vestidos"], 1299.99),
            
            # Accesorios
            ("ACC001", "Cinturón Cuero", "Cinturón de piel", category_ids["Accesorios"], 299.99),
            ("ACC002", "Bufanda Invierno", "Bufanda tejida", category_ids["Accesorios"], 199.99),
            
            # Calzado
            ("SHO001", "Tenis Casual", "Tenis deportivos", category_ids["Calzado"], 899.99),
            ("SHO002", "Zapatos Formales", "Zapatos de vestir", category_ids["Calzado"], 1099.99)
        ]
        
        now = datetime.now().isoformat()
        product_ids = {}
        
        for code, name, description, category_id, price in products:
            db.execute(
                """
                INSERT INTO products (code, name, description, category_id, price, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (code, name, description, category_id, price, now, now)
            )
            product_ids[code] = db.cursor.lastrowid
            
        # Insertar variantes de productos
        variants = []
        
        # Variantes para camisetas
        for code in ["TSH001", "TSH002", "TSH003"]:
            for size in ["CH", "M", "G", "EG"]:
                for color in ["Negro", "Blanco", "Azul"]:
                    variants.append((product_ids[code], size, color))
        
        # Variantes para pantalones
        for code in ["PNT001", "PNT002"]:
            for size in ["28", "30", "32", "34", "36"]:
                for color in ["Azul", "Negro", "Caqui"]:
                    variants.append((product_ids[code], size, color))
        
        # Variantes para vestidos
        for code in ["DRS001", "DRS002"]:
            for size in ["2", "4", "6", "8", "10"]:
                for color in ["Negro", "Rojo", "Azul"]:
                    variants.append((product_ids[code], size, color))
        
        # Variantes para accesorios
        for code in ["ACC001"]:  # Cinturón
            for size in ["28", "30", "32", "34"]:
                for color in ["Negro", "Café"]:
                    variants.append((product_ids[code], size, color))
                    
        for code in ["ACC002"]:  # Bufanda
            for size in ["Único"]:
                for color in ["Negro", "Gris", "Azul", "Rojo"]:
                    variants.append((product_ids[code], size, color))
        
        # Variantes para calzado
        for code in ["SHO001", "SHO002"]:
            for size in ["25", "26", "27", "28", "29"]:
                for color in ["Negro", "Café"]:
                    variants.append((product_ids[code], size, color))
        
        variant_ids = {}
        for product_id, size, color in variants:
            db.execute(
                "INSERT INTO product_variants (product_id, size, color) VALUES (?, ?, ?)",
                (product_id, size, color)
            )
            variant_id = db.cursor.lastrowid
            variant_ids[(product_id, size, color)] = variant_id
            
            # Insertar inventario inicial
            db.execute(
                "INSERT INTO inventory (product_variant_id, quantity, last_updated) VALUES (?, ?, ?)",
                (variant_id, 10, now)  # Cada variante inicia con 10 unidades
            )
        
        # Insertar clientes
        customers = [
            ("Juan Pérez", "juan@email.com", "5551234567", "Calle 1 #123"),
            ("María García", "maria@email.com", "5552345678", "Av. Principal #456"),
            ("Carlos López", "carlos@email.com", "5553456789", "Plaza Central #789"),
            ("Ana Martínez", "ana@email.com", "5554567890", "Calle 2 #321"),
            ("Roberto Sánchez", "roberto@email.com", "5555678901", "Av. Segunda #654")
        ]
        
        customer_ids = {}
        for name, email, phone, address in customers:
            db.execute(
                """
                INSERT INTO customers (name, email, phone, address, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name, email, phone, address, now, now)
            )
            customer_ids[name] = db.cursor.lastrowid
        
        # Insertar ventas de ejemplo
        for i in range(20):  # 20 ventas de ejemplo
            # Elegir un cliente aleatorio
            customer_id = list(customer_ids.values())[i % len(customer_ids)]
            
            # Fecha de venta en los últimos 30 días
            sale_date = (datetime.now() - timedelta(days=i)).isoformat()
            
            # Método de pago alternado
            payment_method = ["EFECTIVO", "TARJETA", "TRANSFERENCIA"][i % 3]
            
            # Crear la venta
            db.execute(
                """
                INSERT INTO sales (customer_id, sale_date, payment_method, total_amount)
                VALUES (?, ?, ?, ?)
                """,
                (customer_id, sale_date, payment_method, 0)  # Total se actualizará después
            )
            sale_id = db.cursor.lastrowid
            
            # Agregar 2-4 items a la venta
            total_amount = 0
            for j in range(2 + (i % 3)):  # 2 a 4 items por venta
                # Seleccionar una variante aleatoria
                variant_id = list(variant_ids.values())[(i + j) % len(variant_ids)]
                
                # Obtener el precio del producto
                db.execute(
                    """
                    SELECT p.price
                    FROM products p
                    JOIN product_variants pv ON p.id = pv.product_id
                    WHERE pv.id = ?
                    """,
                    (variant_id,)
                )
                price = db.fetchone()[0]
                
                # Cantidad aleatoria entre 1 y 3
                quantity = 1 + (i % 3)
                subtotal = price * quantity
                total_amount += subtotal
                
                # Insertar el item de venta
                db.execute(
                    """
                    INSERT INTO sale_items (sale_id, product_variant_id, quantity, unit_price, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (sale_id, variant_id, quantity, price, subtotal)
                )
                
                # Actualizar el inventario
                db.execute(
                    """
                    UPDATE inventory
                    SET quantity = quantity - ?,
                        last_updated = ?
                    WHERE product_variant_id = ?
                    """,
                    (quantity, now, variant_id)
                )
            
            # Actualizar el total de la venta
            db.execute(
                "UPDATE sales SET total_amount = ? WHERE id = ?",
                (total_amount, sale_id)
            )
        
        # Confirmar todos los cambios
        db.commit()
        print("Datos de prueba insertados correctamente")
        
    except Exception as e:
        print(f"Error al insertar datos de prueba: {str(e)}")
        db.conn.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    insert_sample_data() 