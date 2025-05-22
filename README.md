# Manual de Usuario - Sistema de Gestión para Tienda de Ropa Mis Trapitos

## Descripción General
Proyecto final para la materia de Ingeniería del Software
Integrantes del Equipo:
- Israel López Garcia
- Diego Alejandro Guzmán Paniagua
- Fabricio Sabdi Santillán Hernández
- Gian Carlo Tapia Jasso
- Jesús Antonio Torres Contreras

Asesor: Arreola González Mauricio Rodolfo
Este sistema de gestión está diseñado específicamente para tiendas de ropa, permitiendo administrar de manera integral todos los aspectos del negocio: productos, inventario, clientes, ventas, proveedores y reportes.

## Requisitos del Sistema

- Sistema operativo: Windows, macOS o Linux
- Python 3.8 o superior
- Tkinter (incluido en la mayoría de instalaciones de Python)
- Espacio en disco: 100MB mínimo
- RAM: 2GB mínimo recomendado

## Instalación

1. Asegúrese de tener Python 3.8 o superior instalado en su sistema.
2. Clone o descargue este repositorio en su equipo.
3. Abra una terminal o línea de comandos en la carpeta del proyecto.
4. Ejecute el programa con el siguiente comando:

```
python main.py
```

## Funcionalidades Principales

El sistema está organizado en seis módulos principales, accesibles desde la barra de navegación superior:

### 1. Ventas

Este módulo permite:
- Registrar nuevas ventas
- Buscar ventas anteriores por fecha, cliente o productos
- Generar tickets de venta
- Aplicar descuentos
- Seleccionar productos del inventario
- Asociar la venta a un cliente registrado

### 2. Productos

En esta sección puede:
- Añadir nuevos productos al catálogo
- Editar información de productos existentes
- Eliminar productos del catálogo
- Ver detalles como precio, categoría, descripción y tallas disponibles
- Asignar productos a proveedores

### 3. Inventario

El módulo de inventario permite:
- Controlar el stock de cada producto
- Registrar entradas y salidas de mercancía
- Ver alertas de productos con bajo stock
- Hacer ajustes de inventario
- Seguimiento por tallas y colores

### 4. Clientes

Permite gestionar:
- Registro de datos personales de clientes
- Historial de compras por cliente
- Preferencias de productos
- Información de contacto
- Cumpleaños y ocasiones especiales

### 5. Proveedores

En este módulo puede:
- Registrar información de contacto de proveedores
- Asociar proveedores con productos
- Ver historial de pedidos por proveedor
- Gestionar datos de facturación

### 6. Reportes

Genere informes sobre:
- Ventas diarias, semanales, mensuales o personalizadas
- Productos más vendidos
- Clientes frecuentes
- Estado de inventario
- Rentabilidad por categorías de productos
- Exportación de datos a formatos CSV o PDF

## Guía de Uso Paso a Paso

### Iniciar el Sistema

1. Ejecute el archivo `main.py` desde su línea de comandos.
2. El sistema mostrará la ventana principal con la barra de navegación superior.
3. Por defecto, se cargará el módulo de Ventas.

### Registrar una Venta

1. Navegue al módulo de **Ventas** haciendo clic en el botón correspondiente.
2. Haga clic en "Nueva Venta" para iniciar una transacción.
3. Seleccione los productos de la lista disponible.
4. Indique la cantidad y talla para cada producto seleccionado.
5. Opcionalmente, seleccione un cliente existente o cree uno nuevo.
6. Aplique descuentos si es necesario.
7. Seleccione el método de pago.
8. Finalice la venta haciendo clic en "Completar Venta".
9. Imprima o guarde el comprobante de venta.

### Administrar Productos

1. Vaya al módulo de **Productos**.
2. Para añadir un producto, haga clic en "Nuevo Producto".
3. Complete la información requerida: nombre, descripción, precio, categoría, etc.
4. Añada tallas y colores disponibles.
5. Asigne un proveedor (opcional).
6. Guarde los cambios.

### Control de Inventario

1. Acceda al módulo de **Inventario**.
2. Verifique el stock actual de los productos.
3. Para registrar una entrada de mercancía, haga clic en "Registrar Entrada".
4. Seleccione el producto y especifique la cantidad por talla/color.
5. Para ajustar el inventario, use la opción "Ajuste de Inventario".

### Gestión de Clientes

1. Ingrese al módulo de **Clientes**.
2. Para añadir un nuevo cliente, haga clic en "Nuevo Cliente".
3. Registre la información personal y de contacto.
4. Consulte el historial de compras seleccionando un cliente y haciendo clic en "Ver Historial".

### Administración de Proveedores

1. Vaya al módulo de **Proveedores**.
2. Para añadir un proveedor, haga clic en "Nuevo Proveedor".
3. Complete la información de contacto y datos fiscales.
4. Asocie los productos que suministra este proveedor.

### Generación de Reportes

1. Acceda al módulo de **Reportes**.
2. Seleccione el tipo de reporte que desea generar.
3. Especifique el periodo de tiempo para el reporte.
4. Utilice los filtros disponibles para personalizar la información.
5. Genere el reporte haciendo clic en "Crear Reporte".
6. Exporte el reporte al formato deseado (CSV, PDF) utilizando los botones correspondientes.

## Consejos y Buenas Prácticas

- Realice respaldos periódicos de la base de datos (archivo `clothing_store.db`).
- Mantenga actualizada la información de inventario para evitar discrepancias.
- Registre a todos los clientes para poder realizar seguimiento de ventas y preferencias.
- Revise regularmente los reportes para identificar tendencias y tomar decisiones informadas.
- Cierre correctamente el sistema al finalizar su uso para evitar pérdida de datos.

## Solución de Problemas

| Problema | Posible Solución |
|----------|------------------|
| El sistema no inicia | Verifique que Python esté correctamente instalado y que la versión sea 3.8 o superior |
| Error al registrar una venta | Asegúrese de que haya stock suficiente del producto seleccionado |
| No se muestran todos los productos | Compruebe los filtros activos en la lista de productos |
| Error en la base de datos | Restaure desde una copia de seguridad reciente |

## Soporte

Si encuentra algún problema o tiene sugerencias para mejorar el sistema, por favor contacte al equipo de soporte técnico
