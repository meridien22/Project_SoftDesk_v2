from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from client.models import Client


class CustomUserManager(UserManager):

    def _assign_client_by_email(self, email):
        if email and "@" in email:
            domain = email.split('@')[-1].lower()
            try:
                return Client.objects.get(domain=domain)
            except Client.DoesNotExist:
                raise ValidationError("Ce domaine d'email n'est rattaché à aucun client.")
        return None

    def create_user(self, username, email=None, password=None, **extra_fields):
        client = self._assign_client_by_email(email)
        extra_fields.setdefault('client', client)
        
        return super().create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    date_birth = models.DateField(verbose_name="Date de naissance")
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_collected = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="users",
    )
    # En Django, REQUIRED_FIELDS ne sert que pour la commande createsuperuser dans le terminal.
    REQUIRED_FIELDS = ['date_birth']

    objects = CustomUserManager()
