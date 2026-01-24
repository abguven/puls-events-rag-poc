import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_mistralai import MistralAIEmbeddings
from langchain_core.documents import Document 
from pathlib import Path
from dotenv import load_dotenv
import time, os, getpass
from config import CLEAN_SOURCE_DATA_PATH, FAISS_INDEX_PATH

load_dotenv()

if 'MISTRAL_API_KEY' not in os.environ:
    os.environ["MISTRAL_API_KEY"] = getpass.getpass("Enter your Mistral API key: ")

class EventVectorizer:
    """
    Transforme le CSV nettoyé en une base vectorielle FAISS.
    Prépare :
    1. Le 'Content Blob' : Texte lisible pour le LLM (avec heures, prix, description).
    2. Les 'Metadata' : Champs structurés pour le filtrage (Date ISO, Zipcode, Prix).
    """

    def __init__(self, data_path=CLEAN_SOURCE_DATA_PATH, index_path=FAISS_INDEX_PATH):
        self.data_path = Path(data_path)
        self.index_path = Path(index_path)
        
        print("📥 Initialisation du modèle Mistral (API)...")
        self.embeddings = MistralAIEmbeddings(
            model="mistral-embed",
        )

    def _format_date_for_llm(self, date_str):
        """Transforme une date ISO en format humain pour le Blob."""
        if pd.isna(date_str) or str(date_str).strip() == "":
            return ""
        try:
            # On parse la date string
            dt = pd.to_datetime(date_str)
            # Format : 12/05/2025 à 20h30
            return dt.strftime("%d/%m/%Y à %Hh%M")
        except:
            print(f"Erreur lors de la conversion de la date {date_str}")
            return str(date_str)
        

    def load_data(self):
        if not self.data_path.exists():
            raise FileNotFoundError(f"❌ Fichier non trouvé: {self.data_path}")
        
        # On lit le CSV en forçant tout en string pour éviter les erreurs de type
        df = pd.read_csv(self.data_path, dtype=str).fillna("")
        print(f"📊 Chargement de {len(df)} événements depuis le CSV.")
        
        documents = []
        for _, row in df.iterrows():
            
            # --- CONSTRUCTION DU BLOB (Ce que le LLM va lire) ---
            # On soigne le formatage pour donner un contexte clair à Mistral
            
            start_str = self._format_date_for_llm(row.get('date_start'))
            end_str = self._format_date_for_llm(row.get('date_end'))
            
            # Gestion de l'affichage de la date (Début - Fin)
            date_display = start_str
            if end_str and end_str != start_str:
                date_display += f" (jusqu'au {end_str})"
            
            # Construction du texte
            text_blob = (
                f"Titre: {row.get('title')}\n"
                f"Créneau: {date_display}\n"
                f"Lieu: {row.get('address_name')} ({row.get('address_zipcode')})\n"
                f"Prix: {row.get('combined_price')}\n"
                f"Description: {row.get('description')}"
            )
            
            # --- CONSTRUCTION DES METADATA (Pour les filtres FAISS) ---
            meta = {
                "source_id": row.get('id'),
                "title": row.get('title'),                      # Utile pour afficher le titre dans la source
                "start_date": row.get('date_start'),            # Format ISO indispensable pour le filtre temporel
                "zipcode": str(row.get('address_zipcode', '')), # Pour filtrer par arrondissement
                "price_type": row.get('price_type').lower(),    # Pour filtrer 'gratuit'
                "tags": row.get('tags').lower(),                # N'est pas utilisé pour le POC
                "image": row.get('image_url')                   # N'est pas utilisé pour le POC
            }
            
            doc = Document(page_content=text_blob, metadata=meta)
            documents.append(doc)
            
        print(f"✅ {len(documents)} documents structurés prêts.")
        return documents

    def create_index(self):
        docs = self.load_data()
        
        print(f"🧠 Début de la vectorisation de {len(docs)} chunks...")
        start_time = time.time()
        
        vectorstore = FAISS.from_documents(docs, self.embeddings)
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏱️ Vectorisation terminée en {duration:.2f} secondes ({(duration/len(docs)):.3f} s/doc).")
        
        vectorstore.save_local(self.index_path)
        print(f"💾 Index FAISS sauvegardé dans : {self.index_path.resolve()}")

if __name__ == "__main__":
    try:
        vectorizer = EventVectorizer()
        vectorizer.create_index()
    except Exception as e:
        print(f"❌ Erreur critique : {e}")