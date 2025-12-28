import os

# Configuration Meilisearch
MEILISEARCH_URL = os.getenv('MEILISEARCH_URL', 'http://localhost:7700')
MEILISEARCH_KEY = os.getenv('MEILISEARCH_KEY', '')

# Configuration serveur
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8989

# Catégories métiers
CATEGORIES = {
    'couvreur': 'Couvreur',
    'pisciniste': 'Pisciniste',
    'plombier': 'Plombier',
    'vitrier': 'Vitrier',
    'architecte-interieur': "Architecte d'intérieur"
}

# Chemins
JSON_FILE = 'communes-france-avec-polygon-2025 (1).json'
TEMPLATES_DIR = 'templates'
STATIC_DIR = 'static'
OUTPUT_DIR = 'generated'

# Départements du Sud-Est (Auvergne-Rhône-Alpes et descente vers le Sud)
DEPARTMENTS = {
    # Auvergne-Rhône-Alpes
    '01': 'Ain',
    '03': 'Allier',
    '07': 'Ardèche',
    '15': 'Cantal',
    '26': 'Drôme',
    '38': 'Isère',
    '42': 'Loire',
    '43': 'Haute-Loire',
    '63': 'Puy-de-Dôme',
    '69': 'Rhône',
    '73': 'Savoie',
    '74': 'Haute-Savoie',

    # Provence-Alpes-Côte d'Azur
    '04': 'Alpes-de-Haute-Provence',
    '05': 'Hautes-Alpes',
    '06': 'Alpes-Maritimes',
    '13': 'Bouches-du-Rhône',
    '83': 'Var',
    '84': 'Vaucluse',

    # Occitanie (partie Est)
    '11': 'Aude',
    '30': 'Gard',
    '34': 'Hérault',
    '48': 'Lozère',
    '66': 'Pyrénées-Orientales'
}