import math

def suggested(
    average_sale: int,
    replenishment_time: int,
    current_stock: int,
    safety_stock: int,
    packing: int,
) -> dict:
    """
    Calcula la cantidad sugerida de compra para la orden de compra (OC).

    Args:
        average_sale (int): Venta promedio del producto en un período.
        replenishment_time (int): Tiempo que tarda el proveedor en entregar (en días o meses).
        current_stock (int): Inventario físico actual en el almacén.
        safety_stock (int): Stock de colchón para prevenir desabastecimiento.
        packing (int): Cantida viene en el empaque.

    Returns:
        dict: Un diccionario con:
        - "cantidad" (int): Cantidad óptima en unidades a solicitar.
        - "empaque" (int): Cantidad de cajas/paquetes cerrados para el proveedor.
    """

    if average_sale is None or replenishment_time is None or current_stock is None:
        print("Sin datos para realizar el calculo")
        return {"cantidad": 0, "empaque": 0}

    optimal_inventory = average_sale * replenishment_time + safety_stock

    result = optimal_inventory - current_stock

    if result < 0:
        return 0

    necessary_packages = math.ceil(result / packing)

    return {"cantidad": necessary_packages * packing, "empaque": necessary_packages}


def average_weekly_sales(sales_week: list) -> int:
    """Calcula el promedio de la venta semanales de un producto.
    Tomo una lista con las ventas de toda una semana y retorna un resultado redondeado.

    Args:
        sales_week (list): Una lista de numeros que representan las ventas semanales.

    Returns:
        int: el promedio de ventas expresado con un numero entero.

    Raises:
        ValueError: Si la lista `sales_week` está vacía.
    """
    print(f"Procesando el promedio de ventas {sales_week}")

    if not sales_week:
        print("Ventas vacias")
        raise ValueError("La lista de ventas no puede eatar vacía.")

    return int(sum(sales_week) / len(sales_week))
