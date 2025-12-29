# PLAN CLAUDE CODE - Annuaire Professionnel Sud-Est

## Informations Projet

### Identité
- **Nom** : Annuaire Professionnel Sud-Est France
- **Domaine** : eirl-meirland.fr
- **Repository** : https://github.com/lkmeldv/annuaire-ville-plusieurs-metiers.git
- **Type** : Site SEO programmatique / Annuaire local

### Stack Technique
- **Backend** : Python 3.13, Flask 3.x
- **Templates** : Jinja2
- **CSS** : Tailwind CSS (CDN)
- **Recherche** : Meilisearch (optionnel, fallback pandas)
- **Données** : JSON (communes_france.json)
- **WSGI** : Gunicorn

### Serveur Production
```
IP: 51.77.148.205
SSH: root / bhsZHvGBBhrB747488
Chemin: /home/eirlmeirland/htdocs/eirl-meirland.fr/
Venv: /home/eirlmeirland/htdocs/eirl-meirland.fr/venv/
```

---

## Architecture Fichiers

```
testmeilsearch/
├── app.py                      # Routes Flask principales
├── config.py                   # CATEGORIES, DEPARTMENTS, chemins
├── content_generator.py        # Génération contenu spinné
├── data_processor_json.py      # Chargement et traitement données
├── communes_france.json        # ~36,000 communes France
├── requirements.txt            # Dépendances
├── templates/
│   ├── base.html              # Layout + SEO meta tags
│   ├── home.html              # Page d'accueil
│   ├── departments.html       # Liste départements par catégorie
│   ├── department_cities.html # Villes d'un département
│   ├── city.html              # Page ville enrichie (PRINCIPAL)
│   ├── search.html            # Recherche
│   ├── sitemap.html           # Plan du site
│   └── sitemap_html.html      # Sitemap HTML crawlable
├── CHANGELOG.md               # Journal des modifications
├── HISTORIQUE.md              # Historique des échanges
└── CLAUDE_CODE_PLAN.md        # Ce fichier
```

---

## Configuration (config.py)

### Catégories de métiers
```python
CATEGORIES = {
    'plombier': 'Plombier',
    'couvreur': 'Couvreur',
    'pisciniste': 'Pisciniste',
    'vitrier': 'Vitrier',
    'architecte-interieur': 'Architecte d\'intérieur'
}
```

### Départements couverts
```python
DEPARTMENTS = {
    '01': 'Ain',
    '03': 'Allier',
    '07': 'Ardèche',
    '26': 'Drôme',
    '38': 'Isère',
    '42': 'Loire',
    '69': 'Rhône',
    '73': 'Savoie',
    '74': 'Haute-Savoie'
}
```

---

## Routes Principales (app.py)

| Route | Fonction | Description |
|-------|----------|-------------|
| `/` | `home()` | Page d'accueil avec stats |
| `/category/<slug>` | `category_page()` | Liste départements par catégorie |
| `/category/<cat>/<city>` | `city_page()` | **PAGE PRINCIPALE** - Contenu enrichi |
| `/category/<cat>/department/<dept>` | `department_cities_page()` | Villes d'un département |
| `/search` | `search()` | Recherche textuelle |
| `/sitemap` | `sitemap()` | Plan du site HTML |
| `/sitemap.xml` | `sitemap_xml()` | Sitemap XML Google |
| `/robots.txt` | `robots_txt()` | Robots.txt |

---

## Modèle de Données

### Structure d'une entrée commune
```python
{
    'id': '01001_plombier',           # code_insee_category
    'code_insee': '01001',
    'nom_commune': 'Ambérieu-en-Bugey',
    'code_postal': '01500',
    'department': '01',
    'dep_nom': 'Ain',
    'region': 'Auvergne-Rhône-Alpes',
    'population': 14500,
    'lat': 45.9567,
    'lon': 5.3456,
    'category': 'plombier',
    'superficie_km2': 24.5,
    'altitude_moyenne': 250,
    'commune_slug': 'amberieu-en-bugey',
    'city_slug': 'amberieu-en-bugey'      # alias
}
```

### Important
**Chaque commune a 5 entrées** (une par catégorie), soit ~12,500 entrées pour ~2,500 communes.

---

## Génération de Contenu (content_generator.py)

### Structure du contenu généré
```python
content = {
    'intro': "Introduction spécifique au métier...",
    'description': "Description détaillée...",
    'expertise': "Notre expertise...",
    'conclusion': "CTA avec numéro de téléphone..."
}
```

### Variables disponibles
- `{city}` : Nom de la commune
- `{postal_code}` : Code postal
- `{profession}` : Nom du métier (majuscule)
- `{profession_lower}` : Nom du métier (minuscule)

### Templates par catégorie
Chaque catégorie a ses propres templates dans :
- `intro_templates_by_category`
- `description_templates_by_category`
- `expertise_templates`
- `conclusion_templates_by_category`

---

## Maillage Interne (city.html)

### 1. Communes proches
```python
nearby_communes = data_processor.get_nearby_communes(
    lat=commune_data.get('lat', 0),
    lon=commune_data.get('lon', 0),
    category=category_slug,
    current_commune_id=commune_data['id'],
    radius_km=30,  # Rayon de recherche
    limit=6        # Nombre max
)
```

### 2. Autres services
Liens vers les 4 autres catégories pour la même ville.

### 3. Même département
8 autres villes du même département pour la même catégorie.

---

## Commandes de Déploiement

### Upload fichiers
```bash
# Fichiers Python
sshpass -p 'bhsZHvGBBhrB747488' scp app.py content_generator.py data_processor_json.py \
  root@51.77.148.205:/home/eirlmeirland/htdocs/eirl-meirland.fr/

# Templates
sshpass -p 'bhsZHvGBBhrB747488' scp templates/*.html \
  root@51.77.148.205:/home/eirlmeirland/htdocs/eirl-meirland.fr/templates/
```

### Redémarrage Gunicorn
```bash
# Méthode 1 : Signal HUP (graceful reload)
sshpass -p 'bhsZHvGBBhrB747488' ssh root@51.77.148.205 \
  "kill -HUP \$(pgrep -f 'gunicorn.*app:app' -o)"

# Méthode 2 : Si le process ID est connu
sshpass -p 'bhsZHvGBBhrB747488' ssh root@51.77.148.205 "kill -HUP 2976669"
```

### Vérification
```bash
# Status HTTP
curl -s -o /dev/null -w "%{http_code}" "https://eirl-meirland.fr/category/plombier/arfeuilles"

# Processus Gunicorn
sshpass -p 'bhsZHvGBBhrB747488' ssh root@51.77.148.205 "ps aux | grep gunicorn"
```

---

## Tâches Futures Possibles

### SEO
- [ ] Ajouter structured data FAQ sur les pages villes
- [ ] Créer des pages "métier + département" (ex: plombier-ain)
- [ ] Ajouter des avis/témoignages fictifs
- [ ] Optimiser les images (pas d'images actuellement)

### Contenu
- [ ] Ajouter plus de variations de templates
- [ ] Créer des contenus saisonniers (chauffage hiver, piscine été)
- [ ] Ajouter des articles de blog par catégorie

### Technique
- [ ] Mettre en cache les pages avec Redis ou Flask-Caching
- [ ] Ajouter des tests unitaires
- [ ] Créer un script de génération statique (pour CDN)
- [ ] Implémenter la recherche Meilisearch complètement

### Maillage
- [ ] Ajouter liens vers communes limitrophes (pas seulement rayon)
- [ ] Créer des "hubs" régionaux
- [ ] Ajouter des liens inter-catégories thématiques

---

## Dépannage Courant

### Page 404 ou vide
1. Vérifier que la commune existe dans le JSON source
2. Vérifier que `data_processor.process_addresses()` est appelé au démarrage
3. Vérifier que la catégorie existe dans CATEGORIES

### Erreur 500
1. Consulter les logs : `journalctl -u gunicorn` ou logs CloudPanel
2. Vérifier la syntaxe Jinja2 dans les templates
3. Vérifier les imports dans app.py

### Gunicorn ne redémarre pas
1. Trouver le PID master : `pgrep -f 'gunicorn.*app:app' -o`
2. Envoyer SIGHUP : `kill -HUP <PID>`
3. Si bloqué, kill et relancer manuellement

### Meilisearch non disponible
L'application fonctionne sans Meilisearch grâce au fallback pandas dans `search_addresses()`.

---

## Conventions de Code

### Nommage
- Routes : snake_case (`city_page`, `category_page`)
- Templates : snake_case.html (`city.html`, `base.html`)
- Variables Jinja : snake_case (`category_name`, `city_slug`)

### Templates
- Toujours hériter de `base.html`
- Utiliser les blocks : `title`, `meta_description`, `content`
- Inclure Schema.org pour les pages importantes

### Commits
Format : `type: description`
- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `seo:` amélioration SEO
- `refactor:` refactoring code
- `docs:` documentation

---

## Contacts & Ressources

### URLs de test
- Page plombier : https://eirl-meirland.fr/category/plombier/arfeuilles
- Page architecte : https://eirl-meirland.fr/category/architecte-interieur/arfeuilles
- Sitemap XML : https://eirl-meirland.fr/sitemap.xml
- Robots.txt : https://eirl-meirland.fr/robots.txt

### Numéro affiché sur le site
**04 58 10 57 19** (utilisé dans tous les CTA)
