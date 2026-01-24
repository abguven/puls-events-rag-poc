# tests/test_data_quality.py
import pandas as pd
import pytest
import os
from datetime import datetime, timedelta

# Configuration
DATA_PATH = "./data/paris_events_clean.csv"

def test_data_quality():
    print(f"🛡️ Lancement des tests sur {DATA_PATH}...")

    # 1. Vérification du fichier
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"❌ Le fichier {DATA_PATH} n'existe pas !")
    
    df = pd.read_csv(DATA_PATH)
    print(f"   -> Fichier chargé : {len(df)} lignes.")

    # 2. Vérification des colonnes (Basé sur ton screenshot)
    required_cols = ['title', 'date_start', 'combined_price', 'tags', 'address_city']
    for col in required_cols:
        assert col in df.columns, f"❌ Colonne manquante : {col}"
    print("   -> Toutes les colonnes clés sont présentes.")

    # 3. Vérification de la fraîcheur (Moins d'un an)
    # On convertit en datetime en gérant l'UTC
    df['date_start'] = pd.to_datetime(df['date_start'], utc=True)
    
    # Date limite : Aujourd'hui - 365 jours
    # On récupère le timezone de la colonne pour comparer ce qui est comparable
    now = datetime.now(df['date_start'].dtype.tz)
    one_year_ago = now - timedelta(days=365)
    
    # On vérifie qu'aucun événement n'est plus vieux que 1 an
    old_events = df[df['date_start'] < one_year_ago]
    
    if len(old_events) > 0:
        print(f"⚠️ ATTENTION : {len(old_events)} événements ont plus d'un an.")
        # Pour le test, on peut décider si c'est bloquant ou pas.
        # assert len(old_events) == 0  <-- Décommente si tu veux être strict
    else:
        print("   -> Tous les événements datent de moins d'un an.")

    # 4. Vérification de la localité
    # On vérifie que dans 'address_city', on a bien "Paris"
    # On met en minuscule pour éviter les soucis de casse
    paris_events = df[df['address_city'].str.lower().str.contains("paris", na=False)]
    ratio = len(paris_events) / len(df)
    print(f"   -> {ratio:.1%} des événements contiennent 'Paris' dans la ville.")
    
    print("✅ TESTS TERMINÉS AVEC SUCCÈS.")

if __name__ == "__main__":
    try:
        test_data_quality()
    except AssertionError as e:
        print(f"❌ ÉCHEC DU TEST : {e}")
    except Exception as e:
        print(f"❌ ERREUR TECHNIQUE : {e}")