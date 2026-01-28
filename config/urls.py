from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt. views import TokenObtainPairView, TokenRefreshView

from support.views import (
    ProjectViewset, 
    AdminProjectViewset,
    AdminIssueViewset
)
from authentication.views import UserAPIView

router = routers.SimpleRouter()
router.register("project", ProjectViewset, basename="project")
router.register("admin/project", AdminProjectViewset, basename="admin_project")
router.register("admin/issue", AdminIssueViewset, basename="admin_issue")

# !! QUESTION PHILOSOPHIQUE !!
# on peut implémenter 2 stratégies de nommage pour les endpoints
# exemple pour ajouter un commentaire
# URL "à plat" : POST /comments/ (JSON envoyé : {"project": 123, "content": "Super projet !"})
# URL "imbriquée" : POST /projects/1/comments/ (nécessite d'installer la bibliothèque drf-nested-routers)
# Problème de conflit de version :
# Python (3.9, 3.10, 3.11, 3.12, 3.13)
# Django (4.2, 5.0, 5.1, 5.2)
# Django REST Framework (3.14, 3.15, 3.16)
# choix de ne pas utiliser drf-nested-routers car on n'en parle pas dans le cours

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/user/', UserAPIView.as_view()),
    path("api/", include(router.urls))

    # création d'un nouvel utilisateur => doit être authentifié en tant que is_staff
    # path("api/sign-up/", "", name=""),

    # gestion des projets
    # verbe HTTP POST : création d'un projet => doit être authentifié
    # verbe HTTP GET : lecture d'un projet => doit être authentifié et contributeur du projet
    # verbe HTTP PUT : mise à jour total d'un projet => doit être authentifié et auteur du projet
    # verbe HTTP PATCH : mise à jour partielle d'un projet => doit être authentifié et auteur du projet
    # verbe HTTP DELETE : supression d'un projet => doit être authentifié en tant que is_staff
    # path("api/project/", "", name=""),

    # gestion des contributeurs
    # verbe HTTP POST : création d'un contributeur => doit être authentifié et auteur du projet
    # verbe HTTP GET : lecture des contributeurs => doit être authentifié et auteur du projet
    # verbe HTTP PUT : sans objet
    # verbe HTTP PATCH : sans objet
    # verbe HTTP DELETE : supression d'un projet => doit être authentifié en tant que is_staff
    # path("api/contributor/", "", name=""),

    # gestion des problèmes
    # verbe HTTP POST : création d'un problème => doit être authentifié et contributeur du projet
    # verbe HTTP GET : lecture d'un problème => doit être authentifié et contributeur du projet
    # verbe HTTP PUT : mise à jour total d'un problème => doit être authentifié et auteur du problème
    # verbe HTTP PATCH : mise à jour partielle d'un problème => doit être authentifié et auteur du problème
    # verbe HTTP DELETE : supression d'un problème => doit être authentifié et auteur du problème
    # path("api/issue/", "", name=""),

    # gestion des commentaires
    # verbe HTTP POST : création d'un commentaire => doit être authentifié et contributeur du projet
    # verbe HTTP GET : lecture d'un commentaire => doit être authentifié et contributeur du projet
    # verbe HTTP PUT : mise à jour total d'un commentaire => doit être authentifié et auteur du commentaire
    # verbe HTTP PATCH : mise à jour partielle d'un commentaire => doit être authentifié et auteur du commentaire
    # verbe HTTP DELETE : supression d'un commentaire => doit être authentifié et auteur du commentaire
    # path("api/comment/", "", name=""),

]
