import math


def average_weekly_sales(sales_week: list) -> dict:
    """
    Calcula el promedio de las ventas semanales de un producto.
    Extrae correctamente el número dentro de la tupla (valor, es_pesable).
    """
    if not sales_week or len(sales_week) < 3:
        return {"vp": 0.0, "vp_diaria": 0.0, "pesable": False}

    code = sales_week
    product = sales_week

    # CORRECCIÓN DE TUPLA: Extraemos el primer elemento v[0] que contiene el número real
    val = []
    is_weighable = False

    for v in sales_week[2:]:
        if isinstance(v, tuple) and v is not None:
            val.append(float(v[0]))  # <--- v[0] es el número (ej: 71.115)
            is_weighable = v[1]  # <--- v[1] es el booleano (ej: True)

    if not val:
        print(f"El producto {code} no tiene valores numéricos en sus semanas.")
        return {"vp": 0.0, "vp_diaria": 0.0, "pesable": is_weighable}

    # Calcular promedio semanal
    average_sale_weekly = sum(val) / len(val)
    average_sale_daily = average_sale_weekly / 7

    if not is_weighable:
        vp_report = int(round(average_sale_weekly))
        vp_diaria_report = int(round(average_sale_daily))
    else:
        vp_report = round(
            average_sale_weekly, 3
        )  # Mantenemos los 3 decimales de tus Kg
        vp_diaria_report = round(average_sale_daily, 3)

    print(
        f"{code} {product} Promedio venta semanal: {vp_report}, diario: {vp_diaria_report}"
    )

    return {
        "vp": vp_report,
        "vp_diaria": vp_diaria_report,
        "pesable": is_weighable,
    }


def suggested(product_data: dict) -> dict:
    """Calcula la cantidad sugerida adaptando días a semanas y respetando decimales."""
    raw_average_sale: dict = product_data.get("average_sale")

    # CORRECCIÓN DE TIEMPO: El Excel viene en DÍAS (ej: 2). Lo dividimos entre 7 para llevarlo a semanas.
    tiempo_reposicion_dias = float(product_data.get("replenishment_time", 0.0))
    replenishment_time: float = tiempo_reposicion_dias / 7.0

    current_stock: float = float(product_data.get("current_stock", 0.0))
    packing: float = float(product_data.get("packing", 1.0))
    is_weighable: bool = product_data.get("is_weighable", False)
    dispatch_frequency = product_data.get("frecuencia_despacho", 1)

    if raw_average_sale is None or current_stock is None:
        return {"cantidad": 0, "empaque": 0, "stock_seguridad": 0.0, "stock_ideal": 0.0}

    average_sale_weekly: float = float(raw_average_sale["vp"])

    # Evaluación de frecuencia basada en tu columna 'frecuencia' (vale 2)
    if dispatch_frequency >= 2:
        review_interval_weeks = 0.5  # Ventana de 3.5 días
        safety_weeks = 0.5  # Colchón de 3.5 días de venta
    else:
        review_interval_weeks = 1.0  # Ventana de 7 días
        safety_weeks = 1.0  # Colchón de 7 días de venta

    # Calcular el Stock de Seguridad
    if is_weighable:
        safety_stock = round(average_sale_weekly * safety_weeks, 3)
    else:
        safety_stock = math.ceil(average_sale_weekly * safety_weeks)

    # Inventario Óptimo con unidades de tiempo sincronizadas (Semanas)
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
            # Para Kg (Pepino, Tomate) no redondeamos a enteros, dejamos los decimales exactos
            amount = round(result, 3)
            necessary_packages = round(amount / packing, 3)
        else:
            # Para productos por unidad (Bandejas de fresas) redondeamos hacia arriba
            necessary_packages = math.ceil(result / packing)
            amount = int(necessary_packages * packing)

    print(
        f"Frecuencia: {dispatch_frequency} viajes. Stock Seguridad: {safety_stock} | Sugerido Final: {amount}"
    )

    return {
        "cantidad": amount,
        "empaque": necessary_packages,
        "stock_seguridad": safety_stock,
        "stock_ideal": optimal_inventory,
        "pesable": is_weighable,
    }
