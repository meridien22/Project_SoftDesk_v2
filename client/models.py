from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=2048, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
