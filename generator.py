import os
import json
from jinja2 import Environment, FileSystemLoader
from slugify import slugify
from data_processor_json import DataProcessor
from content_generator import ContentGenerator
from config import *

class PageGenerator:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.content_generator = ContentGenerator()
        self.env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

        # Créer le dossier de sortie
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def generate_home_page(self):
        """Génère la page d'accueil"""
        print("Génération de la page d'accueil...")

        # Statistiques
        stats = self.data_processor.get_stats()

        template = self.env.get_template('home.html')
        html = template.render(
            categories=CATEGORIES,
            stats=stats
        )

        with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html)

    def generate_category_pages(self):
        """Génère les pages de catégories avec départements"""
        print("Génération des pages de catégories...")

        df = self.data_processor.df
        if df is None:
            return

        departments_template = self.env.get_template('departments.html')

        for category_slug, category_name in CATEGORIES.items():
            print(f"  - Génération page {category_name}...")

            # Obtenir les départements pour cette catégorie
            category_df = df[df['category'] == category_slug]
            departments_data = []

            for dept_code in category_df['department'].unique():
                dept_communes = category_df[category_df['department'] == dept_code]
                dept_name = DEPARTMENTS.get(dept_code, f"Département {dept_code}")

                departments_data.append({
                    'code': dept_code,
                    'name': dept_name,
                    'cities_count': len(dept_communes['nom_commune'].unique()),
                    'total_population': dept_communes['population'].sum()
                })

            # Trier par nom de département
            departments_data.sort(key=lambda x: x['name'])

            html = departments_template.render(
                categories=CATEGORIES,
                category_name=category_name,
                category_slug=category_slug,
                departments=departments_data
            )

            # Créer le dossier de catégorie
            category_dir = os.path.join(OUTPUT_DIR, 'category', category_slug)
            os.makedirs(category_dir, exist_ok=True)

            with open(os.path.join(category_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(html)

    def generate_department_pages(self):
        """Génère les pages des départements par catégorie"""
        print("Génération des pages de départements...")

        df = self.data_processor.df
        if df is None:
            return

        template = self.env.get_template('department_cities.html')

        for category_slug, category_name in CATEGORIES.items():
            print(f"  - Génération pages départements pour {category_name}...")

            category_df = df[df['category'] == category_slug]

            for dept_code in category_df['department'].unique():
                dept_name = DEPARTMENTS.get(dept_code, f"Département {dept_code}")

                # Obtenir les villes pour ce département et cette catégorie
                dept_category_df = df[
                    (df['category'] == category_slug) &
                    (df['department'] == dept_code)
                ]
                cities_data = []

                for city in dept_category_df['nom_commune'].unique():
                    city_commune = dept_category_df[dept_category_df['nom_commune'] == city].iloc[0]
                    cities_data.append({
                        'name': city,
                        'slug': slugify(city),
                        'population': city_commune.get('population', 0),
                        'postal_code': city_commune.get('code_postal', '')
                    })

                # Trier par nom de ville
                cities_data.sort(key=lambda x: x['name'])

                html = template.render(
                    categories=CATEGORIES,
                    category_name=category_name,
                    category_slug=category_slug,
                    department_name=dept_name,
                    department_code=dept_code,
                    cities=cities_data
                )

                # Créer le dossier du département
                dept_dir = os.path.join(OUTPUT_DIR, 'category', category_slug, 'department', dept_code)
                os.makedirs(dept_dir, exist_ok=True)

                with open(os.path.join(dept_dir, 'index.html'), 'w', encoding='utf-8') as f:
                    f.write(html)

    def generate_city_pages(self, limit_cities=None):
        """Génère les pages de villes par catégorie"""
        print("Génération des pages de villes...")

        df = self.data_processor.df
        if df is None:
            return

        template = self.env.get_template('city.html')
        generated_count = 0

        for category_slug, category_name in CATEGORIES.items():
            print(f"  - Génération pages villes pour {category_name}...")

            category_df = df[df['category'] == category_slug]
            cities = category_df['nom_commune'].unique()

            if limit_cities:
                cities = cities[:limit_cities]

            for city in cities:
                city_slug = slugify(city)
                city_addresses = category_df[category_df['nom_commune'] == city]

                # Limiter à 50 adresses par page
                addresses_data = city_addresses.head(50).to_dict('records')

                html = template.render(
                    categories=CATEGORIES,
                    category_name=category_name,
                    category_slug=category_slug,
                    city_name=city,
                    city_slug=city_slug,
                    addresses=addresses_data
                )

                # Créer le dossier de la ville
                city_dir = os.path.join(OUTPUT_DIR, 'category', category_slug, city_slug)
                os.makedirs(city_dir, exist_ok=True)

                with open(os.path.join(city_dir, 'index.html'), 'w', encoding='utf-8') as f:
                    f.write(html)

                generated_count += 1

                if limit_cities and generated_count >= limit_cities * len(CATEGORIES):
                    break

        print(f"  - {generated_count} pages de villes générées")

    def generate_address_pages(self, limit_addresses=None):
        """Génère les pages détaillées des adresses"""
        print("Génération des pages d'adresses détaillées...")

        df = self.data_processor.df
        if df is None:
            return

        template = self.env.get_template('address_detail.html')
        generated_count = 0
        total_addresses = len(df)

        if limit_addresses:
            df = df.head(limit_addresses)

        for _, address in df.iterrows():
            address_data = address.to_dict()
            category_slug = address_data['category']
            category_name = CATEGORIES[category_slug]

            # Générer le contenu spinné
            content = self.content_generator.generate_content(address_data)

            # Obtenir les communes proches pour le maillage interne
            nearby_addresses = []
            if address_data.get('lat') and address_data.get('lon'):
                nearby_addresses = self.data_processor.get_nearby_communes(
                    lat=address_data['lat'],
                    lon=address_data['lon'],
                    category=category_slug,
                    current_commune_id=address_data['id'],
                    radius_km=20,
                    limit=5
                )

            html = template.render(
                categories=CATEGORIES,
                category_name=category_name,
                category_slug=category_slug,
                address=address_data,
                content=content,
                nearby_addresses=nearby_addresses
            )

            # Créer le dossier de l'adresse
            address_dir = os.path.join(OUTPUT_DIR, 'address', category_slug)
            os.makedirs(address_dir, exist_ok=True)

            # Sauvegarder la page
            filename = f"{address_data['commune_slug']}.html"
            with open(os.path.join(address_dir, filename), 'w', encoding='utf-8') as f:
                f.write(html)

            generated_count += 1

            if generated_count % 100 == 0:
                print(f"  - {generated_count}/{len(df)} pages d'adresses générées")

        print(f"  - {generated_count} pages d'adresses générées au total")

    def generate_sitemap_page(self):
        """Génère la page plan de site"""
        print("Génération de la page plan de site...")

        sitemap_data = self.data_processor.get_sitemap_data()
        stats = self.data_processor.get_stats()

        template = self.env.get_template('sitemap.html')
        html = template.render(
            categories=CATEGORIES,
            departments=DEPARTMENTS,
            sitemap_data=sitemap_data,
            stats=stats
        )

        with open(os.path.join(OUTPUT_DIR, 'sitemap.html'), 'w', encoding='utf-8') as f:
            f.write(html)

    def generate_sample_pages(self):
        """Génère un échantillon de pages pour test"""
        print("Génération d'un échantillon de pages...")

        # Charger et traiter les données
        self.data_processor.process_addresses()

        # Page d'accueil
        self.generate_home_page()

        # Pages de catégories (avec départements)
        self.generate_category_pages()

        # Pages de départements par catégorie
        self.generate_department_pages()

        # Quelques pages de villes (20 villes par catégorie max)
        self.generate_city_pages(limit_cities=20)

        # Quelques pages d'adresses détaillées (200 max pour test)
        self.generate_address_pages(limit_addresses=200)

        # Plan de site
        self.generate_sitemap_page()

        print("Génération terminée!")

    def generate_all_pages(self):
        """Génère toutes les pages"""
        print("Génération complète de toutes les pages...")

        # Charger et traiter les données
        self.data_processor.process_addresses()

        # Page d'accueil
        self.generate_home_page()

        # Pages de catégories (avec départements)
        self.generate_category_pages()

        # Pages de départements par catégorie
        self.generate_department_pages()

        # Toutes les pages de villes
        self.generate_city_pages()

        # Toutes les pages d'adresses détaillées
        self.generate_address_pages()

        # Plan de site
        self.generate_sitemap_page()

        print("Génération complète terminée!")

if __name__ == "__main__":
    generator = PageGenerator()
    generator.generate_sample_pages()