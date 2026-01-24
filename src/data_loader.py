import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from bs4 import BeautifulSoup

class ParisEventsExtractor:
    """
    Extrait les événements depuis OpenDataSoft Paris (Source: Que Faire à Paris).
    Nettoie le HTML et prépare les données pour le RAG.
    """
    
    def __init__(self, data_dir: str = "./data"):
        self.base_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records"
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        
    def _clean_html(self, text):
        """Retire le HTML et nettoie les espaces."""
        if not isinstance(text, str):
            return ""
        soup = BeautifulSoup(text, "html.parser")
        text = soup.get_text(separator=" ")
        return " ".join(text.split())

    def fetch_events(self, limit=100):
        params = {
            'limit': limit,
            'offset': 0,
            'order_by': 'date_start desc'
        }
        
        all_records = []
        print("🔄 Récupération des événements (API Mairie de Paris)...")
        
        while True:
            try:
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                records = data.get('results', [])
                if not records:
                    break
                
                all_records.extend(records)
                params['offset'] += limit
                
                if params['offset'] % 500 == 0:
                    print(f"   -> {len(all_records)} événements récupérés...")
                
                if len(all_records) >= 5000:
                    break
                    
            except Exception as e:
                print(f"❌ Erreur API: {e}")
                break
        
        print(f"✅ {len(all_records)} événements bruts récupérés.")
        
        # Sauvegarde brute
        df_raw = pd.DataFrame(all_records)
        raw_path = self.raw_dir / "paris_events_raw.csv"
        df_raw.to_csv(raw_path, index=False)
        print(f"💾 Raw Data sauvegardé : {raw_path}")
        
        return df_raw
    
    def clean_events(self, df: pd.DataFrame) -> pd.DataFrame:
        print("Début du nettoyage...")
        cleaned = pd.DataFrame()
        
        # Colonnes de base
        cleaned['id'] = df["id"]
        cleaned['title'] = df["title"]
        cleaned['date_start'] = pd.to_datetime(df["date_start"], errors='coerce', utc=True)
        cleaned['date_end'] = pd.to_datetime(df["date_end"], errors='coerce', utc=True)
        cleaned['address_zipcode'] = df["address_zipcode"].fillna('')
        
        # Nettoyage HTML
        print("   -> Suppression des balises HTML...")
        cleaned['description'] = df["description"].apply(self._clean_html)
        
        # Nettoyage des champs "prix"
        cleaned['price_detail'] = df["price_detail"].apply(self._clean_html)       
        cleaned['price_type'] = df["price_type"].fillna('inconnu')
        
        # Logique : Si on a un détail, on l'ajoute entre parenthèses après le type
        # Ex: "payant (15€)" ou juste "gratuit"
        mask = cleaned['price_detail'].notna() & cleaned['price_detail'].astype(str).str.strip().ne("")

        cleaned['combined_price'] = cleaned['price_type'].astype(str)
        cleaned.loc[mask, 'combined_price'] = (
                cleaned.loc[mask, 'price_type'].astype(str)
                + " ("
                + cleaned.loc[mask, 'price_detail'].astype(str)
                + ")"
        )             

        # Coordonnées
        if 'lat_lon' in df.columns:
            cleaned['latitude'] = df['lat_lon'].apply(lambda x: x.get('lat') if isinstance(x, dict) else None)
            cleaned['longitude'] = df['lat_lon'].apply(lambda x: x.get('lon') if isinstance(x, dict) else None)
        else:
            cleaned['latitude'] = None
            cleaned['longitude'] = None
        
        # Infos Contexte
        cleaned['address_name'] = df["address_name"].fillna('')
        cleaned['address_city'] = df["address_city"].fillna('')
        cleaned['address_street'] = df["address_street"].fillna('')
        cleaned['image_url'] = df.get('cover_url', '')
        
        # Gestion des Tags 
        if 'tags' in df.columns:
            cleaned['tags'] = df['tags'].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
        elif 'qfap_tags' in df.columns:
            cleaned['tags'] = df['qfap_tags'].astype(str)
        else:
            cleaned['tags'] = ""

        # Filtre Temporel (< 1 an)
        if not cleaned['date_start'].isnull().all():
            one_year_ago = datetime.now(cleaned['date_start'].dtype.tz) - timedelta(days=365)
            initial_count = len(cleaned)
            cleaned = cleaned[cleaned['date_start'] >= one_year_ago]
            print(f"   -> Filtre Date : {initial_count - len(cleaned)} événements trop vieux supprimés.")

        # Nettoyage final       
        cleaned = cleaned.dropna(subset=['title','id','description'])
        cleaned = cleaned[cleaned[['title','description']].apply(lambda col: col.str.strip() != "").all(axis=1)]
                
        print(f"✅ Nettoyage terminé. {len(cleaned)} événements prêts.")
        return cleaned

def main():
    extractor = ParisEventsExtractor()
    df_raw = extractor.fetch_events()
    
    if not df_raw.empty:
        df_clean = extractor.clean_events(df_raw)
        output_path = extractor.raw_dir / "paris_events_clean.csv"
        df_clean.to_csv(output_path, index=False)

        print(f"FICHIER FINAL : {output_path}")
        print("\nAperçu des prix combinés :")
        print(df_clean[['price_type', 'combined_price']].head())

if __name__ == "__main__":
    main()