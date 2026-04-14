import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


import streamlit as st
from src.rag_chain import RAGAgent
from src.config import ENABLE_MEMORY, LLM_MODEL_NAME


WELCOME_MESSAGE = {
    "role": "assistant",
    "content": "Bonjour ! Je suis votre assistant sorties à Paris. Que souhaitez-vous faire ?",
}

# Configuration de la page
st.set_page_config(page_title="Puls-Events AI", page_icon="src/assets/events_64.png", layout="wide")

# Titre et Header
col_icon, col_title = st.columns([0.05, 0.95])
with col_icon:
    st.image("src/assets/events_64.png", width=64)
with col_title:
    st.title("Puls-Events : Votre Guide Sorties Paris")
st.markdown(f"**Modèle actif :** `{LLM_MODEL_NAME}` | **Mémoire :** `{'ON' if ENABLE_MEMORY else 'OFF'}`")

# --- SIDEBAR ---
with st.sidebar:
    # st.image("src/assets/events_64.png", width=48)
    st.markdown("### Puls-Events")
    st.caption("Assistant RAG conversationnel pour les événements parisiens.")
    st.markdown(f"**Stack :** Mistral AI · FAISS · LangChain")

    st.markdown("---")
    st.markdown("""
    **Ce que je sais faire :**
    - :material/my_location: Filtrage géographique
    - :material/calendar_check: Raisonnement temporel
    - :material/savings: Contraintes budget
    - :material/cognition: Recherche sémantique
    - :material/arrow_split: Requêtes multi-critères
    """)
    st.markdown("---")

    if st.button("Nouvelle Conversation", type="secondary", icon=":material/refresh:", use_container_width=True):
        st.session_state.messages = [WELCOME_MESSAGE]
        st.rerun()


# --- INITIALISATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [WELCOME_MESSAGE]

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
AVATARS = {"user": "src/assets/user_64.png", "assistant": "src/assets/robot_64.png"}

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=AVATARS[message["role"]]):
        st.markdown(message["content"])

# --- INTERACTION ---
if prompt := st.chat_input("Que voulez-vous faire à Paris ?"):
    
    # 1. Affiche le message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=AVATARS["user"]):
        st.markdown(prompt)

    # 2. Génération de la réponse
    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
        with st.spinner("Exploration de la base d'événements..."):
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

                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"Erreur lors de la génération : {e}")

    # Rerun propre : la boucle history en haut affiche le message, sans double rendu
    st.rerun()