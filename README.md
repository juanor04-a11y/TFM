# Diseño e implementación de una arquitectura Lakehouse para la para la correlación inteligente de tickets de incidencias de una plataforma OTT 


Proyecto de Trabajo Fin de Máster orientado al diseño e implementación de una arquitectura **Lakehouse en Microsoft Fabric** para la agrupación inteligente de tickets operativos OTT mediante técnicas de representación semántica, clustering e IA Generativa.

El objetivo principal es integrar tickets procedentes de diferentes mecanismos de ingesta, transformarlos siguiendo una arquitectura **Medallion (Bronze, Silver y Gold)**, generar embeddings semánticos y agrupar tickets potencialmente relacionados para facilitar su análisis operacional.

La solución combina ingesta batch y streaming, arquitectura Lakehouse/Medallion, procesamiento PySpark, embeddings con `all-MiniLM-L6-v2`, clustering mediante DBSCAN, IA Generativa y explotación de resultados en Power BI.

## Estructura del repositorio

```text
TFM/
│
├── data/
│   ├── ground_truth/
│   └── raw/
├── notebooks_Fabric/
├── PowerBI
│   └── TFM_PowerBI.pbix
├── src/
│   ├── ai_model/
│   ├── batch_data_generator/
│   ├── ott_ticket_intelligence/
│   └── streaming_data_producer/
│
├── .gitignore
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

### `data/`

Contiene los datos utilizados durante el desarrollo y evaluación.

- `raw/`: datos de entrada.
- `ground_truth/`: información de referencia para evaluar la calidad del clustering.

El *ground truth* se utiliza únicamente para evaluación y nunca como entrada para generar embeddings o decidir clusters.

### `notebooks_Fabric/`

Contiene los notebooks de Microsoft Fabric utilizados para la ingesta, transformación, generación de embeddings, clustering, agregación de grupos, generación de resúmenes y evaluación experimental.

La lógica experimental se mantiene separada del flujo operacional para mejorar la mantenibilidad, reproducibilidad y eficiencia. Estos notebooks usados durante las pruebas del proyecto se encuentran en `notebooks_Fabric/experiments`

### `PowerBI/`
Contiene el fichero para Power BI, con las vistas utilizadas obtenidas de las tablas en Gold. Las vistas son: 
- OTT Incident Overview: Vista general de los tickets, resumen de los incidentes, información contenida en los clusters etc... Se puede seleccionar el cluster y el servicio de OTT (VOD, EPG, Logic, etc...) para filtrar tickets
- Clustering Evaluation: Contiene las metricas utilizadas para obtener el mejor valor de eps y min_samples y así crear los clusters
- Incident Detail: Contiene el resumen de cada cluster generado con un modelo de IA generativa y una vista de los tickets que tiene cada cluster. De esta manera podemos comprobar si el modelo realmente funciona o no.

### `src/ai_model/`

Código relacionado con los componentes de IA utilizados por la solución, especialmente la generación de resúmenes y la interpretación de grupos.

### `src/batch_data_generator/`

Código utilizado para generar o preparar los tickets procesados mediante el flujo batch.

### `src/streaming_data_producer/`

Productor de eventos utilizado para simular la llegada de tickets en tiempo cercano al real mediante Kafka / Confluent Cloud.

```text
Ticket
  ↓
Kafka / Confluent Cloud
  ↓
Microsoft Fabric Eventstream
  ↓
Bronze.KafkaTickets
```

### `src/ott_ticket_intelligence/`

Paquete Python reutilizable que encapsula parte de la lógica principal del proyecto fuera de los notebooks de Microsoft Fabric. Su objetivo es desacoplar la lógica de negocio de la capa de orquestación, haciendo el código más reutilizable, mantenible y fácil de probar.
Esta separación permite que los notebooks se centren principalmente en cargar datos, recibir parámetros del pipeline, invocar los componentes del paquete y persistir los resultados.
El paquete se distribuye como un archivo .whl, que puede instalarse como librería personalizada en un Environment de Microsoft Fabric.

Los principales componentes son:
* **TicketEmbedder**: Encapsula la generación de embeddings semánticos a partir del texto de los tickets.
* **TicketClusterer**: Encapsula la ejecución operacional del algoritmo DBSCAN sobre los embeddings.
* **IncidentSummarizer**: Encapsula la interacción con el modelo de IA Generativa utilizado para interpretar los grupos detectados.
* **validators.py** contiene funciones de validación reutilizables para comprobar la calidad mínima de los datos antes de seguir con el pipeline.
# Tests unitarios

Este directorio contiene tests para los principales componentes del paquete `ott_ticket_intelligence`.

## Cobertura

- `TicketClusterer`: validación de parámetros, entradas, labels y estadísticas.
- `TicketEmbedder`: carga diferida, dimensionalidad, forma y normalización de embeddings.
- `IncidentSummarizer`: límite de contexto, reproducibilidad, validación JSON y estructura de salida.
- `validators.py`: datasets vacíos, duplicados y nulos.

## Ejecutar

Desde la raíz del proyecto:

```bash
python -m pip install pytest
pytest -v
```

Si quieres ejecutar también los tests Spark:

```bash
python -m pip install pyspark
pytest -v
```

Si `pyspark` no está instalado, `test_validators.py` se omitirá automáticamente.

## Arquitectura Medallion

### Bronze

- `Bronze.Tickets`: tickets procedentes del flujo batch.
- `Bronze.KafkaTickets`: tickets recibidos mediante streaming.

### Silver

- `Silver.Tickets`: tickets integrados, limpiados, normalizados y deduplicados.
- `Silver.TicketEmbeddings`: representación vectorial de los tickets.

Los embeddings se generan utilizando `all-MiniLM-L6-v2`, que produce vectores de 384 dimensiones.

### Gold

- `Gold.TicketClusters`: asignación de cada ticket a un cluster.
- `Gold.ClusteredTickets`: tickets enriquecidos con la información de clustering.
- `Gold.IncidentGroups`: agregación de tickets por `cluster_id`.
- `Gold.IncidentSummaries`: resúmenes generados mediante IA Generativa.

Durante la fase experimental pueden existir tablas adicionales para métricas y evaluación.

## Clustering

El agrupamiento se realiza mediante **DBSCAN** utilizando distancia coseno sobre los embeddings.

Configuración utilizada en el prototipo:

```text
eps = 0.25
min_samples = 3
metric = cosine
```

Estos parámetros pueden enviarse desde Microsoft Fabric Pipeline.

El campo `incident_id` no participa en el clustering. Se utiliza únicamente como referencia para comparar los clusters generados con los incidentes conocidos del dataset sintético.

## Evaluación

La calidad del clustering se analiza mediante:

- Adjusted Rand Index (ARI)
- Normalized Mutual Information (NMI)
- Pairwise Precision
- Pairwise Recall
- Pairwise F1
- análisis de grupos mezclados

La evaluación de embeddings incluye además análisis de similitud coseno, distribución de similitudes y thresholds utilizados únicamente con fines descriptivos.

## IA Generativa

Los tickets pertenecientes a un mismo cluster se agregan en `Gold.IncidentGroups`.

Estos grupos se utilizan como entrada para generar información estructurada como:

- título
- resumen
- posible problema
- ámbito afectado
- acción recomendada
- advertencia cuando el grupo parece heterogéneo (columna warning).

Los resultados se almacenan en `Gold.IncidentSummaries`.

La IA Generativa actúa como una capa de síntesis posterior al clustering y no interviene en la creación de los clusters.

## Requisitos

Se recomienda utilizar Python 3.11 o superior.

Instalación:

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Microsoft Fabric

El pipeline operacional ejecuta de forma secuencial:

```text
Ingesta
  ↓
Bronze
  ↓
Silver
  ↓
Embeddings
  ↓
Clustering
  ↓
Incident Groups
  ↓
IA Generativa
```

Los principales parámetros, como `eps`, `min_samples`, el modelo de embeddings o el número máximo de tickets enviados al modelo generativo, pueden centralizarse en el pipeline y transmitirse a los notebooks.

## Visualización

Los resultados de la capa Gold se consumen desde **Power BI Desktop** mediante el **SQL Analytics Endpoint de Microsoft Fabric**.

El informe permite analizar grupos detectados, tamaño y composición de clusters, métricas, resúmenes generados y detalle de tickets.

## Objetivo del proyecto

El proyecto demuestra cómo una arquitectura moderna de Ingeniería de Datos puede integrar:

**Lakehouse + Streaming + Embeddings + Clustering + IA Generativa + BI**

Y de esta manera mejorar el análisis y consolidación de tickets operativos en un contexto OTT.
