# 🗼 Puls-Events : Assistant de Recommandation d'Événements (POC)

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-Agents-1C3C3C?logo=langchain&logoColor=white) ![Mistral AI](https://img.shields.io/badge/Mistral_AI-mistral--large-FF7000?logo=mistral&logoColor=white) ![Faiss](https://img.shields.io/badge/Faiss-CPU-4285F4?logo=meta&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-Demo-FF4B4B?logo=streamlit&logoColor=white) ![Poetry](https://img.shields.io/badge/Poetry-géré-60A5FA?logo=poetry&logoColor=white) [![Rapport Technique](https://img.shields.io/badge/Rapport-Technique-orange?logo=readthedocs&logoColor=white)](docs/doc_technique.md)

Ce projet est un Proof of Concept (POC) d'un chatbot intelligent pour la recommandation d'événements culturels à Paris, basé sur une architecture RAG (Retrieval-Augmented Generation) "Agentique".

## 🎯 Objectifs

L'objectif est de créer un agent conversationnel capable de :
- Comprendre les demandes en langage naturel (ex: "un concert gratuit ce week-end").
- Interroger une base de données vectorielle (Faiss) contenant des milliers d'événements parisiens.
- Fournir des réponses pertinentes, précises et contextuelles en utilisant les modèles de Mistral AI.

## 📚 Documentation Technique

Pour comprendre les choix d'architecture, le fonctionnement de l'agent et les limites du système, consultez le rapport technique complet :

📄 **[Lire le Rapport Technique](docs/doc_technique.md)**

## 🛠️ Stack Technique

- **Langage :** Python 3.13
- **Gestionnaire de dépendances :** Poetry
- **Source de données :** API OpenData de la Mairie de Paris ("Que Faire à Paris")
- **Base Vectorielle :** Faiss (CPU)
- **Modèles IA :**
  - **Embedding :** `mistral-embed` (via API Mistral)
  - **Génération :** `mistral-large-latest` (via API Mistral)
- **Orchestration :** LangChain (Agents & Tools)
- **Interface de Démo :** Streamlit

## 🚀 Installation et Lancement

**Prérequis :**
- Python 3.13 installé
- Poetry installé
- Une clé API Mistral AI

**Étapes :**

1.  **Cloner le dépôt :**
    ```bash
    git clone https://github.com/abguven/puls-events-rag-poc.git
    cd puls-events-rag-poc
    ```

2.  **Installer les dépendances :**
    ```bash
    poetry install
    ```

3.  **Configurer la clé API :**
    - Créez un fichier `.env` à la racine du projet.
    - Ajoutez-y votre clé : `MISTRAL_API_KEY="votre_cle_ici"`

4.  **(Optionnel) Reconstruire la base de données :**
    Le projet contient un pipeline automatisé pour tout régénérer.
    ```bash
    poetry run python run_pipeline.py
    ```

5.  **Lancer l'application de démo :**
    ```bash
    poetry run streamlit run src/app.py
    ```

## 📁 Structure du Projet

-   `src/` : Code source de l'application.
    -   `app.py`: Interface Streamlit.
    -   `rag_chain.py`: Cœur de l'Agent RAG.
    -   `tools/`: Outils spécialisés (Date resolver).
-   `data/`: Données (ignorées par git, générées par le pipeline).
-   `docs/`: Documentation et Rapport Technique.
-   `tests/`: Tests unitaires de qualité et d'intégrité.
