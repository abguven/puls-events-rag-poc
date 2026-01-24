import subprocess
import sys

def run_command(command, check=True):
    """Exécute une commande et gère les erreurs."""
    label = ' '.join(command)
    print(f"\n--- Lancement : '{label}' ---")
    
    # Utilisation de sys.executable pour pointer vers le python du venv
    process = subprocess.run([sys.executable, *command], capture_output=True, text=True, check=False)
    
    if check and process.returncode != 0:
        print(f"❌ ERREUR LORS DE '{label}'")
        print("--- STDOUT ---")
        print(process.stdout)
        print("--- STDERR ---")
        print(process.stderr)
        sys.exit(1) # Arrêt total du pipeline
    else:
        print(f"✅ Succès pour '{label}'")
        # On affiche la sortie que si c'est pertinent (pas pour les tests pytest qui sont verbeux)
        if "-m" not in command:
             print(process.stdout)
    return True

def main():
    print("*** DÉMARRAGE DU PIPELINE COMPLET PULS-EVENTS ***")

    # --- PHASE 1 : VALIDATION DE L'ENVIRONNEMENT ---
    print("\n[PHASE 1/3] Vérification de l'environnement...")
    run_command(["tests/test_setup.py"])
    
    # --- PHASE 2 : GÉNÉRATION ET TEST DES DONNÉES ---
    print("\n[PHASE 2/3] Traitement des données...")
    # 2a. Lancer l'ETL
    run_command(["src/data_loader.py"])
    # 2b. Lancer les tests de qualité sur le CSV généré
    run_command(["-m", "pytest", "tests/test_data_quality.py"])

    # --- PHASE 3 : CRÉATION ET TEST DE L'INDEX VECTORIEL ---
    print("\n[PHASE 3/3] Vectorisation et validation de l'index...")
    # 3a. Lancer la vectorisation
    run_command(["src/vectorizer.py"])
    # 3b. Lancer le test de l'index Faiss
    run_command(["tests/test_faiss.py"])

    print("\n✅ PIPELINE TERMINÉ AVEC SUCCÈS !")
    print("L'application est prête à être lancée.")
    print("👉 poetry run streamlit run src/app.py")

if __name__ == "__main__":
    main()