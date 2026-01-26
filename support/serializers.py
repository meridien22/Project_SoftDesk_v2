from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from support.models import Project, Issue, Comment

UserModel = get_user_model()


class IssueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Issue
        fields = ["id", "name", "priority"]


class ProjectListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ["id", "name", "description", "type"]

    def validate_name(self, value):
        if Project.objects.filter(name=value).exists():
            raise serializers.ValidationError('Projet already exists')
        return value


class ProjectDetailSerializer(serializers.ModelSerializer):

    issues = IssueSerializer(many=True)

    class Meta:
        model = Project
        fields = ["id", "name", "description", "type", "issues"]


class UserInputSerializer(serializers.ModelSerializer):
    # Avec ModelSerializer, le check "username unique" est ajouté automatiquement par
    # Django REST Framework car il lit les contraintes du modèle.


    class Meta:
        model = UserModel
        fields = ['username', 'password', 'date_birth']
        extra_kwargs = {
            # En sortie (Lecture) : Lorsque l'API renvoie les informations de
            # l'utilisateur (en format JSON), le champ password est totalement exclu
            # Sans ce paramètre, si vous créez un utilisateur et que l'API répond
            # avec les données créées, elle pourrait inclure le mot de passe
            # (ou son empreinte hachée) dans le JSON de réponse.
            'password': {'write_only': True}
        }

    # En DRF, si vous créez une méthode validate_<field_name>, elle est automatiquement
    # exécutée lors de l'appel à is_valid()
    def validate_password(self, value):
        validate_password(value)
        return value