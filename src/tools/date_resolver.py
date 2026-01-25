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

OBJECTIF : Convertir l'expression en JSON au format YYYY-MM-DD.

RÈGLES DE LOGIQUE TEMPORELLE :
1.  **ANNÉE** :
    - Par défaut, utilise l'année de la DATE DE RÉFÉRENCE.
    - Ajoute +1 an UNIQUEMENT si le mois/jour demandé est strictement ANTERIEUR à la date de référence.

2.  **WEEK-END** :
    - Si on est Lundi, Mardi, Mercredi, Jeudi -> "ce week-end" = Samedi/Dimanche à venir.
    - Si on est Vendredi, Samedi, Dimanche -> "ce week-end" = Période restante jusqu'à Dimanche soir inclus.

3.  **SINGLETON vs PÉRIODE** :
    - "fin [mois]", "demain", "le 12" → {{"date": "..."}}.
    - "en [mois]", "semaine prochaine" → {{"debut": "...", "fin": "..."}}.

FORMAT DE SORTIE (JSON PUR) :
- Cas date unique : {{"date": "YYYY-MM-DD"}}
- Cas période : {{"debut": "YYYY-MM-DD", "fin": "YYYY-MM-DD"}}

---
EXEMPLES DE LOGIQUE (Avec une date de référence fictive au 20 Mai 2024) :

Exemple 1 (Dans le futur proche, même année) :
Entrée : "Le 14 juillet"
Réponse : {{"date": "2024-07-14"}}
(Raisonnement : Juillet est après Mai, donc on reste en 2024)

Exemple 2 (Date passée, année suivante) :
Entrée : "Le 1er janvier"
Réponse : {{"date": "2025-01-01"}}
(Raisonnement : Janvier est avant Mai, donc c'est pour l'année d'après)

Exemple 3 (Relatif) :
Entrée : "vendredi prochain"
Réponse : {{"date": "2024-05-24"}}
---
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