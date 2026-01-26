from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    date_birth = models.DateField(verbose_name="Date de naissance")
    can_be_contacted = models.BooleanField(null=True)
    can_data_be_collected = models.BooleanField(null=True)
    can_data_be_shared = models.BooleanField(null=True)
    REQUIRED_FIELDS = ['date_birth']