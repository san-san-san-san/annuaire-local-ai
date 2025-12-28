import random

class ContentGenerator:
    """Générateur de contenu spinné pour les fiches détaillées"""

    def __init__(self):
        # Templates d'introduction génériques
        self.intro_templates = [
            "Découvrez {city}, une commune parfaite pour contacter un {profession} expérimenté. Située dans le {postal_code}, cette localisation bénéficie d'un accès privilégié aux services de {profession_lower}.",
            "La commune de {city} ({postal_code}) constitue un point de référence incontournable pour tous vos besoins en {profession_lower}. Cette zone dynamique offre de nombreux avantages.",
            "Située à {city}, cette commune du {postal_code} représente un emplacement stratégique pour vos projets nécessitant l'intervention d'un {profession_lower} qualifié.",
            "Au cœur de {city} ({postal_code}), vous trouverez un service de {profession_lower} de qualité, dans un environnement privilégié."
        ]

        # Templates d'introduction spécifiques par catégorie
        self.intro_templates_by_category = {
            'architecte-interieur': [
                "Vous recherchez un architecte d'intérieur à {city} pour sublimer votre habitat ? Les professionnels du {postal_code} vous accompagnent dans tous vos projets de décoration et d'aménagement intérieur, du simple conseil à la rénovation complète.",
                "Transformez votre intérieur à {city} grâce à l'expertise d'un architecte d'intérieur local. Dans le secteur du {postal_code}, nos professionnels créent des espaces de vie uniques, fonctionnels et à votre image.",
                "L'architecture d'intérieur à {city} ({postal_code}) prend une nouvelle dimension avec des experts passionnés. Conception sur-mesure, optimisation d'espace et décoration tendance : confiez votre projet à des professionnels certifiés.",
                "Besoin de repenser l'agencement de votre appartement ou maison à {city} ? Les architectes d'intérieur du {postal_code} combinent esthétique et fonctionnalité pour créer l'intérieur de vos rêves."
            ]
        }

        # Templates de description génériques
        self.description_templates = [
            "Cette commune stratégiquement positionnée, {city}, offre de nombreux avantages. Les professionnels {profession_lower}s de la région sont reconnus pour leur expertise et leur savoir-faire. Le secteur du {postal_code} bénéficie d'une excellente desserte et d'une accessibilité optimale.",
            "La commune de {city} est particulièrement appréciée pour sa tranquillité et sa proximité avec les commodités. Les {profession_lower}s locaux interviennent régulièrement dans ce secteur privilégié du {postal_code}.",
            "Cette localisation à {city} présente tous les atouts pour vos projets. La zone du {postal_code} est desservie par de nombreux professionnels {profession_lower}s compétents, garantissant un service de proximité de qualité.",
            "Implantée dans un secteur recherché, {city} du {postal_code} bénéficie d'un environnement favorable. Les {profession_lower}s de la région sont réputés pour leur professionnalisme et leur réactivité."
        ]

        # Templates de description spécifiques par catégorie
        self.description_templates_by_category = {
            'architecte-interieur': [
                "À {city}, l'architecture d'intérieur est un art maîtrisé par des professionnels passionnés. Que vous souhaitiez rénover un appartement haussmannien, optimiser un studio ou créer une ambiance contemporaine dans votre maison, les experts du {postal_code} vous guident à chaque étape. Leur connaissance du patrimoine local et des contraintes architecturales régionales constitue un atout précieux.",
                "Le secteur du {postal_code} concentre des talents en architecture d'intérieur reconnus pour leur créativité et leur rigueur. À {city}, ces professionnels interviennent aussi bien pour les particuliers que pour les professionnels : réaménagement de bureaux, décoration de commerces, home staging pour la vente immobilière. Chaque projet bénéficie d'une approche personnalisée.",
                "Les architectes d'intérieur de {city} se distinguent par leur écoute attentive et leur capacité à traduire vos envies en réalisations concrètes. Du premier rendez-vous à la remise des clés, ils coordonnent l'ensemble des intervenants : menuisiers, peintres, électriciens, cuisinistes. Le {postal_code} dispose ainsi d'un écosystème complet pour mener à bien votre projet.",
                "Investir dans l'architecture d'intérieur à {city} ({postal_code}), c'est valoriser votre bien immobilier tout en améliorant votre qualité de vie quotidienne. Les professionnels locaux maîtrisent les dernières tendances — biophilie, couleurs terracotta, matériaux naturels — tout en respectant votre budget et vos contraintes techniques."
            ]
        }

        self.expertise_templates = {
            'couvreur': [
                "Les couvreurs de {city} maîtrisent parfaitement les techniques de couverture traditionnelles et modernes. Ils interviennent pour tous types de toitures : tuiles, ardoises, zinc, et matériaux écologiques.",
                "L'expertise des professionnels de la couverture dans le {postal_code} couvre l'installation, la réparation et l'entretien des toitures. Ils garantissent l'étanchéité et la durabilité de vos couvertures.",
                "Les artisans couvreurs de {city} proposent des solutions complètes : zinguerie, isolation, démoussage, et installation de systèmes solaires intégrés."
            ],
            'pisciniste': [
                "Les piscinistes de {city} conçoivent et réalisent des piscines sur mesure adaptées à tous les terrains. Leur expertise couvre les piscines enterrées, semi-enterrées et hors-sol.",
                "Dans le secteur du {postal_code}, les professionnels de la piscine maîtrisent toutes les technologies : béton, coque polyester, liner, et systèmes de filtration innovants.",
                "Les spécialistes piscine de {city} assurent également l'entretien, la rénovation et l'hivernage de votre bassin pour une eau cristalline toute l'année."
            ],
            'plombier': [
                "Les plombiers de {city} interviennent pour tous vos besoins en plomberie : installation, dépannage, rénovation de salles de bain et cuisines.",
                "Dans le {postal_code}, les artisans plombiers maîtrisent les dernières technologies : plomberie écologique, systèmes de récupération d'eau, et chauffage performant.",
                "Les professionnels de la plomberie à {city} assurent un service rapide et efficace, disponibles pour les urgences et les projets de rénovation."
            ],
            'vitrier': [
                "Les vitriers de {city} expertisent tous types de vitrages : simple, double, triple vitrage, et verres spéciaux sécurisés ou décoratifs.",
                "Dans le secteur du {postal_code}, les professionnels du vitrage proposent des solutions sur mesure : baies vitrées, vérandas, et miroiterie d'art.",
                "Les artisans vitriers de {city} maîtrisent les techniques modernes : pose, réparation, et remplacement de vitrages avec garantie d'étanchéité."
            ],
            'architecte-interieur': [
                "Les architectes d'intérieur de {city} allient créativité et expertise technique pour transformer vos espaces. De la conception initiale à la livraison finale, ils orchestrent chaque détail : choix des matériaux nobles, agencement optimal des volumes, jeux de lumière naturelle et artificielle. Leur connaissance approfondie des tendances actuelles — du minimalisme japonais au maximalisme coloré — garantit un résultat unique adapté à votre personnalité.",
                "Dans le secteur du {postal_code}, les professionnels de l'architecture d'intérieur excellent dans l'art de sublimer les espaces contraints. Maîtres du home staging, de la rénovation d'appartements anciens et de l'optimisation des petites surfaces, ils créent des intérieurs fonctionnels sans sacrifier l'esthétique. Leur réseau d'artisans locaux qualifiés assure une exécution irréprochable de chaque projet.",
                "Les spécialistes en architecture d'intérieur de {city} proposent un accompagnement sur-mesure : diagnostic de vos besoins, élaboration de moodboards inspirants, modélisation 3D photoréaliste, sélection de mobilier et objets déco, et suivi de chantier rigoureux. Leur expertise s'étend du résidentiel haut de gamme aux espaces professionnels : bureaux, commerces, hôtels et restaurants.",
                "Faire appel à un architecte d'intérieur à {city} ({postal_code}), c'est bénéficier d'un regard expert pour repenser votre habitat. Ces professionnels certifiés maîtrisent les normes d'accessibilité, les contraintes techniques du bâti ancien comme contemporain, et les solutions éco-responsables. Leur objectif : créer des lieux de vie harmonieux qui vous ressemblent, tout en valorisant votre patrimoine immobilier."
            ]
        }

        # Templates de conclusion génériques
        self.conclusion_templates = [
            "Pour tous vos projets nécessitant l'intervention d'un {profession_lower} à {city}, cette commune du {postal_code} représente un point de repère idéal. N'hésitez pas à contacter les professionnels locaux pour obtenir des devis personnalisés.",
            "Cette localisation à {city} vous garantit un accès privilégié aux meilleurs {profession_lower}s de la région. Le secteur du {postal_code} bénéficie d'une couverture professionnelle de qualité.",
            "Faire appel à un {profession_lower} à {city} vous assure un service de proximité et une intervention rapide. Les professionnels du {postal_code} sont à votre écoute.",
            "Cette commune stratégique de {city} vous connecte aux {profession_lower}s les plus qualifiés de la région. Le {postal_code} dispose d'un réseau de professionnels expérimentés et fiables."
        ]

        # Templates de conclusion spécifiques par catégorie
        self.conclusion_templates_by_category = {
            'architecte-interieur': [
                "Prêt à transformer votre intérieur à {city} ? Contactez dès maintenant un architecte d'intérieur du {postal_code} pour une première consultation. Devis gratuit, conseils personnalisés et accompagnement sur-mesure vous attendent pour concrétiser le projet de vos rêves.",
                "Les architectes d'intérieur de {city} sont à votre disposition pour donner vie à vos idées. Du simple relooking à la rénovation totale, les professionnels du {postal_code} s'adaptent à tous les budgets et à toutes les envies. Demandez votre devis personnalisé dès aujourd'hui.",
                "Vous méritez un intérieur qui vous ressemble. À {city} ({postal_code}), les architectes d'intérieur locaux mettent leur expertise à votre service pour créer des espaces uniques, fonctionnels et esthétiques. Premier rendez-vous offert pour discuter de votre projet.",
                "Ne laissez plus votre décoration au hasard. Les professionnels de l'architecture d'intérieur à {city} vous accompagnent pour optimiser chaque mètre carré de votre habitat. Prenez rendez-vous avec un expert du {postal_code} et découvrez le potentiel de votre espace."
            ]
        }

    def generate_content(self, commune_data):
        """Génère le contenu complet pour une fiche commune"""
        category = commune_data['category']
        profession = CATEGORIES[category]
        profession_lower = profession.lower()

        variables = {
            'city': commune_data['nom_commune'],
            'postal_code': commune_data['code_postal'],
            'profession': profession,
            'profession_lower': profession_lower
        }

        # Sélection des templates selon la catégorie
        if category in self.intro_templates_by_category:
            intro = random.choice(self.intro_templates_by_category[category])
        else:
            intro = random.choice(self.intro_templates)

        if category in self.description_templates_by_category:
            description = random.choice(self.description_templates_by_category[category])
        else:
            description = random.choice(self.description_templates)

        if category in self.conclusion_templates_by_category:
            conclusion = random.choice(self.conclusion_templates_by_category[category])
        else:
            conclusion = random.choice(self.conclusion_templates)

        content = {
            'intro': intro.format(**variables),
            'description': description.format(**variables),
            'expertise': random.choice(self.expertise_templates[category]).format(**variables),
            'conclusion': conclusion.format(**variables)
        }

        return content

# Import pour avoir accès à CATEGORIES
from config import CATEGORIES