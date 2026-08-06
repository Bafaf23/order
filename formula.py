import math


def average_weekly_sales(sales_week: list) -> dict:
    """
    Calcula el promedio de las ventas semanales de un producto.
    Soporta la estructura pre_sale de Flask con tuplas (valor, es_pesable).
    """
    if not sales_week or len(sales_week) < 3:
        print("Ventas vacías o estructura pre_sale incorrecta")
        return {"vp": 0.0, "vp_diaria": 0.0, "pesable": False}

    code = sales_week[0]
    product = sales_week[1]

    # CORRECCIÓN DE INDEXACIÓN:
    # Recorremos desde el índice 2 en adelante. Cada 'v' es una tupla: (número, es_pesable)
    # Extraemos solo el número (v[0]) de cada tupla semanal.
    val = [
        float(v[0]) for v in sales_week[2:] if isinstance(v, tuple) and v[0] is not None
    ]

    # Extraemos el indicador 'is_weighable' del primer registro de venta válido
    is_weighable = sales_week[2][1] if isinstance(sales_week[2], tuple) else False

    if not val:
        print(f"El producto {code} no tiene valores numéricos en sus semanas.")
        return {"vp": 0.0, "vp_diaria": 0.0, "pesable": is_weighable}

    # Calcular promedio semanal manteniendo flotante para precisión intermedia
    average_sale_weekly = sum(val) / len(val)

    # Calcular promedio diario
    average_sale_daily = average_sale_weekly / 7

    # Si no es pesable, redondeamos el resultado final para la reportería
    if not is_weighable:
        vp_report = int(round(average_sale_weekly))
        vp_diaria_report = int(round(average_sale_daily))
    else:
        vp_report = round(average_sale_weekly, 2)
        vp_diaria_report = round(average_sale_daily, 2)

    print(
        f"{code} {product} Promedio venta semanal: {vp_report}, promedio diario: {vp_diaria_report}"
    )

    return {
        "vp": vp_report,
        "vp_diaria": vp_diaria_report,
        "pesable": is_weighable,
    }


def suggested(product_data: dict) -> dict:
    """Calcula la cantidad sugerida de compra para la orden de compra (OC) basándose en semanas."""
    raw_average_sale: dict = product_data.get("average_sale")
    replenishment_time: float = float(product_data.get("replenishment_time", 0.0))
    current_stock: float = float(product_data.get("current_stock", 0.0))
    packing: float = float(product_data.get("packing", 1.0))
    is_weighable: bool = product_data.get("is_weighable", False)

    # Captura de la frecuencia enviada dinámicamente desde Flask
    dispatch_frequency = product_data.get("frecuencia_despacho", 1)

    if raw_average_sale is None or current_stock is None:
        print("Sin datos para realizar el cálculo")
        return {"cantidad": 0, "empaque": 0, "stock_seguridad": 0.0, "stock_ideal": 0.0}

    average_sale_weekly: float = float(raw_average_sale["vp"])

    # Evaluación logística de la frecuencia de visitas del camión
    if dispatch_frequency == 2:
        review_interval_weeks = 0.5  # Se pide cada 3.5 días
        safety_weeks = 0.5  # Colchón de media semana de ventas
    else:
        review_interval_weeks = 1.0  # Se pide cada 7 días
        safety_weeks = 1.0  # Colchón de una semana entera de ventas

    # Cálculo del Stock de Seguridad
    if is_weighable:
        safety_stock = average_sale_weekly * safety_weeks
    else:
        safety_stock = math.ceil(average_sale_weekly * safety_weeks)

    # El inventario óptimo suma el tiempo de ciclo + el tránsito del camión + el colchón
    optimal_inventory = (
        average_sale_weekly * (review_interval_weeks + replenishment_time)
    ) + safety_stock

    # Unidades netas faltantes
    result = optimal_inventory - current_stock

    if result <= 0:
        necessary_packages = 0
        amount = 0
    else:
        if is_weighable:
            amount = round(result, 2)
            necessary_packages = round(amount / packing, 2)
        else:
            # Redondeo estricto hacia arriba a cajas completas (UXE)
            necessary_packages = math.ceil(result / packing)
            amount = int(necessary_packages * packing)

    print(
        f"Frecuencia evaluada: {dispatch_frequency} viaje(s). Stock seguridad: {safety_stock}"
    )

    return {
        "cantidad": amount,
        "empaque": necessary_packages,
        "stock_seguridad": safety_stock,
        "stock_ideal": optimal_inventory,
        "pesable": is_weighable,
    }
