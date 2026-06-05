# PharmaSafe Analytics: Sistema de Análisis Exploratorio para Farmacovigilancia Pediátrica

## 1. Descripción del Proyecto
PharmaSafe Analytics (o PediaRisk Analytics) es una aplicación web piloto diseñada para auditar y analizar incidentes adversos asociados a errores de medicación en la población pediátrica. Construida enteramente bajo el ecosistema de **Python** utilizando **Flask** para el enrutamiento y servicio web, **Pandas** para la manipulación y análisis de datos en memoria, y **Matplotlib** para la generación de reportes gráficos. 

Este proyecto propone una alternativa programática, transparente y reproducible que sustituye las licencias cerradas de software de Business Intelligence (como Power BI) por código ejecutable de código abierto, facilitando el procesamiento relacional directamente en el servidor.

---

## 2. Arquitectura de Datos
El sistema ingesta y procesa tres fuentes de datos simuladas bajo estándares reales (CIE-10 y Minsalud) ubicadas en la carpeta `/data`:

1.  **Dataset Transaccional (`incidentes_farmacovigilancia.csv`):** Contiene 150 registros de incidentes hospitalarios pediátricos reales con variables demográficas (edad, sexo), diagnósticos CIE-10, principios activos involucrados, y la gravedad o severidad del daño.
2.  **Catálogo Dimensional (`catalogo_medicamentos_pediatricos.csv`):** Actúa como un diccionario maestro de medicamentos que define las alertas de similitud ortográfica y fonética (LASA), los riesgos asociados a la preparación (ej. reconstitución con agua) y las vías de administración aprobadas.
3.  **Golden Record de Dosificación (`guia_dosificacion_pediatrica.csv`):** Reglas clínicas de dosificación teórica recomendada que asocian el peso promedio poblacional por grupo etario con la dosis límite teórica en miligramos por kilogramo.

---

## 3. Metodología Analítica Aplicada
El flujo analítico está programado de principio a fin en el backend para asegurar la integridad de la auditoría médica:

*   **Limpieza y Perfilamiento:** Uso de `df.isnull()` y verificación de tipos de datos (`dtypes`) para identificar y reportar la completitud y validez de las columnas en la pestaña de Calidad de Datos.
*   **Análisis Descriptivo:** Aplicación de agrupaciones y frecuencias con `.value_counts()` y resúmenes descriptivos de variables continuas con `.describe()` para calcular KPIs clave y distribuciones por grupo etario o severidad.
*   **Ingeniería de Datos y Cruce Relacional:** Implementación de un triple cruzamiento (LEFT JOIN) relacional utilizando `pd.merge()` en memoria para comparar los medicamentos de los incidentes reales contra sus guías clínicas teóricas de dosificación y alertas de confusión LASA.

---

## 4. Guía de Archivos para la Sustentación Académica
Para la presentación del proyecto o sustentación académica ante la profesora, se recomienda abrir y señalar los siguientes fragmentos de código específicos para demostrar las respectivas competencias de ciencia de datos:

| Archivo a Mostrar | Qué debes señalar en el código | Competencia que demuestras al profesor |
| :--- | :--- | :--- |
| **`motor_analisis.py`** | El bloque donde haces el triple `pd.merge()` uniendo los 3 CSV en la función `auditar_cruce_datos()`. | *"Profesora, aquí apliqué la teoría de bases de datos relacionales directamente en memoria con Python (Pandas), uniendo la transacción con catálogos y guías sin necesidad de instalar motores SQL."* |
| **`motor_analisis.py`** | Uso de `.value_counts()` y `.describe()` en la función `obtener_calidad_datos()`. | *"Esta es la implementación de estadística descriptiva básica aplicada a variables categóricas y continuas para perfilar la calidad del dataset."* |
| **`app.py`** | La función `io.BytesIO()` y `base64.b64encode()` coordinada con `generar_graficos()`. | *"Para optimizar el servidor, renderizo los gráficos de Matplotlib directamente en la memoria RAM y los convierto a Base64, evitando generar basura o consumir espacio en el disco duro del servidor."* |
| **`templates/dashboard.html`** | Las variables `{{ grafico1 }}`, `{{ kpi_total }}` inyectadas dentro de las etiquetas HTML. | *"Aquí se evidencia la separación de capas: el frontend consume directamente las estructuras de datos calculadas en el backend sin depender de licencias de Power BI u otras herramientas."* |

---

## 5. Instrucciones de Ejecución
Para iniciar el panel interactivo en su entorno de desarrollo local:

1.  Asegúrese de activar su entorno virtual:
    ```bash
    source venv/bin/activate
    ```
2.  Instale las dependencias requeridas (si no están instaladas):
    ```bash
    pip install pandas matplotlib flask
    ```
3.  Ejecute la aplicación web:
    ```bash
    python app.py
    ```
4.  Abra su navegador web e ingrese a:
    `http://127.0.0.1:5000`
