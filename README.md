# Living on the Edge 🏘️

Aplicación desarrollada en Streamlit para ayudar a encontrar el municipio ideal en la Comunidad de Madrid según accesibilidad, calidad de vida y prioridades personales.

## Descripción

Esta herramienta permite a los residentes elegir entre municipios de menos de 50.000 habitantes, clasificándolos según tres dimensiones principales:

- **Accesibilidad**: Tiempo mensual de desplazamiento a servicios esenciales (supermercados, sanidad, deporte, educación).
- **Calidad de vida**: Calidad del aire, educación, atractivo urbanístico, infraestructura de transporte y dinamismo económico.
- **Asequibilidad**: Precio de la vivienda por m².

## Funcionalidades principales

### 1. Cuestionario personalizado

El usuario proporciona información sobre su situación y preferencias a través de un formulario interactivo. Se solicitan las frecuencias de uso para diversos servicios:

- **Coche**: Casi nunca (0-1 días/semana), Ocasionalmente (2-3 días/semana), Frecuentemente (4-5 días/semana), Casi siempre (6-7 días/semana).
- **Supermercado**: 1 vez/semana, 2 veces/semana, 3 veces/semana, 4 o más veces/semana.
- **Deporte**: Mismas opciones que el coche.
- **Sanidad**: Solo emergencias, Revisiones regulares, Acompañar personas de riesgo, Enfermedad recurrente.

También se pregunta sobre la situación familiar (presencia de hijos, tipo de colegio preferido, etapas educativas) y un filtro para la población de los municipios. Finalmente, el usuario califica la importancia de 7 criterios principales en una escala del 0 al 10:

- **Ahorro de tiempo en desplazamientos**: Tiempo semanal en viajes a servicios esenciales. Este tiempo se calcula con las respuestas del usuario para las preguntas anteriores.
- **Calidad de la educación**: Calidad de los centros educativos del municipio.
- **Calidad del aire y del entorno**: Calidad ambiental medida por estaciones de monitoreo.
- **Atractividad de las viviendas**: Estado de conservación del parque inmobiliario.
- **Calidad de las infraestructuras de transporte**: Disponibilidad de transporte público y carreteras.
- **Dinamismo económico**: Actividad económica y tejido empresarial.
- **Precio de la vivienda**: Coste medio por metro cuadrado.

### 2. Ponderación inteligente (AHP)

El **Proceso Analítico Jerárquico** (AHP, por sus siglas en inglés) transforma las calificaciones subjetivas del usuario (escala 0-10) en pesos normalizados matemáticamente consistentes. El algoritmo construye una **matriz de comparaciones pareadas** a partir de las prioridades indicadas, calcula el **vector propio principal** para obtener los pesos, y valida la coherencia mediante el **ratio de consistencia** (CR). Si el CR supera el umbral aceptable (0.1), el sistema aplica correcciones automáticas para garantizar la consistencia. Los pesos finales se muestran de forma transparente en la barra lateral, permitiendo al usuario verificar cómo sus prioridades se traducen en la ponderación final.

### 3. Visualizaciones interactivas

La aplicación ofrece múltiples vistas complementarias para explorar los resultados:

- **Vista de mapa**: Mapa coroplético interactivo coloreado por puntuación, con selección de municipios mediante clic.

- **Vista de lista**: Tarjetas paginadas ordenadas por puntuación, mostrando imagen y métricas clave de cada municipio.

- **Panel de detalles**: Desglose completo con barras de progreso por criterio y contribución de cada uno al score final.

- **Modo comparación**: Visualización lado a lado de dos municipios para comparar directamente todos sus indicadores.

### 4. Exportación de resultados

Los resultados completos pueden descargarse en **formato CSV** para análisis posterior. El archivo exportado incluye para cada municipio: nombre, coordenadas, puntuación global normalizada (0-100), puntuaciones normalizadas de cada criterio individual, contribuciones ponderadas al score final, y valores brutos de todos los indicadores. Esto permite al usuario realizar análisis personalizados, crear gráficos adicionales, o compartir los resultados con otras personas.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
streamlit run app.py
```

## Estructura del proyecto

```md
Datathon-LODCoreMadrid/
├── app.py                 # Punto de entrada principal
├── config/
│   ├── constants.py       # Criterios, etiquetas y mapeos
│   └── styles.py          # Estilos CSS y configuración
├── core/
│   ├── accessibility.py   # Cálculo de tiempos de desplazamiento
│   ├── ahp.py             # Algoritmos AHP
│   ├── data_loader.py     # Carga de datos e imágenes
│   └── scoring.py         # Normalización y ranking
├── ui/
│   ├── questionnaire.py   # Formulario de entrada
│   ├── map_view.py        # Mapa interactivo
│   ├── list_view.py       # Tarjetas de municipios
│   ├── details_view.py    # Desglose detallado y comparación
│   └── comparison_view.py # Vista de comparación
├── data/
│   └── merged_dataset.csv
├── boundaries/
│   └── recintos_municipales_inspire_peninbal_etrs89.shp
└── assets/
    └── municipalities/    # Imágenes de municipios
```

## Metodología

### Cálculo de accesibilidad

El **tiempo semanal de desplazamiento** personalizado se calcula mediante la siguiente fórmula:

$$\text{Horas semanales} = \sum_{s \in \text{servicios}} \left( \text{visitas/semana}_s \times \frac{2 \times \text{minutos}_s}{60} \right)$$

Los **servicios incluidos** son:

- **Supermercados**: Frecuencia directamente especificada por el usuario (1, 2, 3 o 4.5 veces/semana).
- **Gasolineras**: Calculada proporcionalmente al uso del coche (hasta 1 visita/semana para usuarios frecuentes).
- **Instalaciones deportivas**: Frecuencia directamente especificada por el usuario (0.5, 2.5, 4.5 o 6.5 veces/semana).
- **Sanidad**: La frecuencia total se reparte en 20% para médico de cabecera y 80% para farmacia, según el perfil sanitario del usuario.
- **Educación**: 5 visitas/semana (días escolares) divididas equitativamente entre los niveles educativos seleccionados (Preinfantil, Infantil, Primaria, Secundaria), solo si tiene hijos.

Los tiempos de desplazamiento ($\text{minutos}_s$) se calculan como una **combinación ponderada entre coche y transporte público**, según la frecuencia de uso del coche declarada por el usuario:

$$\text{minutos}_s = w_{\text{coche}} \times \text{minutos}_{\text{coche}} + (1 - w_{\text{coche}}) \times \text{minutos}_{\text{transporte público}}$$

donde $w_{\text{coche}} = \frac{\text{frecuencia coche (días/semana)}}{7}$ representa la proporción de uso del coche. Los tiempos se obtienen de datos reales de accesibilidad para cada municipio.

### Normalización de criterios

Para hacer comparables todos los criterios, se aplica **normalización min-max** llevando todos los valores al rango [0, 1]:

**Criterios de beneficio** (mayor es mejor - como calidad del aire, educación, etc.):

$$\text{normalizado} = \frac{x - x_{\min}}{x_{\max} - x_{\min}}$$

**Criterios de coste** (menor es mejor - como precio de vivienda, tiempo de accesibilidad):

$$\text{normalizado} = 1 - \frac{x - x_{\min}}{x_{\max} - x_{\min}}$$

Donde $x$ es el valor del criterio para un municipio específico, y $x_{\min}$ y $x_{\max}$ son los valores mínimo y máximo observados en todo el conjunto de municipios filtrados.

### Puntuación final

La **puntuación agregada** de cada municipio se obtiene mediante suma ponderada:

$$\text{Score} = \sum_{i=1}^{7} (\text{criterio normalizado}_i \times \text{peso AHP}_i)$$

Esta puntuación se escala al rango [0, 100] para facilitar la interpretación:

$$\text{Score final} = \frac{\text{Score}}{\text{Score}_{\max}} \times 100$$

Donde $\text{Score}_{\max}$ es la puntuación máxima teórica posible (1.0 en este caso, ya que todos los criterios están normalizados). Los municipios se ordenan descendentemente por este score final, mostrando primero las mejores opciones según las preferencias del usuario.

## Fuentes de datos

La aplicación integra datos de múltiples fuentes oficiales:

- **Límites geográficos**: Recintos municipales de INSPIRE (sistema de referencia ETRS89) para la representación cartográfica y el mapa interactivo.

- **Demografía y población**: Datos del **Instituto Nacional de Estadística (INE)**, incluyendo población total por municipio y distribución demográfica por grupos de edad y género.

- **Precios de vivienda**: Precio medio por metro cuadrado obtenido de **Idealista**, utilizado como indicador de asequibilidad.

- **Accesibilidad a servicios**: Tiempos de desplazamiento en coche y transporte público a diferentes servicios (supermercados, sanidad, educación, deporte, gasolineras) calculados a partir de datos de la **Comunidad de Madrid** y **OpenStreetMap** (columnas ACC_* y OSM_*).

- **Indicadores de calidad**: Atributos de calidad del aire, educación, edificación, infraestructuras de transporte y dinamismo económico provenientes de **datos abiertos de la Comunidad de Madrid** (columnas ATR_*), procesados mediante clustering estadístico.

## Licencia

Uso educativo e investigación. Las fuentes de datos conservan sus licencias originales.

## Autores

_MiniEdgers_ - Datathon UC3M 2025