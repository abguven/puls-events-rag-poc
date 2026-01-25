import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Imports LangChain V1
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.agents import create_agent

from src.utils_logger import logger
from src.tools.date_resolver import resolve_date_expression
from langchain_core.tools import tool
from src.config import LLM_MODEL_NAME, SEARCH_K, SEARCH_RESULTS, MODEL_TEMPERATURE

load_dotenv()

# --- CONFIGURATION ---
INDEX_PATH = str(Path("./data/faiss_index"))
API_KEY = os.getenv("MISTRAL_API_KEY")

# Chargement FAISS global
print("📚 Chargement de l'index FAISS...")
embeddings = MistralAIEmbeddings(model="mistral-embed")
try:
    vectorstore = FAISS.load_local(
        INDEX_PATH, 
        embeddings, 
        allow_dangerous_deserialization=True
    )
except Exception as e:
    raise FileNotFoundError(f"❌ Impossible de charger FAISS : {e}")

# --- OUTIL INTELLIGENT ---
@tool
def search_events(query: str, date_start: str = None, date_end: str = None, price_type: str = None, zipcode: str = None):
    """
    Cherche des événements à Paris avec des filtres précis.
    Args:
        query: Le sujet principal (ex: 'Concert', 'Atelier', 'Théâtre').
        date_start: Date exacte au format YYYY-MM-DD (ex: '2026-01-10').
        date_end: Date de fin (YYYY-MM-DD) si c'est une période.
        price_type: 'gratuit' ou 'payant'.
        zipcode: Code postal (ex: '75018').
    """
    
    # Log pour vérifier la période
    log_date = date_start
    if date_start and date_end:
        log_date = f"{date_start} -> {date_end}"
    elif date_start:
        log_date = f">= {date_start}"
        
    logger.info(f"🔎 RECHERCHE : Sujet='{query}' | Date={log_date} | Prix={price_type} | CP={zipcode}")
    
    # Recherche Large (k=3000) pour avoir de la matière à filtrer
    results_with_scores  = vectorstore.similarity_search_with_score(query, k=SEARCH_K)
    
    filtered_docs = []
    
    # Filtrage Python STRICT
    for doc, score in results_with_scores:
                
        meta = doc.metadata
        keep = True

        # Filtre DATE (Période ou Singleton)
        if date_start:
            doc_date = str(meta.get('start_date', ''))[:10]
        
            # Cas 1 : Période (Ex: Semaine prochaine / Mois prochain)
            if date_end:
                # On garde si l'événement est DANS la plage [date_start, date_end]
                if not (date_start <= doc_date <= date_end):
                    keep = False
        
            # Cas 2 : Singleton (Ex: Demain / Ce soir / À partir de)
            else:
                # On garde tout ce qui est APRES ou EGAL
                if doc_date < date_start:
                    keep = False                
                
        
        # Filtre PRIX
        if keep and price_type:
            # Si on demande gratuit, on vérifie que 'gratuit' est dans le type
            meta_price = str(meta.get('price_type', '')).lower()
            if price_type.lower() == 'gratuit' and 'gratuit' not in meta_price:
                keep = False
            # Si on demande payant, on peut exclure les 100% gratuits si besoin, 
            # mais souvent 'payant' est implicite.
                
        # Filtre LIEU (Zipcode)
        if keep and zipcode:
            meta_zip = str(meta.get('zipcode', ''))
            if zipcode not in meta_zip:
                keep = False
                        
        if keep:
            filtered_docs.append((doc, score))
            
    # Tri par date croissante si l'utilisateur a précisé une date
    if date_start:
        # Tri par Date (Priorité 1) puis par Score (Priorité 2)
        # x[0] est le doc, x[1] est le score
        filtered_docs.sort(key=lambda x: (str(x[0].metadata.get('start_date', '')), x[1]))
    else:
        # Tri par Score uniquement (Pertinence)
        filtered_docs.sort(key=lambda x: x[1])
        
            
    # Sélection Finale
    # final_docs = filtered_docs[:SEARCH_RESULTS] # On garde le top N filtré
    final_docs = [doc for doc, score in filtered_docs[:SEARCH_RESULTS]]
    
    response_text = ""
    if not final_docs:
        response_text = f"Aucun événement trouvé pour '{query}' avec ces critères (Date: {date_start}, Prix: {price_type})."
        logger.warning(f"⚠️ {response_text}") 
        return response_text

    # Formatage de la réponse pour l'agent
    response_text = f"Trouvé {len(final_docs)} événements correspondants :\n"
    for doc in final_docs:
        response_text += f"---\n{doc.page_content}\n"

    logger.info(f"✅ {response_text}")        
    return response_text

# --- AGENT ---
class RAGAgent:
    def __init__(self):
        self.llm = ChatMistralAI(
            model_name=LLM_MODEL_NAME, 
            temperature=MODEL_TEMPERATURE,
            max_retries=3
        )
        
        tools = [search_events, resolve_date_expression] 
        
        # System Prompt optimisé pour l'extraction de paramètres
        self.system_message_template = """Tu es un assistant spécialisé EXCLUSIVEMENT sur les événements à Paris et sa région.
            Nous sommes le {current_date}.
        
            🚨 RÈGLE DE SÉCURITÉ PRIORITAIRE :
            Si l'utilisateur mentionne une ville hors de l'Île-de-France (Lyon, Marseille...), REFUSE DE RÉPONDRE.
            Dis : "Désolé, je ne couvre que Paris et l'Île-de-France."

            POUR LES DEMANDES SUR PARIS, SUIS CETTE SÉQUENCE STRICTE :

            ÉTAPE 1 : ANALYSE TEMPORELLE
            Si la question contient une notion de temps relative (ex: "ce week-end", "mardi prochain", "dans un mois"), tu DOIS utiliser l'outil 'resolve_date_expression' pour obtenir la date précise.
            N'essaie pas de deviner la date toi-même.

            ÉTAPE 2 : RECHERCHE D'ÉVÉNEMENTS
            Utilise l'outil 'search_events' avec les paramètres extraits :
            - query : Mots-clés (ex: 'Concert Jazz'). ATTENTION : NE PAS INCLURE le nom de la ville ou du quartier dans ce paramètre.
            - date_start / date_end : Les dates ISO exactes obtenues à l'étape 1 (ou celle donnée explicitement).
            - price_type : 'gratuit' uniquement si demandé.
            - zipcode : Code postal si un quartier est cité.

            ÉTAPE 3 : RÉPONSE SYNTHÉTIQUE
            Les documents ci-dessous te sont fournis, déjà triés par ordre chronologique. Ta mission est de répondre à la question en te basant sur eux.

            RÈGLES DE SYNTHÈSE :
            1.  **FILTRE HORAIRE :** Si l'utilisateur précise un moment de la journée (ex: "ce soir" > 18h, "cet après-midi" 14h-18h), sélectionne UNIQUEMENT les événements dont les horaires correspondent.
            2.  **SÉLECTION :** Choisis les **5 événements les plus pertinents** qui correspondent à la demande.
            3.  **FORMAT :** Pour chaque événement retenu, présente-le clairement (Titre, Date précise, Lieu, Prix).
            4.  **HONNÊTETÉ :** Si après filtrage il ne reste aucun événement, dis-le poliment ("Je n'ai rien trouvé pour cette période précise...").
            """
        
        self.agent = create_agent(
            model=self.llm,
            tools=tools
        )

    def ask(self, question):
        # Date dynamique
        now = datetime.now()
        current_date_str = now.strftime("%A %d %B %Y")
        
        
        
        # Injection de la date dans le template
        formatted_system = self.system_message_template.format(current_date=current_date_str)
        
        logger.info(f"🤖 [AGENT] Reçoit la question : {question}")
        logger.info(f"📅 [CONTEXTE] {current_date_str}")        
        
        # On place notre consigne système en "message utilisateur" pour forcer le contexte
        messages = [
            {"role": "user", "content": f"INSTRUCTION SYSTEME: {formatted_system}\n\nQUESTION UTILISATEUR: {question}"}
        ]
        
        try:
            result = self.agent.invoke({"messages": messages}) 
        
            # Le résultat est dans la dernière réponse de l'assistant
            return result["messages"][-1].content
        except Exception as e:
            logger.error(f"❌ ERREUR CRITIQUE AGENT : {e}")
            raise e        

# --- TEST ---
if __name__ == "__main__":
    bot = RAGAgent()
    while True:
        q = input("\nVotre question : ")
        if q.lower() in ["exit", "quit"]: break
        try:
            print("\n💬 Réponse :")
            print(bot.ask(q))
        except Exception as e:
            print(f"❌ Erreur : {e}")