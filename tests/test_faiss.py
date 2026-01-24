# tests/test_faiss.py
import sys, os, getpass
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_mistralai import MistralAIEmbeddings
from src.config import FAISS_INDEX_PATH

# Chargement des secrets
load_dotenv()

if 'MISTRAL_API_KEY' not in os.environ:
    os.environ["MISTRAL_API_KEY"] = getpass.getpass("Enter your Mistral API key: ")

def check_faiss_index():
    print("🕵️‍♂️ AUDIT DE LA BASE VECTORIELLE (FAISS)...")
    
    # 1. Vérifier si le dossier existe
    if not os.path.exists(FAISS_INDEX_PATH):
        print(f"❌ ERREUR : Le dossier {FAISS_INDEX_PATH} n'existe pas. Lancez vectorizer.py d'abord.")
        return

    # 2. Recharger l'index depuis le disque
    try:
        embeddings = MistralAIEmbeddings(model="mistral-embed")
        
        # Chargement de la base (allow_dangerous_deserialization est requis pour les fichiers pickle locaux)
        db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        print("✅ Index chargé avec succès.")
        
    except Exception as e:
        print(f"❌ ERREUR lors du chargement de l'index : {e}")
        return

    # 3. Vérification du nombre de documents (Point de vigilance du PDF)
    # L'index Faiss brut est accessible via db.index
    total_vectors = db.index.ntotal
    print(f"📊 Nombre total de vecteurs dans l'index : {total_vectors}")
    
    # On s'attend à avoir environ 2607 (ton chiffre précédent). 
    # Si c'est 0 ou très bas, il y a un problème.
    if total_vectors < 100:
        print("⚠️ ALERTE : L'index semble vide ou presque vide !")
    else:
        print("✅ Le volume de données semble cohérent.")

    # 4. Test de Recherche Sémantique (Recommandation du PDF : "Vérifier l'efficacité")
    query = "Soirée Jazz à Paris"
    print(f"\n🧪 Test de recherche pour la requête : '{query}'")
    
    # On demande les 2 documents les plus proches
    results = db.similarity_search(query, k=2)
    
    if not results:
        print("❌ AUCUN RÉSULTAT TROUVÉ (Bizarre...)")
    else:
        for i, doc in enumerate(results):
            print(f"\n--- Résultat {i+1} ---")
            print(f"📄 Contenu : {doc.page_content[:200]}...") # On affiche le début du texte
            print(f"🏷️ Metadata : {doc.metadata}")
            
            # Vérification visuelle
            content_lower = doc.page_content.lower()
            if "jazz" in content_lower or "concert" in content_lower or "musique" in content_lower:
                print("✅ PERTINENCE : Ce résultat semble lié à la musique/jazz.")
            else:
                print("⚠️ PERTINENCE DOUTEUSE : Vérifie manuellement si ça a du sens.")

if __name__ == "__main__":
    check_faiss_index()