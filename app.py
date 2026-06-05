# -*- coding: utf-8 -*-
"""
Controlador Principal Flask - PharmaSafe Analytics
Maneja las rutas de la aplicación web y coordina con el motor de análisis de datos.
"""

import secrets
from flask import Flask, render_template, redirect, url_for
import motor_analisis

app = Flask(__name__)

# Configuración de seguridad: Generar clave secreta efímera e independiente
# TODO(security): En producción, se debe cargar desde un administrador de secretos.
app.secret_key = secrets.token_hex(32)

@app.route('/')
def index():
    """Redirecciona al inicio del sitio."""
    return redirect(url_for('inicio'))

@app.route('/inicio')
def inicio():
    """Renderiza la página de presentación académica y metodología."""
    return render_template('inicio.html', active_page='inicio')

@app.route('/dashboard')
def dashboard():
    """Renderiza el Dashboard General con KPIs y gráficos principales."""
    try:
        kpis = motor_analisis.obtener_kpis()
        graficos = motor_analisis.generar_graficos()
        insights = motor_analisis.obtener_insights()
        
        return render_template(
            'dashboard.html',
            active_page='dashboard',
            kpis=kpis,
            grafico1=graficos['grafico1'],
            grafico2=graficos['grafico2'],
            insight_dia=insights['insight_dia'],
            alerta_riesgo=insights['alerta_riesgo']
        )
    except Exception as e:
        app.logger.error(f"Error en dashboard: {str(e)}")
        # TODO(security): Mensaje genérico de error al usuario para no exponer detalles internos
        return render_template('error.html', mensaje="Ocurrió un error al procesar el dashboard.")

@app.route('/incidentes')
def incidentes():
    """Renderiza el desglose y listado analítico de los incidentes."""
    try:
        df_inc, _, _ = motor_analisis._cargar_dataframes()
        incidentes_lista = df_inc.to_dict(orient='records')
        graficos = motor_analisis.generar_graficos()
        
        return render_template(
            'incidentes.html',
            active_page='incidentes',
            incidentes=incidentes_lista,
            grafico1=graficos['grafico1'],
            grafico3=graficos['grafico3']
        )
    except Exception as e:
        app.logger.error(f"Error en incidentes: {str(e)}")
        return render_template('error.html', mensaje="Ocurrió un error al cargar la sección de incidentes.")

@app.route('/riesgos')
def riesgos():
    """Renderiza la sección de riesgos farmacológicos y severidad."""
    try:
        _, df_cat, _ = motor_analisis._cargar_dataframes()
        # Filtrar fármacos con alertas LASA activas o preparación media/alta
        alertas_lasa = df_cat[df_cat['alerta_lasa'].str.lower() == 'sí'].to_dict(orient='records')
        graficos = motor_analisis.generar_graficos()
        
        return render_template(
            'riesgos.html',
            active_page='riesgos',
            alertas_lasa=alertas_lasa,
            grafico2=graficos['grafico2'],
            grafico4=graficos['grafico4']
        )
    except Exception as e:
        app.logger.error(f"Error en riesgos: {str(e)}")
        return render_template('error.html', mensaje="Ocurrió un error al cargar la sección de riesgos.")

@app.route('/cruce')
def cruce():
    """Renderiza la tabla consolidada de auditoría (Triple Merge)."""
    try:
        df_audit = motor_analisis.auditar_cruce_datos()
        registros_cruce = df_audit.to_dict(orient='records')
        
        # Estadísticas sencillas sobre el cruce
        total_cruzados = len(df_audit)
        con_guia = len(df_audit[df_audit['tiene_guia'] == 'Sí'])
        
        return render_template(
            'cruce.html',
            active_page='cruce',
            registros=registros_cruce,
            total_cruzados=total_cruzados,
            con_guia=con_guia
        )
    except Exception as e:
        app.logger.error(f"Error en cruce de datos: {str(e)}")
        return render_template('error.html', mensaje="Ocurrió un error en el cruce de datos relacionales.")

@app.route('/calidad')
def calidad():
    """Renderiza el perfilamiento de la calidad de datos y describe()."""
    try:
        calidad_info = motor_analisis.obtener_calidad_datos()
        return render_template(
            'calidad.html',
            active_page='calidad',
            calidad=calidad_info
        )
    except Exception as e:
        app.logger.error(f"Error en calidad de datos: {str(e)}")
        return render_template('error.html', mensaje="Ocurrió un error al cargar el reporte de calidad de datos.")

@app.route('/hallazgos')
def hallazgos():
    """Renderiza la página de hallazgos clínicos y recomendaciones."""
    try:
        insights = motor_analisis.obtener_insights()
        return render_template(
            'hallazgos.html',
            active_page='hallazgos',
            insights=insights
        )
    except Exception as e:
        app.logger.error(f"Error en hallazgos: {str(e)}")
        return render_template('error.html', mensaje="Ocurrió un error al cargar el reporte de hallazgos.")

# Manejador de error 404 personalizado
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', mensaje="La página solicitada no existe."), 404

if __name__ == '__main__':
    # Configuración de ejecución en desarrollo: escuchar en localhost puerto 5000
    app.run(host='127.0.0.1', port=5000, debug=True)
