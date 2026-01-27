from django.db import models
from django.contrib.auth.models import AbstractUser
from client.models import Client


class User(AbstractUser):
    date_birth = models.DateField(verbose_name="Date de naissance")
    can_be_contacted = models.BooleanField(null=True)
    can_data_be_collected = models.BooleanField(null=True)
    can_data_be_shared = models.BooleanField(null=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="users",
    )
    # En Django, REQUIRED_FIELDS ne sert que pour la commande createsuperuser dans le terminal.
    REQUIRED_FIELDS = ['date_birth']