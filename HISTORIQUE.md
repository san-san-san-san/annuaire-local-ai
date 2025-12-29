# HISTORIQUE DES ECHANGES - Projet Annuaire Professionnel

## Session du 29 Décembre 2025

### Contexte initial
- **Projet** : Annuaire professionnel pour artisans du Sud-Est de la France
- **Technologies** : Flask, Jinja2, Meilisearch, Pandas, Tailwind CSS
- **Domaine** : eirl-meirland.fr
- **Serveur** : CloudPanel sur OVH (51.77.148.205)

---

## Echange 1 : Problème des pages vides

### Question utilisateur
> "pourquoi il n'y a pas de page sur le site ? normalement il y a des milliers de pages sur le site"

### Diagnostic
- Vérification de la structure des routes dans `app.py`
- Analyse du modèle de données dans `data_processor_json.py`

### Cause identifiée
Dans `prepare_communes_data()`, chaque commune était assignée à UNE SEULE catégorie aléatoire :
```python
commune_data['category'] = random.choice(list(CATEGORIES.keys()))
```

Cela signifiait que sur 5 catégories, seule 1 était disponible par commune = 80% des pages étaient vides.

---

## Echange 2 : Page spécifique vide

### Question utilisateur
> "ici la page est vide, pk : https://eirl-meirland.fr/category/architecte-interieur/cesset ? active tout les agents et plugins pour améliorer le code et le site stp"

### Actions réalisées

#### 1. Correction du modèle de données
Modification de `data_processor_json.py` :
```python
# Créer une entrée pour CHAQUE catégorie pour chaque commune
for category in CATEGORIES.keys():
    commune_data = {
        'id': f"{commune['code_insee']}_{category}",
        # ...
        'category': category,
    }
    prepared_communes.append(commune_data)
```

#### 2. Mise à jour de `get_commune_by_slug()`
Ajout du paramètre `category` pour filtrer correctement.

#### 3. Correction du déploiement
Après upload, l'app.py était écrasé sans l'appel `data_processor.process_addresses()`. Ajouté à nouveau.

#### 4. Améliorations SEO
- Ajout route `/robots.txt`
- Ajout canonical URLs dans base.html
- Ajout Open Graph meta tags
- Ajout Twitter Card meta tags
- Ajout hreflang tags

---

## Echange 3 : Enrichissement des pages villes

### Question utilisateur
> "parfait, merci. Ajoute stp un peu de contenu, de contexte, maillage interne dans les pages villes comme celle la : https://eirl-meirland.fr/category/plombier/arfeuilles"

### Analyse de la page existante
La page contenait uniquement :
- Un titre basique
- Un numéro de téléphone
- Aucun contenu textuel
- Aucun maillage interne

### Actions réalisées

#### 1. Enrichissement de `app.py` - route `city_page()`

Ajout de :
- **Génération de contenu** : `content_generator.generate_content(commune_data)`
- **Communes proches** : Calcul géographique dans un rayon de 30km, max 6 résultats
- **Autres services** : Liste des 4 autres catégories disponibles dans la même ville
- **Maillage département** : 8 autres villes du même département

#### 2. Refonte complète de `templates/city.html`

Nouvelle structure :
```
┌─────────────────────────────────────────────┐
│ Breadcrumb (Schema.org BreadcrumbList)      │
├─────────────────────────────────────────────┤
│ CTA Principal (téléphone + message)         │
├──────────────────────────┬──────────────────┤
│                          │ Sidebar          │
│ Contenu Principal        │ - Fiche commune  │
│ - Introduction           │ - CTA téléphone  │
│ - Description            │ - Autres services│
│ - Expertise              │                  │
│ - Services (liste)       │                  │
│ - Conclusion             │                  │
│                          │                  │
│ Maillage : Villes proches│                  │
│ Maillage : Même départ.  │                  │
├──────────────────────────┴──────────────────┤
│ Schema.org LocalBusiness (JSON-LD)          │
├─────────────────────────────────────────────┤
│ CTA Mobile Sticky (visible sur mobile)      │
└─────────────────────────────────────────────┘
```

#### 3. Templates de contenu spécifiques dans `content_generator.py`

Création de templates pour les 5 métiers :
- **Plombier** : 4 intros, 4 descriptions, 3 expertises, 4 conclusions
- **Couvreur** : 4 intros, 4 descriptions, 3 expertises, 4 conclusions
- **Pisciniste** : 4 intros, 4 descriptions, 3 expertises, 4 conclusions
- **Vitrier** : 4 intros, 4 descriptions, 3 expertises, 4 conclusions
- **Architecte d'intérieur** : 4 intros, 4 descriptions, 4 expertises, 4 conclusions

Variables dynamiques : `{city}`, `{postal_code}`, `{profession}`, `{profession_lower}`

---

## Echange 4 : Documentation et Git

### Question utilisateur
> "c'est vraiment du super boulot ca merci. tu peux faire un changelog complet et archi détaillé, un historique de nos échanges, un plan détaillé et complet pour claude code pour la prochaine fois et ensuite tu git init, cree un repo privé si pas déja fait et ensuite tu commit et push"

### Actions en cours
1. Création de `CHANGELOG.md` (ce fichier)
2. Création de `HISTORIQUE.md` (ce fichier)
3. Création de `CLAUDE_CODE_PLAN.md`
4. Vérification Git (déjà initialisé, repo existant)
5. Commit et push

---

## Echange 5 : Google Search Console

### Question utilisateur
> "ajoute cette balise dans head stp pour la search console et push en prod : <meta name="google-site-verification" content="8GuLm4jVzqcW01uJBaQUdoRsFr2-u5A5mgb244DPuuE" />"

### Action réalisée
- Ajout de la balise dans `templates/base.html` ligne 6
- Déploiement en production

---

## Résumé des fichiers modifiés

| Fichier | Modifications |
|---------|---------------|
| `data_processor_json.py` | Modèle de données (toutes catégories), `get_commune_by_slug()` |
| `app.py` | Route `city_page()` enrichie, route `robots_txt()` |
| `templates/base.html` | SEO meta tags, Google Search Console |
| `templates/city.html` | Refonte complète avec contenu et maillage |
| `content_generator.py` | Templates spécifiques par métier |

---

## Commandes de déploiement utilisées

```bash
# Upload des fichiers Python
sshpass -p 'PASSWORD' scp app.py content_generator.py data_processor_json.py \
  root@51.77.148.205:/home/eirlmeirland/htdocs/eirl-meirland.fr/

# Upload des templates
sshpass -p 'PASSWORD' scp templates/*.html \
  root@51.77.148.205:/home/eirlmeirland/htdocs/eirl-meirland.fr/templates/

# Redémarrage Gunicorn (via signal HUP au master process)
sshpass -p 'PASSWORD' ssh root@51.77.148.205 "kill -HUP $(pgrep -f 'gunicorn.*app:app' | head -1)"
```

---

## Informations serveur

- **IP** : 51.77.148.205
- **SSH** : root / bhsZHvGBBhrB747488
- **Chemin site** : /home/eirlmeirland/htdocs/eirl-meirland.fr/
- **Venv Python** : /home/eirlmeirland/htdocs/eirl-meirland.fr/venv/
- **Gunicorn** : 3 workers sur 127.0.0.1:8000
- **Proxy** : Nginx vers Gunicorn
