import math


def suggested(product_data: dict) -> dict:
    """
    Calcula la cantidad sugerida de compra para la orden de compra (OC).

    Args:
        product_data (dict): Diccionario con la información relevante al cálculo para generar el sugerido de compra.

        Debe contener:

        - "average_sale" (float): Venta promedio del producto en un período (semanas).
        - "replenishment_time" (float): Tiempo que tarda el proveedor en entregar (en semanas).
        - "current_stock" (float): Inventario físico actual en el almacén.
        - "safety_stock" (float): Stock de colchón para prevenir desabastecimiento.
        - "packing" (float): Cantidad que viene en el empaque.

    Returns:
        dict: Un diccionario con:
        - "cantidad" (float): Cantidad óptima en unidades a solicitar.
        - "empaque" (float): Cantidad de cajas/paquetes cerrados para el proveedor.
    """
    average_sale: float = product_data.get("average_sale") / 7
    replenishment_time: float = product_data.get("replenishment_time")
    current_stock: float = product_data.get("current_stock")
    safety_stock: float = product_data.get("safety_stock")
    packing: float = product_data.get("packing", 1)

    if average_sale is None or replenishment_time is None or current_stock is None:
        print("Sin datos para realizar el calculo")
        return {"cantidad": 0, "empaque": 0}

    optimal_inventory = (average_sale * replenishment_time) + safety_stock

    result = optimal_inventory - current_stock

    if result <= 0:
        return {"cantidad": 0, "empaque": 0}

    necessary_packages = math.ceil(result / packing)

    return {
        "cantidad": int(necessary_packages * packing),
        "empaque": necessary_packages,
    }


def average_weekly_sales(sales_week: list) -> int:
    """Calcula el promedio de la venta semanales de un producto.
    Tomo una lista con las ventas de toda una semana y retorna un resultado redondeado.

    Args:
        sales_week (list): Una lista de numeros que representan las ventas semanales.

    Returns:
        round: el promedio de ventas expresado con un numero entero.

    Raises:
        ValueError: Si la lista `sales_week` está vacía.
    """
    print(f"Procesando el promedio de ventas {sales_week}")

    if not sales_week:
        print("Ventas vacias")
        raise ValueError("La lista de ventas no puede eatar vacía.")

    average_sale = sum(sales_week) / len(sales_week)
    print(f"Pormedio venta: {average_sale}")
    return average_sale
