from flask import Blueprint, render_template, redirect, url_for
from datetime import datetime, timedelta
from sqlalchemy import func
from blueprints.models import DetalleVentas, Galleta, TipoVenta, Venta, db
import pandas as pd
import plotly.express as px
from plotly.io import to_html
from flask_login import current_user
from functools import wraps

dashboard_blueprint = Blueprint("dashboard", __name__, template_folder="templates")
def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            # Redirigir a una página de acceso denegado o a la página principal
            return render_template('404/404.html')
        return func(*args, **kwargs)
    return decorated_view

def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login.login'))
        return func(*args, **kwargs)
    return decorated_view

@dashboard_blueprint.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    ventas_diarias = calcular_ventas_diarias()
    plot_html_ventas_diarias, plot_html_productos_vendidos, plot_html_ventas_tipo = generar_graficos(ventas_diarias)
    return render_template('dashboard/dashboard.html', plot_html_ventas_diarias=plot_html_ventas_diarias, plot_html_productos_vendidos=plot_html_productos_vendidos, plot_html_ventas_tipo=plot_html_ventas_tipo)

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

def generar_graficos(ventas_diarias):
    # Gráfico de Ventas Diarias
    df_ventas_diarias = pd.DataFrame(ventas_diarias, columns=['fecha', 'total'])
    fig_ventas_diarias = px.bar(df_ventas_diarias, x='fecha', y='total', title='Ventas Diarias')
    plot_html_ventas_diarias = to_html(fig_ventas_diarias, full_html=False)
    
    # Gráfico de Productos Más Vendidos
    detalles_ventas = db.session.query(
        DetalleVentas.galleta_id_galleta,
        func.sum(DetalleVentas.cantidad).label('total_vendido')
    ).group_by(
        DetalleVentas.galleta_id_galleta
    ).all()
    df_productos_vendidos = pd.DataFrame(detalles_ventas, columns=['galleta_id', 'total_vendido'])
    df_productos_vendidos['producto'] = df_productos_vendidos['galleta_id'].apply(lambda id: Galleta.query.get(id).nombre)
    fig_productos_vendidos = px.bar(df_productos_vendidos, x='producto', y='total_vendido', title='Productos Más Vendidos')
    plot_html_productos_vendidos = to_html(fig_productos_vendidos, full_html=False)

    # Gráfico de Ventas por Tipo de Galleta
    detalles_ventas_tipos = db.session.query(
        DetalleVentas.galleta_id_galleta,
        DetalleVentas.tipoventa_id_tipoVenta,
        func.sum(DetalleVentas.cantidad).label('total_vendido')
    ).group_by(
        DetalleVentas.galleta_id_galleta,
        DetalleVentas.tipoventa_id_tipoVenta
    ).all()
    df_ventas_tipo = pd.DataFrame(detalles_ventas_tipos, columns=['galleta_id', 'tipo_venta_id', 'total_vendido'])
    df_ventas_tipo['tipo_venta'] = df_ventas_tipo['tipo_venta_id'].apply(lambda id: TipoVenta.query.get(id).descripcion)
    df_ventas_tipo['producto'] = df_ventas_tipo['galleta_id'].apply(lambda id: Galleta.query.get(id).nombre)
    fig_ventas_tipo = px.bar(df_ventas_tipo, x='producto', y='total_vendido', color='tipo_venta', title='Ventas por Tipo de Galleta')
    plot_html_ventas_tipo = to_html(fig_ventas_tipo, full_html=False)
    fig_ventas_diarias = px.bar(
    df_ventas_diarias, 
    x='fecha', 
    y='total', 
    title='Ventas Diarias',
    color_discrete_sequence=['#b0c2f2']  # Cambia el color aquí; usa un código de color hex
    )
    fig_productos_vendidos = px.bar(
    df_productos_vendidos, 
    x='producto', 
    y='total_vendido', 
    title='Productos Más Vendidos',
    color_discrete_sequence=['#b0f2c2']  # Cambia el color aquí
    )
    fig_ventas_tipo = px.bar(
    df_ventas_tipo, 
    x='producto', 
    y='total_vendido', 
    color='tipo_venta',
    title='Ventas por Tipo de Galleta',
    color_discrete_map={
        'Tipo 1': '#c5c6c8',  # Cambia 'Tipo 1' por la descripción real del tipo de venta
        'Tipo 2': '#b0f2c2',
        'Tipo 3': '#b0c2f2'
    }
    )

    return plot_html_ventas_diarias, plot_html_productos_vendidos, plot_html_ventas_tipo
