import logging
import os
from logging.handlers import RotatingFileHandler
import subprocess
import sys

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

def ejecutar_script(nombre_script, scripts_dir):
    """
    Ejecuta un script como subproceso, captura su salida y la registra en el log.
    Retorna True si tuvo éxito (exit code 0), False si falló.
    """
    ruta_script = os.path.join(scripts_dir, nombre_script)
    logger.info(f"Ejecutando {nombre_script}...")

    resultado = subprocess.run(
        [sys.executable, ruta_script],  # sys.executable = ruta al python.exe actual
        capture_output=True,            # captura stdout y stderr en vez de mostrarlos directo
        text=True                       # decodifica bytes a string automáticamente
    )

    # Lo que el script imprimió normalmente (sus print() de validación, etc.)
    if resultado.stdout:
        logger.info(f"[{nombre_script}] stdout:\n{resultado.stdout}")

    # Lo que el script mandó como error (tracebacks, excepciones no capturadas)
    if resultado.stderr:
        logger.error(f"[{nombre_script}] stderr:\n{resultado.stderr}")

    if resultado.returncode == 0:
        logger.info(f"{nombre_script} completado correctamente.")
        return True
    else:
        logger.error(f"{nombre_script} falló con exit code {resultado.returncode}.")
        return False
    

def main():
    scripts_dir = os.path.join(base_dir, "scripts")

    pipeline = [
        "01_Obtener_datos.py",
        "02_Procesamiento_datos.py",
        "03_Carga_datos_Postgres.py",
    ]

    logger.info("=== Inicio de ejecución del pipeline ===")

    for script in pipeline:
        exito = ejecutar_script(script, scripts_dir)
        if not exito:
            logger.error(f"Pipeline detenido: {script} falló. No se ejecutarán los pasos siguientes.")
            sys.exit(1)  # el orquestador también reporta su propio exit code

    logger.info("=== Pipeline completado exitosamente ===")


if __name__ == "__main__":
    main()