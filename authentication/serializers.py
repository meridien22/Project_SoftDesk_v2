from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth import get_user_model
from authentication.models import User
from support.models import Project

UserModel = get_user_model()


class UserInputSerializer(serializers.ModelSerializer):
    # Avec ModelSerializer, le check "username unique" est ajouté automatiquement par
    # Django REST Framework car il lit les contraintes du modèle.


    class Meta:
        model = UserModel
        fields = ['username', 'password', 'date_birth', 'client']
        extra_kwargs = {
            # En sortie (Lecture) : Lorsque l'API renvoie les informations de
            # l'utilisateur (en format JSON), le champ password est totalement exclu
            # Sans ce paramètre, si vous créez un utilisateur et que l'API répond
            # avec les données créées, elle pourrait inclure le mot de passe
            # (ou son empreinte hachée) dans le JSON de réponse.
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # utiliser create_user au lieu de create permet de hacher le mot de passe
        return User.objects.create_user(**validated_data)
    

class ChangeProjectAuthorSerializer(serializers.ModelSerializer):

    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.none())


    class Meta:
        model = Project
        fields = ['author']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user:
            self.fields['author'].queryset = User.objects.filter(
                client=request.user.client
            )