from datetime import date
from rest_framework import serializers


class MinAgeValidator:
    def __init__(self, min_age):
        self.min_age = min_age

    def __call__(self, value):
        today = date.today()
        # on enlève 1 à la différence de date si la date d'anniversaire n'est pas passée
        ajustement = (today.month, today.day) < (value.month, value.day)
        age = today.year - value.year - ajustement
        
        if age < self.min_age:
            raise serializers.ValidationError(f"Vous devez avoir au moins {self.min_age} ans.")