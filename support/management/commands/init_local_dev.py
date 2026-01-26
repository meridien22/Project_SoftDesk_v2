from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from support.models import Project, ProjectContributors, Issue, Comment

UserModel = get_user_model()

PROJECTS = [
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
                "name":"Manque de clareté",
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

class Command(BaseCommand):

    help = 'Initialize project for local development'

    UserModel.objects.all().delete()
    Project.objects.all().delete()

    super_user = UserModel.objects.create_superuser(
        username="meridien",
        password='meridien22',
        date_birth="1990-01-01"
    )

    alicia_user = UserModel.objects.create_user(
        username="Alicia",
        password='alicia-pwd',
        date_birth="1980-01-01",
        is_staff=True
    )

    bob_user = UserModel.objects.create_user(
        username="Bob",
        password='bob-pwd',
        date_birth="1980-02-02"
    )

    def get_user(self, name):
        match name:
            case "Alicia":
                return self.alicia_user
            case "Bob":
                return self.bob_user
            case _:
                return None


    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING(self.help))

        for project_data in PROJECTS:
            project = Project.objects.create(
                name=project_data["name"],
                description=project_data["description"],
                type=project_data["type"],
                author=self.get_user(project_data["author"])
            )

            ProjectContributors.objects.create(
                contributor = self.alicia_user,
                project = project
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
                    project=project
                )
                for comment_data in issue_data["comments"]:
                    comment = Comment.objects.create(
                        description=comment_data["description"],
                        issue=issue,
                        author=self.get_user(project_data["author"])
                    )


        self.stdout.write(self.style.SUCCESS("All Done !"))