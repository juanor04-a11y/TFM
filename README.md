# TFM — OTT Ticket Intelligence

Proyecto de TFM orientado a Ingeniería de Datos para agrupar tickets operativos OTT mediante Microsoft Fabric, embeddings semánticos e IA Generativa.

## Estructura inicial

```text
tfm_ott_ticket_intelligence/
├── src/
│   └── generate_synthetic_tickets.py
├── data/
│   ├── raw/
│   └── ground_truth/
├── requirements.txt
├── .gitignore
└── README.md
```

## Crear entorno local

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Generar dataset sintético

```powershell
python src/generate_synthetic_tickets.py
```

Por defecto genera:

- 1.000 tickets.
- 50 incidentes subyacentes.
- Semilla aleatoria 42.
- Aproximadamente 10 % de tickets aislados.
- Aproximadamente 5 % de duplicados intencionados.

Los archivos se generan en:

```text
data/raw/synthetic_ott_tickets.csv
data/ground_truth/incident_ground_truth.csv
```

También se pueden cambiar los parámetros:

```powershell
python src/generate_synthetic_tickets.py --tickets 2000 --incidents 80 --seed 42
```

## Ground truth

`incident_id` representa el incidente real al que pertenece un ticket y se utilizará únicamente para evaluar el resultado del modelo. No debe utilizarse como variable durante el clustering.

## Próximos pasos

1. Crear workspace y Lakehouse en Microsoft Fabric.
2. Ingerir `synthetic_ott_tickets.csv` en la capa Bronze.
3. Crear notebook Bronze → Silver.
4. Generar embeddings.
5. Comparar TF-IDF frente a embeddings.
6. Aplicar clustering.
7. Evaluar los grupos contra `incident_id`.
8. Publicar resultados en Power BI.
