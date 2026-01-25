# Configuration du POC Puls-Events

# 1. Choix du Modèle (Cerveau)
# Options : "mistral-large-latest" (Best), "mistral-small-latest" (Fast), "mistral-tiny" (Cheap)
LLM_MODEL_NAME = "mistral-large-latest"
MODEL_TEMPERATURE=0.5


# 2. Gestion de la Mémoire
# True : Le bot se souvient des messages précédents
# False : Le bot oublie tout à chaque question (Mode Amnésique / Test unitaire)
ENABLE_MEMORY = False

# 3. Paramètres de Recherche
SEARCH_K = 3000  # Nombre de candidats FAISS avant filtrage
SEARCH_RESULTS = 20  # Nombre final de résultats envoyés au LLM

# 4. Chemins vers les données
CLEAN_SOURCE_DATA_PATH = "./data/paris_events_clean.csv"
FAISS_INDEX_PATH = "./data/faiss_index"