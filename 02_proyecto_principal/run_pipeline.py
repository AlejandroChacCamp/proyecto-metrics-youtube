import logging
import os
from logging.handlers import RotatingFileHandler

# Rutas base — mismo patrón __file__ que ya aplicaste en los 3 scripts
base_dir = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(base_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)  # crea logs/ si no existe, no falla si ya existe
log_path = os.path.join(logs_dir, "pipeline.log")

# 1. El logger — el objeto al que tu código le habla
logger = logging.getLogger("pipeline")
logger.setLevel(logging.INFO)  # umbral: INFO para arriba (descarta DEBUG)

# 2. El formatter — cómo se ve cada línea
formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 3a. Handler para archivo, con rotación (lo que vimos: tamaño máximo + respaldos)
file_handler = RotatingFileHandler(
    log_path, maxBytes=2_000_000, backupCount=5, encoding="utf-8"
)
file_handler.setFormatter(formatter)

# 3b. Handler para pantalla — confirmaste que quieres ver ambos a la vez
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# El logger usa AMBOS handlers — cada mensaje va a los dos destinos
logger.addHandler(file_handler)
logger.addHandler(console_handler)