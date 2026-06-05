# -*- coding: utf-8 -*-
"""
Motor de Análisis - PharmaSafe Analytics
Lógica separada para el procesamiento de datos con Pandas y generación de gráficos con Matplotlib.
"""

import os
import io
import base64
import pandas as pd
import numpy as np
import matplotlib
# Forzar backend no interactivo
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def _cargar_dataframes():
    """
    Carga y limpia los dataframes aplicando codificaciones correctas y eliminando espacios.
    """
    # incidentes_farmacovigilancia.csv está en latin-1 y tiene cada línea entre comillas
    path_inc = os.path.join(DATA_DIR, 'incidentes_farmacovigilancia.csv')
    with open(path_inc, 'r', encoding='latin-1') as f:
        # Quitamos comillas externas en cada línea
        lines = [line.strip().strip('"') for line in f if line.strip()]
    df_incidentes = pd.read_csv(io.StringIO('\n'.join(lines)))

    # Los catálogos y guías están en utf-8 con BOM
    df_catalogo = pd.read_csv(os.path.join(DATA_DIR, 'catalogo_medicamentos_pediatricos.csv'), encoding='utf-8-sig')
    df_guia = pd.read_csv(os.path.join(DATA_DIR, 'guia_dosificacion_pediatrica.csv'), encoding='utf-8-sig')
    
    # Limpieza básica de espacios
    for df in [df_incidentes, df_catalogo, df_guia]:
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Convertir edad a tipo numérico
    if 'edad_meses' in df_incidentes.columns:
        df_incidentes['edad_meses'] = pd.to_numeric(df_incidentes['edad_meses'], errors='coerce')
        
    return df_incidentes, df_catalogo, df_guia

def obtener_kpis():
    """
    Calcula los KPIs principales del Dashboard.
    """
    df_inc, df_cat, _ = _cargar_dataframes()
    
    total_incidentes = len(df_inc)
    
    # Críticos: severidad es Grave o Crítica
    criticos = df_inc[df_inc['severidad'].str.lower().isin(['grave', 'crítica', 'critica'])].shape[0]
    
    # Fármacos únicos involucrados
    farmacos = df_inc['medicamento'].nunique()
    
    # Edad promedio en meses
    edad_promedio_meses = df_inc['edad_meses'].mean()
    
    return {
        'total_incidentes': total_incidentes,
        'criticos': criticos,
        'farmacos': farmacos,
        'edad_promedio_meses': round(edad_promedio_meses, 1),
        'edad_promedio_anos': round(edad_promedio_meses / 12.0, 1)
    }

def auditar_cruce_datos():
    """
    Implementa el Cruce de Datos (Triple Merge) obligatorio:
    Merge entre incidentes, catálogo de medicamentos y la guía de dosificación.
    """
    df_inc, df_cat, df_gui = _cargar_dataframes()
    
    # 1. Merge de incidentes con catálogo en medicamento <-> principio_activo
    df_m1 = pd.merge(df_inc, df_cat, left_on='medicamento', right_on='principio_activo', how='left')
    
    # 2. Merge con la guía en cie10_codigo, grupo_etario, y medicamento
    df_audit = pd.merge(
        df_m1, 
        df_gui, 
        on=['cie10_codigo', 'grupo_etario', 'medicamento'], 
        how='left', 
        suffixes=('', '_guia')
    )
    
    # Rellenar nulos para campos críticos en auditoría para visualización limpia
    df_audit['alerta_lasa'] = df_audit['alerta_lasa'].fillna('No')
    df_audit['riesgo_preparacion'] = df_audit['riesgo_preparacion'].fillna('No especificado')
    df_audit['dosis_recomendada_mg_kg'] = df_audit['dosis_recomendada_mg_kg'].fillna(0)
    df_audit['dosis_total_teorica_mg'] = df_audit['dosis_total_teorica_mg'].fillna(0)
    
    # Agregar un indicador de auditoría: si coincide con la guía de dosis recomendada
    df_audit['tiene_guia'] = df_audit['dosis_total_teorica_mg'].apply(lambda x: 'Sí' if x > 0 else 'No')
    
    return df_audit

def obtener_calidad_datos():
    """
    Genera estadísticas de calidad de datos usando Pandas (isnull(), describe(), dtypes).
    """
    df_inc, df_cat, df_gui = _cargar_dataframes()
    
    # Información de incidentes
    nulos = df_inc.isnull().sum().to_frame(name='valores_nulos')
    nulos['porcentaje_nulos'] = round((nulos['valores_nulos'] / len(df_inc)) * 100, 2)
    nulos['tipo_dato'] = df_inc.dtypes.astype(str)
    nulos = nulos.reset_index().rename(columns={'index': 'columna'})
    
    # Estadísticas descriptivas de variables numéricas (edad_meses)
    describir = df_inc['edad_meses'].describe().to_frame().reset_index()
    describir.columns = ['Métrica', 'Edad (Meses)']
    
    # Mapear los nombres de métricas al español
    metricas_es = {
        'count': 'Cantidad de Registros',
        'mean': 'Media (Promedio)',
        'std': 'Desviación Estándar',
        'min': 'Valor Mínimo',
        '25%': 'Percentil 25 (Q1)',
        '50%': 'Mediana (Percentil 50)',
        '75%': 'Percentil 75 (Q3)',
        'max': 'Valor Máximo'
    }
    describir['Métrica'] = describir['Métrica'].map(metricas_es).fillna(describir['Métrica'])
    
    # Conteo de duplicados
    duplicados = df_inc.duplicated().sum()
    
    return {
        'columnas_tabla': nulos.to_dict(orient='records'),
        'describir_tabla': describir.to_dict(orient='records'),
        'total_filas': len(df_inc),
        'duplicados': int(duplicados)
    }

def obtener_insights():
    """
    Genera insights automatizados y alertas destacadas basados en la analítica de Pandas.
    """
    df_inc, df_cat, _ = _cargar_dataframes()
    
    # Medicamento más común en incidentes
    top_med = df_inc['medicamento'].value_counts().idxmax()
    top_med_count = df_inc['medicamento'].value_counts().max()
    
    # Etapa más común de error
    top_etapa = df_inc['etapa_proceso'].value_counts().idxmax()
    top_etapa_count = df_inc['etapa_proceso'].value_counts().max()
    
    # Proporción de severidad crítica
    criticos = df_inc[df_inc['severidad'].str.lower().isin(['grave', 'crítica', 'critica'])]
    porcentaje_criticos = round((len(criticos) / len(df_inc)) * 100, 1)
    
    # Alertas del catálogo que coinciden con incidentes
    df_cruzado = pd.merge(df_inc, df_cat, left_on='medicamento', right_on='principio_activo', how='inner')
    con_lasa = df_cruzado[df_cruzado['alerta_lasa'].str.lower() == 'sí']
    con_lasa_count = len(con_lasa)
    
    # Detalle de medicamentos con alerta LASA involucrados
    lasa_meds = ", ".join(con_lasa['medicamento'].unique())
    
    insight_dia = (
        f"La etapa de **{top_etapa}** representa la mayor vulnerabilidad operativa con "
        f"{top_etapa_count} incidentes. El medicamento **{top_med}** fue el principio activo más "
        f"involucrado ({top_med_count} casos). El {porcentaje_criticos}% de los incidentes se "
        f"clasificaron como graves o críticos."
    )
    
    alerta_riesgo = (
        f"¡Alerta LASA Detectada! Se registran {con_lasa_count} incidentes con medicamentos bajo "
        f"alerta de similitud fonética o visual (LASA), afectando principalmente a: **{lasa_meds}**. "
        f"Es imperativo reforzar las etiquetas diferenciadas y el doble chequeo."
    )
    
    return {
        'insight_dia': insight_dia,
        'alerta_riesgo': alerta_riesgo,
        'top_med': top_med,
        'top_etapa': top_etapa,
        'porcentaje_criticos': porcentaje_criticos,
        'con_lasa_count': con_lasa_count
    }

def _fig_to_base64(fig):
    """
    Convierte una figura de Matplotlib a Base64 en memoria y limpia el lienzo.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig) # Liberar memoria y evitar superposiciones
    return img_b64

def generar_graficos():
    """
    Genera los 4 gráficos solicitados usando Matplotlib y retorna sus códigos Base64.
    """
    df_inc, _, _ = _cargar_dataframes()
    
    # Paleta de colores personalizada
    color_indigo = '#312e81'
    color_violeta = '#4f46e5'
    color_acento_verde = '#10b981'
    color_acento_morado = '#a855f7'
    color_naranja = '#f59e0b'
    color_rojo = '#ef4444'
    
    # -----------------
    # GRÁFICO 1: Medicamentos más Involucrados (Barras)
    # -----------------
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    top_meds = df_inc['medicamento'].value_counts().head(5)
    bars = ax1.bar(top_meds.index, top_meds.values, color=[color_indigo, color_violeta, color_acento_morado, '#818cf8', '#a5b4fc'])
    ax1.set_title('Top 5 Medicamentos Involucrados en Incidentes', fontsize=12, fontweight='bold', color=color_indigo)
    ax1.set_ylabel('Cantidad de Incidentes', fontsize=10)
    ax1.set_xlabel('Principio Activo', fontsize=10)
    # Agregar etiquetas de valor encima de las barras
    for bar in bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.5, str(int(yval)), ha='center', va='bottom', fontsize=9, fontweight='bold')
    # Quitar bordes para estética limpia
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    fig1.tight_layout()
    g1_b64 = _fig_to_base64(fig1)
    
    # -----------------
    # GRÁFICO 2: Distribución por Severidad (Dona)
    # -----------------
    fig2, ax2 = plt.subplots(figsize=(5.5, 4))
    severidad_counts = df_inc['severidad'].value_counts()
    
    # Mapear colores específicos
    colores_sev = {
        'Leve': color_acento_verde,
        'Moderada': color_naranja,
        'Grave': color_rojo,
        'Crítica': '#7f1d1d' # Rojo oscuro
    }
    colores_lista = [colores_sev.get(idx, '#64748b') for idx in severidad_counts.index]
    
    wedges, texts, autotexts = ax2.pie(
        severidad_counts.values, 
        labels=severidad_counts.index, 
        autopct='%1.1f%%',
        startangle=90, 
        colors=colores_lista,
        wedgeprops=dict(width=0.4, edgecolor='white') # Dona
    )
    plt.setp(autotexts, size=9, weight="bold", color="white")
    plt.setp(texts, size=10)
    ax2.set_title('Distribución de Incidentes por Severidad', fontsize=12, fontweight='bold', color=color_indigo)
    fig2.tight_layout()
    g2_b64 = _fig_to_base64(fig2)
    
    # -----------------
    # GRÁFICO 3: Incidentes por Etapa del Proceso (Barras Horizontales)
    # -----------------
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    etapas = df_inc['etapa_proceso'].value_counts().sort_values(ascending=True)
    bars_h = ax3.barh(etapas.index, etapas.values, color=color_violeta)
    ax3.set_title('Incidentes por Etapa del Proceso', fontsize=12, fontweight='bold', color=color_indigo)
    ax3.set_xlabel('Cantidad de Incidentes', fontsize=10)
    
    # Agregar etiquetas de valor al final de cada barra
    for bar in bars_h:
        xval = bar.get_width()
        ax3.text(xval + 0.5, bar.get_y() + bar.get_height()/2.0, str(int(xval)), ha='left', va='center', fontsize=9, fontweight='bold')
    
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    fig3.tight_layout()
    g3_b64 = _fig_to_base64(fig3)
    
    # -----------------
    # GRÁFICO 4: Severidad por Grupo Etario (Barras Apiladas)
    # -----------------
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    
    # Crear tabla cruzada de Grupo Etario vs Severidad
    crosstab = pd.crosstab(df_inc['grupo_etario'], df_inc['severidad'])
    
    # Asegurar el orden de severidad
    orden_sev = ['Leve', 'Moderada', 'Grave', 'Crítica']
    orden_sev_existentes = [col for col in orden_sev if col in crosstab.columns]
    crosstab = crosstab[orden_sev_existentes]
    
    colores_apilados = [colores_sev.get(col, '#64748b') for col in orden_sev_existentes]
    
    crosstab.plot(kind='bar', stacked=True, color=colores_apilados, ax=ax4)
    ax4.set_title('Severidad de Incidentes según Grupo Etario', fontsize=12, fontweight='bold', color=color_indigo)
    ax4.set_ylabel('Cantidad de Incidentes', fontsize=10)
    ax4.set_xlabel('Grupo Etario', fontsize=10)
    ax4.legend(title='Severidad', frameon=False)
    plt.xticks(rotation=0)
    
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    fig4.tight_layout()
    g4_b64 = _fig_to_base64(fig4)
    
    return {
        'grafico1': g1_b64,
        'grafico2': g2_b64,
        'grafico3': g3_b64,
        'grafico4': g4_b64
    }
