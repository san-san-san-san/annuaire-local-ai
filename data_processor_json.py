import json
import pandas as pd
import meilisearch
from slugify import slugify
from config import *
import random
import math

class DataProcessor:
    """Processeur de données basé sur le fichier JSON des communes françaises"""

    def __init__(self):
        self.client = meilisearch.Client(MEILISEARCH_URL, MEILISEARCH_KEY)
        self.df = None
        self.raw_data = None

    def load_json(self):
        """Charge le fichier JSON des communes françaises"""
        print("Chargement du fichier JSON des communes...")

        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.raw_data = data

        # Filtrer pour les départements du Sud-Est
        filtered_communes = []
        for commune in data['data']:
            if commune['dep_code'] in DEPARTMENTS:
                filtered_communes.append(commune)

        print(f"Loaded {len(filtered_communes)} communes from Sud-Est departments")
        return filtered_communes

    def prepare_communes_data(self, communes_data):
        """Prépare les données de communes avec assignation de catégories"""
        print("Préparation des données de communes...")

        prepared_communes = []

        for commune in communes_data:
            # Assigner une catégorie aléatoire à chaque commune
            category = random.choice(list(CATEGORIES.keys()))

            commune_data = {
                'id': commune['code_insee'],
                'code_insee': commune['code_insee'],
                'nom_commune': commune['nom_standard'],
                'code_postal': commune['code_postal'],
                'department': commune['dep_code'],
                'dep_nom': commune['dep_nom'],
                'region': commune['reg_nom'],
                'population': commune.get('population', 0),
                'lat': commune.get('latitude_centre', commune.get('latitude_mairie', 0)),
                'lon': commune.get('longitude_centre', commune.get('longitude_mairie', 0)),
                'category': category,
                'superficie_km2': commune.get('superficie_km2', 0),
                'superficie_hectare': commune.get('superficie_hectare', 0),
                'densite': commune.get('densite', 0),
                'altitude_moyenne': commune.get('altitude_moyenne', 0),
                'grille_densite': commune.get('grille_densite', 0),
                'grille_densite_texte': commune.get('grille_densite_texte', ''),
                'unite_urbaine': commune.get('nom_unite_urbaine', 'Hors unité urbaine'),
                'type_commune_unite_urbaine': commune.get('type_commune_unite_urbaine', ''),
                'niveau_equipements_services': commune.get('niveau_equipements_services', 0),
                'niveau_equipements_services_texte': commune.get('niveau_equipements_services_texte', ''),
                'gentile': commune.get('gentile', ''),
                'url_wikipedia': commune.get('url_wikipedia', ''),
                'url_villedereve': commune.get('url_villedereve', '')
            }

            prepared_communes.append(commune_data)

        print(f"Prepared {len(prepared_communes)} communes")
        return prepared_communes

    def process_addresses(self):
        """Traite et enrichit les données de communes"""
        communes_data = self.load_json()
        prepared_data = self.prepare_communes_data(communes_data)

        # Convertir en DataFrame
        self.df = pd.DataFrame(prepared_data)

        # Création d'identifiants et slugs
        self.df['commune_slug'] = self.df['nom_commune'].apply(slugify)
        self.df['city_slug'] = self.df['nom_commune'].apply(slugify)  # Alias pour compatibilité

        # Préparation pour affichage
        self.df['display_name'] = self.df.apply(
            lambda row: f"{row['nom_commune']} ({row['code_postal']})",
            axis=1
        )

        print(f"Processed {len(self.df)} communes")
        return self.df

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

    def get_nearby_communes(self, lat, lon, category, current_commune_id, radius_km=50, limit=5):
        """Trouve les communes proches pour le maillage interne"""
        if self.df is None or pd.isna(lat) or pd.isna(lon):
            return []

        # Filtrer par catégorie et exclure la commune actuelle
        category_df = self.df[
            (self.df['category'] == category) &
            (self.df['id'] != current_commune_id)
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

    def get_commune_by_slug(self, commune_slug):
        """Récupère une commune par son slug"""
        if self.df is None:
            return None

        commune_row = self.df[self.df['commune_slug'] == commune_slug]
        if commune_row.empty:
            return None

        return commune_row.iloc[0].to_dict()

    # Alias pour compatibilité
    def get_address_by_slug(self, address_slug):
        return self.get_commune_by_slug(address_slug)

    def get_sitemap_data(self):
        """Génère les données pour le plan de site organisé par département"""
        if self.df is None:
            return {}

        sitemap_data = {}

        for category in CATEGORIES.keys():
            category_df = self.df[self.df['category'] == category]
            cities_data = []

            for city in category_df['nom_commune'].unique():
                city_commune = category_df[category_df['nom_commune'] == city].iloc[0]
                cities_data.append({
                    'name': city,
                    'slug': city_commune['city_slug'],
                    'count': 1,  # Une commune = un résultat
                    'department': city_commune['department'],
                    'dep_nom': city_commune['dep_nom']
                })

            # Trier par nom
            cities_data.sort(key=lambda x: x['name'])
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
            'total_addresses': len(self.df),  # Maintenant = total communes
            'cities_count': len(self.df['nom_commune'].unique()),
            'departments_count': len(self.df['department'].unique())
        }

    def get_cities_by_category(self, category):
        """Récupère les villes pour une catégorie donnée"""
        if self.df is None:
            return []

        cities_data = []
        category_df = self.df[self.df['category'] == category]

        for city in category_df['nom_commune'].unique():
            city_commune = category_df[category_df['nom_commune'] == city].iloc[0]
            cities_data.append({
                'name': city,
                'slug': city_commune['city_slug'],
                'count': 1,  # Une commune
                'department': city_commune['department']
            })

        return sorted(cities_data, key=lambda x: x['name'])

    def get_addresses_by_city_and_category(self, city, category):
        """Récupère les adresses pour une ville et catégorie données"""
        if self.df is None:
            return []

        addresses = self.df[
            (self.df['nom_commune'] == city) &
            (self.df['category'] == category)
        ]
        return addresses.to_dict('records')

    def search_addresses(self, query, category=None, city=None, limit=20):
        """Recherche simple via pandas (fallback)"""
        if self.df is None:
            return []

        search_df = self.df.copy()

        # Filtrer par catégorie si spécifiée
        if category:
            search_df = search_df[search_df['category'] == category]

        # Filtrer par ville si spécifiée
        if city:
            search_df = search_df[search_df['nom_commune'] == city]

        # Recherche textuelle simple
        if query:
            mask = (
                search_df['nom_commune'].str.contains(query, case=False, na=False) |
                search_df['code_postal'].str.contains(query, case=False, na=False) |
                search_df['dep_nom'].str.contains(query, case=False, na=False)
            )
            search_df = search_df[mask]

        return search_df.head(limit).to_dict('records')

    def index_to_meilisearch(self):
        """Indexe les données dans Meilisearch"""
        if self.df is None:
            return False

        print("Indexation dans Meilisearch...")

        try:
            # Création de l'index
            index = self.client.index('communes')

            # Préparation des documents
            documents = []
            for _, row in self.df.iterrows():
                doc = {
                    'id': row['id'],
                    'code_insee': row['code_insee'],
                    'nom_commune': row['nom_commune'],
                    'code_postal': row['code_postal'],
                    'category': row['category'],
                    'commune_slug': row['commune_slug'],
                    'city_slug': row['city_slug'],
                    'display_name': row['display_name'],
                    'department': row['department'],
                    'dep_nom': row['dep_nom'],
                    'region': row['region'],
                    'lat': row['lat'] if pd.notna(row['lat']) else 0,
                    'lon': row['lon'] if pd.notna(row['lon']) else 0,
                    'population': row.get('population', 0),
                    'superficie_km2': row.get('superficie_km2', 0),
                    'altitude_moyenne': row.get('altitude_moyenne', 0)
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
                'nom_commune', 'code_postal', 'display_name', 'dep_nom'
            ])

            index.update_filterable_attributes([
                'category', 'nom_commune', 'code_postal', 'city_slug', 'department'
            ])

            print("Indexation Meilisearch terminée!")
            return True

        except Exception as e:
            print(f"Erreur Meilisearch: {e}")
            return False