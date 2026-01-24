# tools/date_resolver.py
import os
import json
from datetime import datetime
from langchain_core.tools import tool
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv

load_dotenv()

DATE_SYSTEM_PROMPT = """Tu es un expert en extraction de dates temporelles.

ENTRÉE : Une expression temporelle
DATE DE RÉFÉRENCE (AUJOURD'HUI) : {date_ref}

OBJECTIF : Convertir l'expression en JSON.

RÈGLES DE LOGIQUE TEMPORELLE (CRITIQUE) :
1.  **VERS LE FUTUR UNIQUEMENT** :
    - Si une date fixe (ex: "le 5 janvier", "Noël", "le nouvel an") est DÉJÀ PASSÉE par rapport à la date de référence, c'est obligatoirement l'année suivante (+1 an).
    - Exemple : Si on est le 13 janvier et qu'on dit "le 2 janvier", c'est le 2 janvier de l'année D'APRÈS.

2.  **SINGLETON vs PÉRIODE** :
    - "fin [mois]", "fin janvier", "le 20", "demain" → Retourne {{"date": "..."}} (Le dernier jour ou le jour précis).
    - "le mois de...", "semaine prochaine", "ce weekend" → Retourne {{"debut": "...", "fin": "..."}}.

3.  **CALENDRIER** :
    - Gère correctement les années bissextiles pour février (28 ou 29 jours).
    - Semaine : Lundi au Dimanche.

FORMAT DE SORTIE (JSON PUR) :
- Cas date unique : {{"date": "YYYY-MM-DD"}}
- Cas période : {{"debut": "YYYY-MM-DD", "fin": "YYYY-MM-DD"}}

EXEMPLES (Avec Ref: 2026-06-15) :
- "le 10 juin" -> {{"date": "2027-06-10"}} (Car 10 juin est passé)
- "fin juillet" -> {{"date": "2026-07-31"}}
- "juillet" -> {{"debut": "2026-07-01", "fin": "2026-07-31"}}
"""


@tool
def resolve_date_expression(expression: str):
    """
    Convertit une expression temporelle naturelle (ex: 'ce week-end', 'mardi prochain') 
    en date ISO précise au format JSON.
    Utilise ce tool dès que l'utilisateur mentionne une notion de temps.
    """
    # 1. Config du petit cerveau dédié aux dates
    llm_date = ChatMistralAI(
        model="mistral-large-latest", # On garde le large car il est fort en logique
        temperature=0,
        api_key=os.getenv("MISTRAL_API_KEY")
    )
    
    # 2. Date de référence dynamique
    now = datetime.now()
    ref_date = now.strftime("%Y-%m-%d")
    
    # 3. Appel JSON Mode
    try:
        messages = [
            ("system", DATE_SYSTEM_PROMPT.format(date_ref=ref_date)),
            ("user", expression)
        ]
        ai_msg = llm_date.invoke(messages)
        content = ai_msg.content
        
        # Nettoyage Markdown éventuel
        if "```" in content:
            content = content.replace("```json", "").replace("```", "").strip()
            
        return content # Retourne le JSON string (ex: '{"date": "2026-01-20"}')
        
    except Exception as e:
        return f"Erreur calcul date: {e}"