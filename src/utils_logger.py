import logging
import os
import sys

def setup_logger(name="PulsEvents"):
    """
    Configure un logger qui écrit dans la console ET dans un fichier.
    """
    # Création du dossier logs s'il n'existe pas
    os.makedirs("logs", exist_ok=True)
    
    # Configuration du format
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Éviter les doublons de logs si on reload
    if logger.handlers:
        return logger

    # 1. Handler Fichier (Pour garder une trace)
    file_handler = logging.FileHandler("logs/activity.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 2. Handler Console (Pour voir en direct)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Instance globale
logger = setup_logger()