from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from support.models import Project, ProjectContributors, Issue, Comment
from client.models import Client

UserModel = get_user_model()

CLIENTS = [
    {
        "name": "Meridien",
        "description": "Le SIG en ligne pour visualiser et explorer vos données sur mobile, tablette et desktop.",
    },
    {
        "name": "Magellium",
        "description": "L'un des leaders indépendants en France, expert en traitement d'images satellites, cartographie numérique et solutions de défense/sécurité complexes.",
    },
    {
        "name": "Camptocamp",
        "description": "Référence incontestée de l'Open Source, ils conçoivent des infrastructures SIG robustes basées sur QGIS, GeoServer et des solutions web sur mesure.",
    },
    {
        "name": "Esri France",
        "description": "Distributeur et intégrateur majeur de la suite ArcGIS, ils accompagnent les collectivités et grands comptes dans la transformation de leurs données.",
    },
    {
        "name": "Geofit",
        "description": "Spécialiste de l'acquisition et de l'exploitation de la donnée géographique (Lidar, photogrammétrie), ils créent des logiciels de gestion de patrimoine technique.",
    },
    {
        "name": "Isogeo",
        "description": "Expert en gouvernance des données, leur solution SaaS permet aux organisations de cataloguer, documenter et valoriser leurs patrimoines de données géospatiales.",
    },
    {
        "name": "Sogefi",
        "description": "Basée à Toulouse, cette entreprise est spécialisée dans les SIG web pour les collectivités.",
    },

]

CLIENT_1_PROJECTS = [
    {
        "name": "GeoNode",
        "description": "Système de gestion de contenu géospatial complet pour cataloguer, stocker et partager des données cartographiques au sein d'organisations.",
        "type": "Front-end",
        "author": "Alicia",
        "issues": [
            {
                "name":"Connexion impossible",
                "description":"Il est impossible de se connecter !",
                "priority":"High",
                "balise":"Bug",
                "progression":"To Do",
                "author": "Bob",
                "attribution": "Alicia",
                "comments":[
                    {
                        "description":"La touche majuscule est peut-être vérouillée ?",
                        "author": "Alicia"
                    },
                    {
                        "description":"Avez-vous vérifié votre accès internet ?",
                        "author": "Bob",
                    }
                ]
            },
            {
                "name":"Manque de clarté",
                "description":"Peut-on changer les couleurs ?",
                "priority":"Low",
                "balise":"Amélioration",
                "progression":"To Do",
                "author": "Bob",
                "attribution": "Bob",
                "comments":[
                    {
                        "description":"Un thème sombre conviendrait ?",
                        "author": "Alicia"
                    }
                ]
            }
        ]
    },
    {
        "name": "Atlas.co",
        "description": "Plateforme SIG cloud nouvelle génération mettant l'accent sur la rapidité, la collaboration en temps réel et l'intégration de l'IA.",
        "type": "Back-end",
        "author": "Bob",
        "issues": [
            {
                "name":"Format GeoJson non pris en charge",
                "description":"Ce standard est indispensable.",
                "priority":"High",
                "balise":"Amélioration",
                "progression":"To Do",
                "author": "Alicia",
                "attribution": "Bob",
                "comments":[]
            }
        ]
    },
    {
        "name": "Leaflet",
        "description": "Leaflet est la principale bibliothèque JavaScript open source pour la création de cartes interactives adaptées aux mobiles.",
        "type": "Android",
        "author": "Alicia",
        "issues": []
    },
    {
        "name": "ArcGIS Online",
        "description": "Leader du marché, cette plateforme cloud d'Esri permet de créer, partager et analyser des cartes interactives très complètes.",
        "type": "Android",
        "author": "Alicia",
        "issues": []
    },
    {
        "name": "Carto",
        "description": "Solution axée sur l'analyse de données massives ('Cloud Native'), idéale pour le géomarketing et les visualisations dynamiques complexes.",
        "type": "iOS",
        "author": "Bob",
        "issues": []
    },
    {
        "name": "Mapbox",
        "description": "Plateforme flexible pour les développeurs, offrant des cartes hautement personnalisables et des outils de navigation pour applications web.",
        "type": "Front-end",
        "author": "Alicia",
        "issues": []
    },
    {
        "name": "Felt",
        "description": "Outil moderne et collaboratif conçu pour créer des cartes rapidement à plusieurs, avec une interface intuitive et très fluide.",
        "type": "Back-end",
        "author": "Bob",
        "issues": []
    },
    {
        "name": "Google Earth Engine",
        "description": "Plateforme d'analyse géospatiale à l'échelle planétaire, utilisée par les chercheurs pour surveiller les changements environnementaux par satellite.",
        "type": "Android",
        "author": "Alicia",
        "issues": []
    },
    {
        "name": "GeoServer",
        "description": "Serveur cartographique open source permettant de diffuser des données géospatiales via des standards ouverts (WMS, WFS) sur le web.",
        "type": "Front-end",
        "author": "Bob",
        "issues": []
    },
    {
        "name": "QGIS Server",
        "description": "Version serveur du célèbre logiciel QGIS, elle permet de publier vos projets cartographiques bureautiques directement sur le web.",
        "type": "Back-end",
        "author": "Alicia",
        "issues": []
    },
    {
        "name": "MapStore",
        "description": "Cadre d'application moderne pour créer, gérer et partager des portails cartographiques et des tableaux de bord interactifs complets.",
        "type": "iOS",
        "author": "Alicia",
        "issues": []
    }
]

CLIENT_2_PROJECTS = [
    {
        "name": "MapInfo",
        "description": "Système d'Information Géographique utilisant des fichiers .TAB.",
        "type": "Front-end",
        "author": "Sophie",
        "issues": [
            {
                "name":"Sauvegarde des projets.",
                "description":"Impossible d'enregistrer le projet !",
                "priority":"High",
                "balise":"Bug",
                "progression":"To Do",
                "author": "Thierry",
                "attribution": "Sophie",
                "comments":[
                    {
                        "description":"Constaté à chauqe fois ?",
                        "author": "Sophie"
                    },
                    {
                        "description":"Depuis quelle version avez-vous constaté le problème ?",
                        "author": "Thierry",
                    }
                ]
            },
            {
                "name":"Aide de l'application",
                "description":"il n'y a pas de lien vers l'aide de l'application",
                "priority":"Low",
                "balise":"Amélioration",
                "progression":"To Do",
                "author": "Thierry",
                "attribution": "Thierry",
                "comments":[
                    {
                        "description":"Un lien vers la page du site pourrait convenir ?",
                        "author": "Sophie"
                    }
                ]
            }
        ]
    }
]

CLIENT_PROJECTS = [CLIENT_1_PROJECTS , CLIENT_2_PROJECTS]

class Command(BaseCommand):

    help = 'Initialize project for local development'

    UserModel.objects.all().delete()
    Project.objects.all().delete()
    Client.objects.all().delete()

    client_objects = []
    for client_data in CLIENTS:
        client_objects.append(
            Client.objects.create(
                name=client_data["name"],
                description=client_data["description"],
            )
        )

    super_user = UserModel.objects.create_superuser(
        username="meridien",
        password='meridien22',
        date_birth="1990-01-01",
        client=client_objects[0],
    )

    alicia_user = UserModel.objects.create_user(
        username="Alicia",
        password='alicia-pwd',
        date_birth="1980-01-01",
        is_staff=True,
        client=client_objects[1],
    )

    bob_user = UserModel.objects.create_user(
        username="Bob",
        password='bob-pwd',
        date_birth="1980-02-02",
        client=client_objects[1],
    )

    thierry_user = UserModel.objects.create_user(
        username="Thierry",
        password='thierry-pwd',
        date_birth="1980-03-03",
        is_staff=True,
        client=client_objects[2],
    )

    sophie_user = UserModel.objects.create_user(
        username="Sophie",
        password='sophie-pwd',
        date_birth="1980-04-04",
        client=client_objects[2],
    )

    def get_user(self, name):
        match name:
            case "Alicia":
                return self.alicia_user
            case "Bob":
                return self.bob_user
            case "Thierry":
                return self.thierry_user
            case "Sophie":
                return self.sophie_user
            case _:
                return None


    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING(self.help))

        for CLIENT_PROJECT in CLIENT_PROJECTS:

            for project_data in CLIENT_PROJECT:

                project = Project.objects.create(
                    name=project_data["name"],
                    description=project_data["description"],
                    type=project_data["type"],
                    author=self.get_user(project_data["author"]),
                )

                ProjectContributors.objects.create(
                    contributor = self.get_user(project_data["author"]),
                    project = project,
                )

                for issue_data in project_data["issues"]:
                    issue = Issue.objects.create(
                        name=issue_data["name"],
                        description=issue_data["description"],
                        priority=issue_data["priority"],
                        balise=issue_data["balise"],
                        progression=issue_data["progression"],
                        author=self.get_user(issue_data["author"]),
                        attribution=self.get_user(issue_data["attribution"]),
                        project=project,
                    )

                    for comment_data in issue_data["comments"]:
                        comment = Comment.objects.create(
                            description=comment_data["description"],
                            issue=issue,
                            author=self.get_user(project_data["author"]),
                        )
     
        self.stdout.write(self.style.SUCCESS("All Done !"))