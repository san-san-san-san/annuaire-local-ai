from flask import Flask, render_template, request, jsonify, Response, url_for
from data_processor_json import DataProcessor
from content_generator import ContentGenerator
from config import *
import os

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
data_processor = DataProcessor()
data_processor.process_addresses()  # Charger les données au démarrage
content_generator = ContentGenerator()

@app.route('/')
def home():
    """Page d'accueil"""
    # Statistiques
    df = data_processor.df
    stats = {
        'total_addresses': len(df) if df is not None else 0,
        'total_cities': len(df['nom_commune'].unique()) if df is not None else 0
    }

    return render_template('home.html',
                         categories=CATEGORIES,
                         stats=stats)

@app.route('/category/<category_slug>')
def category_page(category_slug):
    """Page de catégorie avec liste des départements"""
    if category_slug not in CATEGORIES:
        return "Catégorie non trouvée", 404

    category_name = CATEGORIES[category_slug]

    # Obtenir les départements pour cette catégorie
    df = data_processor.df
    if df is None:
        departments_data = []
    else:
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

    return render_template('departments.html',
                         categories=CATEGORIES,
                         category_name=category_name,
                         category_slug=category_slug,
                         departments=departments_data)

@app.route('/category/<category_slug>/department/<department_code>')
def department_cities_page(category_slug, department_code):
    """Page des villes d'un département pour une catégorie"""
    if category_slug not in CATEGORIES:
        return "Catégorie non trouvée", 404

    if department_code not in DEPARTMENTS:
        return "Département non trouvé", 404

    category_name = CATEGORIES[category_slug]
    department_name = DEPARTMENTS[department_code]

    # Obtenir les villes pour cette catégorie et ce département
    df = data_processor.df
    if df is None:
        cities_data = []
    else:
        dept_category_df = df[
            (df['category'] == category_slug) &
            (df['department'] == department_code)
        ]
        cities_data = []

        for city in dept_category_df['nom_commune'].unique():
            city_commune = dept_category_df[dept_category_df['nom_commune'] == city].iloc[0]
            cities_data.append({
                'name': city,
                'slug': city_commune['city_slug'],
                'population': city_commune.get('population', 0),
                'postal_code': city_commune.get('code_postal', '')
            })

        # Trier par nom de ville
        cities_data.sort(key=lambda x: x['name'])

    return render_template('department_cities.html',
                         categories=CATEGORIES,
                         category_name=category_name,
                         category_slug=category_slug,
                         department_name=department_name,
                         department_code=department_code,
                         cities=cities_data)

@app.route('/category/<category_slug>/<city_slug>')
def city_page(category_slug, city_slug):
    """Page de ville avec contenu riche et maillage interne"""
    if category_slug not in CATEGORIES:
        return "Catégorie non trouvée", 404

    category_name = CATEGORIES[category_slug]

    # Trouver la ville correspondante au slug
    df = data_processor.df
    if df is None:
        return "Données non disponibles", 500

    city_df = df[df['city_slug'] == city_slug]
    if city_df.empty:
        return "Ville non trouvée", 404

    # Obtenir les données de la commune pour cette catégorie
    commune_df = df[
        (df['city_slug'] == city_slug) &
        (df['category'] == category_slug)
    ]

    if commune_df.empty:
        return "Service non disponible dans cette ville", 404

    commune_data = commune_df.iloc[0].to_dict()
    city_name = commune_data['nom_commune']

    # Générer le contenu spinné
    content = content_generator.generate_content(commune_data)

    # Obtenir les communes proches pour le maillage interne
    nearby_communes = data_processor.get_nearby_communes(
        lat=commune_data.get('lat', 0),
        lon=commune_data.get('lon', 0),
        category=category_slug,
        current_commune_id=commune_data['id'],
        radius_km=30,
        limit=6
    )

    # Obtenir les autres services disponibles dans cette ville
    other_services = []
    for cat_slug, cat_name in CATEGORIES.items():
        if cat_slug != category_slug:
            other_services.append({
                'slug': cat_slug,
                'name': cat_name,
                'url': f'/category/{cat_slug}/{city_slug}'
            })

    # Obtenir d'autres villes du même département pour le maillage
    dept_code = commune_data.get('department', '')
    dept_name = DEPARTMENTS.get(dept_code, f"Département {dept_code}")
    same_dept_communes = df[
        (df['department'] == dept_code) &
        (df['category'] == category_slug) &
        (df['city_slug'] != city_slug)
    ].head(8).to_dict('records')

    return render_template('city.html',
                         categories=CATEGORIES,
                         category_name=category_name,
                         category_slug=category_slug,
                         city_name=city_name,
                         city_slug=city_slug,
                         commune=commune_data,
                         content=content,
                         nearby_communes=nearby_communes,
                         other_services=other_services,
                         same_dept_communes=same_dept_communes,
                         dept_code=dept_code,
                         dept_name=dept_name,
                         addresses=[commune_data])

@app.route('/sitemap')
def sitemap():
    """Page plan du site"""
    sitemap_data = data_processor.get_sitemap_data()
    stats = data_processor.get_stats()

    return render_template('sitemap.html',
                         categories=CATEGORIES,
                         departments=DEPARTMENTS,
                         sitemap_data=sitemap_data,
                         stats=stats)

@app.route('/search')
def search():
    """Page de recherche"""
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()

    results = []

    if query:
        # Recherche via Meilisearch
        try:
            results = data_processor.search_addresses(
                query=query,
                category=category if category else None,
                limit=20
            )
        except Exception as e:
            print(f"Erreur de recherche: {e}")
            # Fallback sur recherche pandas si Meilisearch n'est pas disponible
            df = data_processor.df
            if df is not None:
                search_df = df.copy()

                # Filtrer par catégorie si spécifiée
                if category:
                    search_df = search_df[search_df['category'] == category]

                # Recherche textuelle simple
                mask = (
                    search_df['nom_commune'].str.contains(query, case=False, na=False) |
                    search_df['nom_voie'].str.contains(query, case=False, na=False) |
                    search_df['full_address'].str.contains(query, case=False, na=False)
                )

                results = search_df[mask].head(20).to_dict('records')

    return render_template('search.html',
                         categories=CATEGORIES,
                         query=query,
                         selected_category=category,
                         results=results)

@app.route('/address/<category_slug>/<address_slug>')
def address_detail(category_slug, address_slug):
    """Page détaillée d'une adresse"""
    if category_slug not in CATEGORIES:
        return "Catégorie non trouvée", 404

    category_name = CATEGORIES[category_slug]

    # Récupérer la commune
    address = data_processor.get_commune_by_slug(address_slug)
    if not address:
        return "Commune non trouvée", 404

    # Générer le contenu spinné
    content = content_generator.generate_content(address)

    # Obtenir les communes proches pour le maillage interne
    nearby_addresses = []
    if address.get('lat') and address.get('lon'):
        nearby_addresses = data_processor.get_nearby_communes(
            lat=address['lat'],
            lon=address['lon'],
            category=category_slug,
            current_commune_id=address['id'],
            radius_km=20,
            limit=5
        )

    return render_template('address_detail.html',
                         categories=CATEGORIES,
                         category_name=category_name,
                         category_slug=category_slug,
                         address=address,
                         content=content,
                         nearby_addresses=nearby_addresses)

@app.route('/api/search')
def api_search():
    """API de recherche JSON"""
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    limit = int(request.args.get('limit', 10))

    if not query:
        return jsonify({'results': []})

    try:
        results = data_processor.search_addresses(
            query=query,
            category=category if category else None,
            limit=limit
        )
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sitemap.xml')
def sitemap_xml():
    """Génère le sitemap XML pour Google"""
    base_url = request.url_root.rstrip('/')

    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    # Page d'accueil
    xml_content += f'  <url>\n    <loc>{base_url}/</loc>\n    <priority>1.0</priority>\n  </url>\n'

    # Page recherche
    xml_content += f'  <url>\n    <loc>{base_url}/search</loc>\n    <priority>0.8</priority>\n  </url>\n'

    # Pages catégories
    for category_slug in CATEGORIES.keys():
        xml_content += f'  <url>\n    <loc>{base_url}/category/{category_slug}</loc>\n    <priority>0.9</priority>\n  </url>\n'

        # Pages départements par catégorie
        df = data_processor.df
        if df is not None:
            category_df = df[df['category'] == category_slug]
            for dept_code in category_df['department'].unique():
                xml_content += f'  <url>\n    <loc>{base_url}/category/{category_slug}/department/{dept_code}</loc>\n    <priority>0.8</priority>\n  </url>\n'

            # Pages communes par catégorie
            for _, row in category_df.iterrows():
                xml_content += f'  <url>\n    <loc>{base_url}/address/{category_slug}/{row["commune_slug"]}</loc>\n    <priority>0.7</priority>\n  </url>\n'

    xml_content += '</urlset>'

    return Response(xml_content, mimetype='application/xml')

@app.route('/sitemap-html')
def sitemap_html():
    """Page sitemap HTML simple pour le crawl"""
    df = data_processor.df

    sitemap_data = {}
    for category_slug, category_name in CATEGORIES.items():
        if df is not None:
            category_df = df[df['category'] == category_slug]
            departments = {}

            for dept_code in sorted(category_df['department'].unique()):
                dept_name = DEPARTMENTS.get(dept_code, f"Département {dept_code}")
                dept_communes = category_df[category_df['department'] == dept_code].sort_values('nom_commune')

                communes_list = []
                for _, row in dept_communes.iterrows():
                    communes_list.append({
                        'name': row['nom_commune'],
                        'slug': row['commune_slug']
                    })

                departments[dept_code] = {
                    'name': dept_name,
                    'communes': communes_list
                }

            sitemap_data[category_slug] = {
                'name': category_name,
                'departments': departments
            }

    return render_template('sitemap_html.html',
                         categories=CATEGORIES,
                         sitemap_data=sitemap_data)

@app.route('/robots.txt')
def robots_txt():
    """Robots.txt pour les moteurs de recherche"""
    base_url = request.url_root.rstrip('/')
    content = f"""User-agent: *
Allow: /
Disallow: /api/
Disallow: /search?
Crawl-delay: 1

Sitemap: {base_url}/sitemap.xml
"""
    return Response(content, mimetype='text/plain')

def initialize_data():
    """Initialise les données au démarrage"""
    print("Initialisation des données...")
    try:
        # Charger et traiter les données
        data_processor.process_addresses()
        print("Données chargées avec succès!")

        # Optionnel: indexer dans Meilisearch
        try:
            data_processor.index_to_meilisearch()
            print("Indexation Meilisearch réussie!")
        except Exception as e:
            print(f"Avertissement: Meilisearch non disponible - {e}")
            print("L'application fonctionnera en mode recherche simple.")

    except Exception as e:
        print(f"Erreur lors de l'initialisation: {e}")

if __name__ == '__main__':
    initialize_data()
    print(f"Démarrage du serveur sur http://{SERVER_HOST}:{SERVER_PORT}")
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True)