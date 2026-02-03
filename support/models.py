from django.db import models
from django.conf import settings
import uuid
from client.models import Client


class ActiveProjectManager(models.Manager):
    def get_queryset(self):
        # On filtre par défaut sur is_active=True
        return super().get_queryset().filter(is_active=True)


class Project(models.Model):


    class Meta:
        ordering = ['id']

    class Type(models.TextChoices):
        BACKEND = "Back-end"
        FRONTEND = "Front-end"
        IOS = "iOS"
        ANDROID = "Android"


    name = models.CharField(max_length=128)
    description = models.CharField(max_length=2048, blank=True)
    type = models.CharField(max_length=30, choices=Type.choices, verbose_name='Type de projet')
    time_created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_projects",
    )
    contributors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ProjectContributors",
        related_name="contributions",
    )
    is_active = models.BooleanField(default=True)

    # Le manager par défaut employé par le modèle
    objects = ActiveProjectManager()
    # Le manager à employer si on veut voir tout les projets y compris les inactifs
    all_objects = models.Manager()


# Le champ contributors : sert à aller du Projet vers les Utilisateurs (project.contributors).
# Le related_name="contributions" : sert à aller de l'Utilisateur vers les Projets (user.contributions).

# Tous les utilisateurs (User) liés au projet :

# contributors = my_project.contributors.all()
# contributors = User.objects.filter(contributions__id=my_project.id)

# Récupère les instances du modèle intermédiaire
# memberships = ProjectContributors.objects.filter(project=my_project)
# Pour obtenir les utilisateurs à partir de là :
# users = [m.contributor for m in memberships]

# Une seule requête pour les projets + une seule pour tous les contributeurs
# projects = Project.objects.prefetch_related('contributors').all()
# for project in projects:
#     print(project.name)
#     print(project.contributors.all())

# Tous les projets d'un utilisateur
# projects = user.contributions.all()
# projects = Project.objects.filter(contributors__id=user.id)
# projects = Project.objects.filter(contributors__username='alice')

class Issue(models.Model):

    class Balise(models.TextChoices):
        BUG = "Bug"
        TASK = "Tâche"
        FEATURE = "Amélioration"


    class Priority(models.TextChoices):
        LOW = "Low"
        MEDIUM = "Medium"
        HIGH = "High"


    class Progression(models.TextChoices):
        TODO = "To Do"
        INPROGRESS = "In Progress"
        FINISHED = "Finished"


    name = models.CharField(max_length=128)
    description = models.CharField(max_length=2048, blank=True)
    priority = models.CharField(max_length=30, choices=Priority.choices)
    attribution = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_issues"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_issues"
    )
    balise = models.CharField(max_length=30, choices=Balise.choices)
    progression = models.CharField(
        max_length=30,
        choices=Progression.choices,
        default='TODO'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="issues"
    )
    time_created = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    description = models.CharField(max_length=2048, blank=True)
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    # l'utilisateur doit aussi donner un lien vers une issue, ! à implémenter !
    time_created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )


class ProjectContributors(models.Model):
    contributor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name = "project_links",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name = "contributor_links",
    )
    time_created = models.DateTimeField(auto_now_add=True)
