import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


import streamlit as st
from src.rag_chain import RAGAgent
from src.config import ENABLE_MEMORY, LLM_MODEL_NAME


# Configuration de la page
st.set_page_config(page_title="Puls-Events AI", page_icon="🎉", layout="wide")

# Titre et Header
st.title("🎉 Puls-Events : Assistant Sorties Paris")
st.markdown(f"**Modèle actif :** `{LLM_MODEL_NAME}` | **Mémoire :** `{'ON' if ENABLE_MEMORY else 'OFF'}`")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Paramètres")
    
    # Bouton Reset (Indispensable pour la démo)
    if st.button("🗑️ Nouvelle Conversation", type="primary"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    **Guide Démo :**
    1. Demandez "Ce week-end"
    2. Testez "Gratuit ce soir"
    3. Testez "Jazz à Montmartre"
    """)

# --- INITIALISATION ---
# 1. Session State pour l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Chargement de l'Agent (Mise en cache pour ne pas recharger FAISS à chaque clic)
@st.cache_resource
def load_agent():
    return RAGAgent()

try:
    agent = load_agent()
except Exception as e:
    st.error(f"Erreur critique au chargement de l'agent : {e}")
    st.stop()

# --- AFFICHAGE CHAT ---
# On réaffiche tout l'historique à chaque rechargement de page
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- INTERACTION ---
if prompt := st.chat_input("Que voulez-vous faire à Paris ?"):
    
    # 1. Affiche le message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Génération de la réponse
    with st.chat_message("assistant"):
        with st.spinner("L'IA réfléchit... (Interrogation FAISS + Mistral)"):
            try:
                # GESTION MÉMOIRE (Selon config.py)
                if ENABLE_MEMORY:
                    # On passe l'historique complet (format simplifié pour notre agent custom)                    
                    history_text = ""
                    # On prend les 2 derniers échanges pour ne pas saturer le prompt
                    for msg in st.session_state.messages[-4:]: 
                        history_text += f"{msg['role'].upper()}: {msg['content']}\n"
                    
                    full_query = f"HISTORIQUE CONVERSATION:\n{history_text}\n\nNOUVELLE QUESTION: {prompt}"
                    response = agent.ask(full_query)
                else:
                    # Mode Amnésique : Juste la question brute
                    response = agent.ask(prompt)
                
                st.markdown(response)
                
                # Sauvegarde réponse
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Erreur lors de la génération : {e}")