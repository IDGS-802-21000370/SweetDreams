from flask import Blueprint, render_template, request
from datetime import datetime, timedelta
from sqlalchemy import extract
from blueprints.models import DetalleVentas, Galleta, TipoVenta, Venta, db
from sqlalchemy import func
import matplotlib.pyplot as plt
import io
import base64

dashboard_blueprint = Blueprint("dashboard", __name__, template_folder="templates")

@dashboard_blueprint.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    ventas_diarias = calcular_ventas_diarias()
    plot_url_ventas_diarias, plot_url_productos_vendidos, plot_url_ventas_tipo = generar_grafico_ventas_diarias(ventas_diarias)
    return render_template('dashboard/dashboard.html', plot_url_ventas_diarias=plot_url_ventas_diarias, plot_url_productos_vendidos=plot_url_productos_vendidos, plot_url_ventas_tipo=plot_url_ventas_tipo)

def calcular_ventas_diarias():
    fecha_actual = datetime.now().date()
    primer_dia_mes = fecha_actual.replace(day=1)
    ultimo_dia_mes = primer_dia_mes.replace(month=primer_dia_mes.month % 12 + 1, day=1) - timedelta(days=1)
    
    ventas_diarias = db.session.query(
        func.date(Venta.fecha_creacion).label('fecha'),
        func.sum(Venta.total).label('total')
    ).filter(
        Venta.fecha_creacion.between(primer_dia_mes, ultimo_dia_mes)
    ).group_by(
        func.date(Venta.fecha_creacion)
    ).all()

    return ventas_diarias

def generar_grafico_ventas_diarias(ventas_diarias):
    labels = [venta.fecha.strftime('%Y-%m-%d') for venta in ventas_diarias]
    values = [venta.total for venta in ventas_diarias]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, values)
    plt.xlabel('Fecha')
    plt.ylabel('Total Vendido')
    plt.title('Ventas Diarias')
    plt.xticks(rotation=45)
    plt.tight_layout()

    image_stream_ventas_diarias = io.BytesIO()
    plt.savefig(image_stream_ventas_diarias, format='png')
    image_stream_ventas_diarias.seek(0)
    plt.close()

    detalles_ventas = db.session.query(
        DetalleVentas.galleta_id_galleta,
        func.sum(DetalleVentas.cantidad).label('total_vendido')
    ).group_by(
        DetalleVentas.galleta_id_galleta
    ).all()

    ventas_por_producto = {detalle.galleta_id_galleta: detalle.total_vendido for detalle in detalles_ventas}

    productos_mas_vendidos = sorted(
        ventas_por_producto.items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:5]

    nombres_productos_mas_vendidos = [Galleta.query.get(id_galleta).nombre for id_galleta, _ in productos_mas_vendidos]
    cantidades_productos_mas_vendidos = [cantidad for _, cantidad in productos_mas_vendidos]

    plt.figure(figsize=(10, 6))
    plt.bar(nombres_productos_mas_vendidos, cantidades_productos_mas_vendidos)
    plt.xlabel('Producto')
    plt.ylabel('Cantidad Vendida')
    plt.title('Productos Más Vendidos')
    plt.xticks(rotation=45)
    plt.tight_layout()

    image_stream_productos_vendidos = io.BytesIO()
    plt.savefig(image_stream_productos_vendidos, format='png')
    image_stream_productos_vendidos.seek(0)
    plt.close()

    detalles_ventas_tipos = db.session.query(
        DetalleVentas.galleta_id_galleta,
        DetalleVentas.tipoventa_id_tipoVenta,
        func.sum(DetalleVentas.cantidad).label('total_vendido')
    ).group_by(
        DetalleVentas.galleta_id_galleta,
        DetalleVentas.tipoventa_id_tipoVenta
    ).all()

    ventas_por_tipo = {}
    for detalle in detalles_ventas_tipos:
        galleta_id = detalle.galleta_id_galleta
        tipo_venta_id = detalle.tipoventa_id_tipoVenta
        tipo_venta_nombre = TipoVenta.query.get(tipo_venta_id).descripcion
        cantidad = detalle.total_vendido
        if galleta_id not in ventas_por_tipo:
            ventas_por_tipo[galleta_id] = {}
        ventas_por_tipo[galleta_id][tipo_venta_nombre] = cantidad

    nombres_galletas = [Galleta.query.get(id_galleta).nombre for id_galleta in ventas_por_tipo.keys()]
    
    ventas_por_tipo_list = [ventas_por_tipo.get(galleta_id, {}) for galleta_id in ventas_por_tipo.keys()]
    ventas_por_tipo_list = [{'caja': venta.get('caja', 0), 'pieza': venta.get('pieza', 0), 'gramaje': venta.get('gramaje', 0)} for venta in ventas_por_tipo_list]

    ventas_por_caja = [venta['caja'] for venta in ventas_por_tipo_list]
    ventas_por_pieza = [venta['pieza'] for venta in ventas_por_tipo_list]
    ventas_por_gramaje = [venta['gramaje'] for venta in ventas_por_tipo_list]

    plt.figure(figsize=(10, 6))
    bar_width = 0.35
    indices = range(len(nombres_galletas))

    plt.bar(indices, ventas_por_caja, bar_width, label='Caja')
    plt.bar([i + bar_width for i in indices], ventas_por_pieza, bar_width, label='Pieza')
    plt.bar([i + bar_width * 2 for i in indices], ventas_por_gramaje, bar_width, label='Gramaje')
    
    plt.xlabel('Galleta')
    plt.ylabel('Cantidad Vendida')
    plt.title('Ventas por Tipo de Galleta')
    plt.xticks([i + bar_width for i in indices], nombres_galletas, rotation=45)
    plt.legend()
    plt.tight_layout()

    image_stream_ventas_tipo = io.BytesIO()
    plt.savefig(image_stream_ventas_tipo, format='png')
    image_stream_ventas_tipo.seek(0)
    plt.close()

    image_base64_ventas_diarias = base64.b64encode(image_stream_ventas_diarias.getvalue()).decode('utf-8')
    image_base64_productos_vendidos = base64.b64encode(image_stream_productos_vendidos.getvalue()).decode('utf-8')
    image_base64_ventas_tipo = base64.b64encode(image_stream_ventas_tipo.getvalue()).decode('utf-8')

    return image_base64_ventas_diarias, image_base64_productos_vendidos, image_base64_ventas_tipo