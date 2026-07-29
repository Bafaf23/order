import math


def suggested(product_data: dict) -> dict:
    """
    Calcula la cantidad sugerida de compra para la orden de compra (OC).

    Args:
        product_data (dict): Diccionario con la información relevante al cálculo para generar el sugerido de compra.

        Debe contener:

        - "average_sale" (dict): Venta promedio del producto en un período (semanas).
        - "replenishment_time" (float): Tiempo que tarda el proveedor en entregar (en semanas).
        - "current_stock" (float): Inventario físico actual en el almacén.
        - "safety_stock" (float): Stock de colchón para prevenir desabastecimiento.
        - "packing" (float): Cantidad que viene en el empaque.
        - "is_weighable" (bool): Indentificador del tipo de producto, pesable o no pesable

    Returns:
        dict: Un diccionario con:
        - "cantidad" (float): Cantidad óptima en unidades a solicitar.
        - "empaque" (float): Cantidad de cajas/paquetes cerrados para el proveedor.
        - "stock_seguridad": Cantidad para prevencion de logistica ante cualquier imprevisto de parte del proveedor.
        - "pesable": Idedtifiacor si el producto es pesable o no.
    """
    raw_average_sale: dict = product_data.get("average_sale")
    replenishment_time: float = product_data.get("replenishment_time")
    current_stock: float = product_data.get("current_stock")
    packing: float = product_data.get("packing", 1)
    is_weighable: bool = product_data.get("is_weighable")

    if raw_average_sale is None or replenishment_time is None or current_stock is None:
        print("Sin datos para realizar el calculo")
        return {"cantidad": 0, "empaque": 0, "stock_seguridad": 0.0, "stock_ideal": 0.0}

    # venta diaria
    average_sale: float = raw_average_sale["vp"] / 7

    # stock de seguridad
    safety_stock = (
        average_sale * replenishment_time
        if is_weighable
        else math.ceil(average_sale * replenishment_time)
    )

    optimal_inventory = (average_sale * replenishment_time) + safety_stock

    result = optimal_inventory - current_stock

    if result <= 0:
        necessary_packages = 0
        amount = 0
    else:
        necessary_packages = math.ceil(result / packing)
        print(f"Stock de seguridad calculado: {safety_stock}")
        amount = int(necessary_packages * packing)

    return {
        "cantidad": amount,
        "empaque": necessary_packages,
        "stock_seguridad": safety_stock,
        "stock_ideal": optimal_inventory,
        "pesable": is_weighable,
    }


def average_weekly_sales(sales_week: list) -> dict:
    """Calcula el promedio de las ventas semanales de un producto.

    Args:
        sales_week (list): Lista de tuplas (valor, es_pesable).

    Returns:
        dict: Diccionario con la venta promedio semanal ("vp") y diaria ("vp_diaria").

    Raises:
        ValueError: Si la lista `sales_week` está vacía.
    """

    print(f"Procesando el promedio de ventas {sales_week}")

    if not sales_week:
        print("Ventas vacias")
        raise ValueError("La lista de ventas no puede eatar vacía.")

    val = [v[0] for v in sales_week]

    is_weighable = sales_week[0][1]

    raw_weekly_avg = sum(val) / len(val)

    average_sale = raw_weekly_avg if is_weighable else int(round(raw_weekly_avg))

    raw_daily_avg = average_sale / 7
    average_daily = raw_daily_avg if is_weighable else int(round(raw_daily_avg))

    print(f"Promedio de venta semanal: {average_sale} y diaria: {average_daily}")

    return {"vp": average_sale, "vp_diaria": average_daily, "pesable": is_weighable}
