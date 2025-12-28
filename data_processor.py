import pandas as pd
import meilisearch
from slugify import slugify
from config import *
import random
import math

class DataProcessor:
    def __init__(self):
        self.client = meilisearch.Client(MEILISEARCH_URL, MEILISEARCH_KEY)
        self.df = None

    def load_csv(self):
        """Charge le fichier CSV des adresses"""
        print("Chargement du fichier CSV...")
        self.df = pd.read_csv(CSV_FILE, sep=';', low_memory=False)
        print(f"Loaded {len(self.df)} addresses")
        return self.df

    def process_addresses(self):
        """Traite et enrichit les données d'adresses"""
        if self.df is None:
            self.load_csv()

        # Nettoyage des données
        self.df = self.df.dropna(subset=['nom_commune', 'nom_voie', 'numero'])

        # Convertir les numéros en entier pour le tri
        self.df['numero'] = pd.to_numeric(self.df['numero'], errors='coerce')
        self.df = self.df.dropna(subset=['numero'])

        # Garder seulement une adresse par numéro/voie/ville (la première)
        self.df = self.df.drop_duplicates(subset=['numero', 'nom_voie', 'nom_commune'], keep='first')

        print(f"Après dédoublonnage: {len(self.df)} adresses uniques")

        # Ajout du département basé sur le code postal
        self.df['department'] = self.df['code_postal'].astype(str).str[:2]

        # Ajout des catégories (simulation d'assignation par adresse)
        categories_list = list(CATEGORIES.keys())
        self.df['category'] = [random.choice(categories_list) for _ in range(len(self.df))]

        # Création d'identifiants et slugs
        self.df['address_slug'] = self.df.apply(
            lambda row: slugify(f"{int(row['numero'])}-{row['nom_voie']}-{row['nom_commune']}"),
            axis=1
        )
        self.df['city_slug'] = self.df['nom_commune'].apply(slugify)

        # Préparation pour Meilisearch
        self.df['full_address'] = self.df.apply(
            lambda row: f"{int(row['numero'])} {row['nom_voie']}, {row['code_postal']} {row['nom_commune']}",
            axis=1
        )

        return self.df

    def index_to_meilisearch(self):
        """Indexe les données dans Meilisearch"""
        if self.df is None:
            self.process_addresses()

        print("Indexation dans Meilisearch...")

        # Création de l'index
        index = self.client.index('addresses')

        # Préparation des documents
        documents = []
        for _, row in self.df.iterrows():
            doc = {
                'id': row['id'],
                'numero': str(row['numero']) if pd.notna(row['numero']) else '',
                'nom_voie': row['nom_voie'],
                'code_postal': row['code_postal'],
                'nom_commune': row['nom_commune'],
                'category': row['category'],
                'address_slug': row['address_slug'],
                'city_slug': row['city_slug'],
                'full_address': row['full_address'],
                'department': row['department'],
                'lat': row['lat'] if pd.notna(row['lat']) else 0,
                'lon': row['lon'] if pd.notna(row['lon']) else 0
            }
            documents.append(doc)

        # Indexation par batch de 1000
        batch_size = 1000
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            index.add_documents(batch)
            print(f"Indexed batch {i//batch_size + 1}/{(len(documents)//batch_size) + 1}")

        # Configuration des attributs de recherche
        index.update_searchable_attributes([
            'nom_voie', 'nom_commune', 'full_address', 'numero'
        ])

        index.update_filterable_attributes([
            'category', 'nom_commune', 'code_postal', 'city_slug'
        ])

        print("Indexation terminée!")
        return True

    def get_cities_by_category(self, category):
        """Récupère les villes pour une catégorie donnée"""
        if self.df is None:
            self.process_addresses()

        cities = self.df[self.df['category'] == category]['nom_commune'].unique()
        return sorted(cities)

    def get_addresses_by_city_and_category(self, city, category):
        """Récupère les adresses pour une ville et catégorie données"""
        if self.df is None:
            self.process_addresses()

        addresses = self.df[
            (self.df['nom_commune'] == city) &
            (self.df['category'] == category)
        ]
        return addresses.to_dict('records')

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calcule la distance entre deux points en km"""
        if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
            return float('inf')

        R = 6371  # Rayon de la Terre en km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    def get_nearby_addresses(self, lat, lon, category, current_address_id, radius_km=20, limit=5):
        """Trouve les adresses proches pour le maillage interne"""
        if self.df is None or pd.isna(lat) or pd.isna(lon):
            return []

        # Filtrer par catégorie et exclure l'adresse actuelle
        category_df = self.df[
            (self.df['category'] == category) &
            (self.df['id'] != current_address_id)
        ].copy()

        # Calculer les distances
        category_df['distance'] = category_df.apply(
            lambda row: self.calculate_distance(lat, lon, row['lat'], row['lon']),
            axis=1
        )

        # Filtrer par rayon et trier par distance
        nearby = category_df[
            category_df['distance'] <= radius_km
        ].sort_values('distance').head(limit)

        return nearby.to_dict('records')

    def get_sitemap_data(self):
        """Génère les données pour le plan de site organisé par département"""
        if self.df is None:
            return {}

        sitemap_data = {}

        for category in CATEGORIES.keys():
            category_df = self.df[self.df['category'] == category]
            cities_data = []

            for city in category_df['nom_commune'].unique():
                city_addresses = category_df[category_df['nom_commune'] == city]
                cities_data.append({
                    'name': city,
                    'slug': city_addresses['city_slug'].iloc[0],
                    'count': len(city_addresses),
                    'department': city_addresses['department'].iloc[0]
                })

            # Trier par nombre d'adresses (décroissant) puis par nom
            cities_data.sort(key=lambda x: (-x['count'], x['name']))
            sitemap_data[category] = cities_data

        return sitemap_data

    def get_stats(self):
        """Retourne les statistiques du site"""
        if self.df is None:
            return {
                'total_addresses': 0,
                'cities_count': 0,
                'departments_count': 0
            }

        return {
            'total_addresses': len(self.df),
            'cities_count': len(self.df['nom_commune'].unique()),
            'departments_count': len(self.df['department'].unique())
        }

    def get_address_by_slug(self, address_slug):
        """Récupère une adresse par son slug"""
        if self.df is None:
            return None

        address_row = self.df[self.df['address_slug'] == address_slug]
        if address_row.empty:
            return None

        return address_row.iloc[0].to_dict()

    def search_addresses(self, query, category=None, city=None, limit=20):
        """Recherche des adresses via Meilisearch"""
        index = self.client.index('addresses')

        filter_conditions = []
        if category:
            filter_conditions.append(f"category = '{category}'")
        if city:
            filter_conditions.append(f"nom_commune = '{city}'")

        filter_str = ' AND '.join(filter_conditions) if filter_conditions else None

        results = index.search(query, {
            'filter': filter_str,
            'limit': limit
        })

        return results['hits']