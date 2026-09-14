"""
Para poder utilizar el modelo en Microsoft Fabric se ha optado por descargarlo y luego se ha añadido al Workspace.
Este código descarga el modelo para que posteriormente se pueda subir a nuestro Workspace
"""

from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="sentence-transformers/all-MiniLM-L6-v2",
    local_dir="all-MiniLM-L6-v2"
)