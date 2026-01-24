# tests/test_setup.py
import sys
import os
from dotenv import load_dotenv

def test_environment_setup():
    """
    Vérifie l'installation des bibliothèques clés et la présence de la clé API.
    Lève une exception si une vérification échoue.
    """
    print("--- Vérification de l'environnement ---")
    
    try:
        import pandas as pd
        print(f"✅ Pandas OK (v{pd.__version__})")
        
        import langchain
        print(f"✅ LangChain OK (v{langchain.__version__})")
        
        import faiss
        index = faiss.IndexFlatL2(5)
        print(f"✅ Faiss-cpu OK (Index créé)")
        
        import mistralai
        print(f"✅ MistralAI OK")
        
    except ImportError as e:
        print(f"❌ Erreur d'import : {e}")
        raise  # Fait remonter l'erreur pour arrêter le pipeline

    # Vérification de la clé API
    load_dotenv()
    if not os.getenv("MISTRAL_API_KEY"):
        # On lève une ValueError, qui fera planter le script
        raise ValueError("MISTRAL_API_KEY non trouvée dans le fichier .env !")
    else:
        print("✅ MISTRAL_API_KEY OK")

if __name__ == "__main__":
    try:
        test_environment_setup()
        print("\n✅ Environnement validé avec succès.")
    except Exception as e:
        print(f"\n❌ ERREUR FATALE : {e}")
        # On quitte avec un code d'erreur pour que le pipeline s'arrête
        sys.exit(1)