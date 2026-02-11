from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from authentication.models import User
from support.models import Project, ProjectContributors, Issue, Comment
from authentication.validators import MinAgeValidator

from client.models import Client

from datetime import date

UserModel = get_user_model()


class UserInputSerializer(serializers.ModelSerializer):
    # Avec ModelSerializer, le check "username unique" est ajouté automatiquement par
    # Django REST Framework car il lit les contraintes du modèle.

    date_birth = serializers.DateField(validators=[MinAgeValidator(15)])

    class Meta:

        model = UserModel
        fields = [
            "id",
            "username",
            "password",
            "date_birth",
            "can_be_contacted",
            "can_data_be_collected",
            "can_data_be_shared",
            "email",

        ]
        extra_kwargs = {
            # En sortie (Lecture) : Lorsque l'API renvoie les informations de
            # l'utilisateur (en format JSON), le champ password est totalement exclu
            # Sans ce paramètre, si vous créez un utilisateur et que l'API répond
            # avec les données créées, elle pourrait inclure le mot de passe
            # (ou son empreinte hachée) dans le JSON de réponse.
            'password': {'write_only': True}
        }


    def validate_email(self, value):
        domain = value.split('@')[-1].lower()
        if not Client.objects.filter(domain=domain).exists():
            raise serializers.ValidationError("Domaine non autorisé.")
        return value
    
    def create(self, validated_data):
            # On appelle explicitement create_user du manager
            return UserModel.objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):

    date_birth = serializers.DateField(validators=[MinAgeValidator(15)])
    # cela permet de transmettre le client pour que l'on puisse faire le contrôle
    # d'unicité du username mais sans laisser la possibilité de la modifier
    client = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:

        model = UserModel
        fields = [
            "username",
            "date_birth",
            "can_be_contacted",
            "can_data_be_collected",
            "can_data_be_shared",
            "client",
        ]
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=UserModel.objects.all(),
                fields=['username', 'client'],
                message="Un utilisateur avec ce nom existe déjà."
            )
        ]


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


class ChangeIssueAuthorSerializer(serializers.ModelSerializer):

    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.none())


    class Meta:
        model = Issue
        fields = ['author']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        issue = self.instance
        project = issue.project
        self.fields['author'].queryset = project.contributors.all()


class ChangeCommentAuthorSerializer(serializers.ModelSerializer):

    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.none())


    class Meta:
        model = Comment
        fields = ['author']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        comment = self.instance
        project = comment.issue.project
        self.fields['author'].queryset = project.contributors.all()


class AddProjectContributorSerializer(serializers.ModelSerializer):


    class Meta:
        model = ProjectContributors
        fields = ["contributor", "project"]


    def validate(self, data):

        request = self.context.get('request')

        if not request:
            raise serializers.ValidationError("Object request manquant.")
        else:
            project_id = request.data.get('project')
            contributor_id = request.data.get('contributor')
            user = request.user

        # Le projet doit exister dans les projets du client
        existing_project = Project.objects.filter(
            author__client=user.client,
            id=project_id,
        ).exists()
        if not existing_project :
            raise serializers.ValidationError("Référence projet incorrecte.")
        
        # L'utilisateur doit être auteur du projet ou membre du staff
        is_author = Project.objects.filter(
            id=project_id,
            author=user,
        ).exists()
        if not is_author and not user.is_staff:
            raise serializers.ValidationError("L'utilisateur n'est pas auteur du projet.")
            
        # Le contributeur ne doit pas déjà être contributeur du projet
        existing_contributor = ProjectContributors.objects.filter(
            contributor_id=contributor_id,
            project_id=project_id,
        ).exists()
        if existing_contributor :
            raise serializers.ValidationError("Contributeur déjà associé au projet.")

        # Le contributeur doit être un utilisateur du client
        existing_user = User.objects.filter(
            client=user.client,
            id=contributor_id,
        ).exists()
        if not existing_user :
            raise serializers.ValidationError("Référence contributeur incorrecte.")
        
        return data
    

class DeleteProjectContributorSerializer(serializers.ModelSerializer):


    class Meta:
        model = ProjectContributors
        fields = ["contributor", "project"]

    
    def validate(self, data):

        request = self.context.get('request')

        if not request:
            raise serializers.ValidationError("Object request manquant.")
        else:
            project_id = request.data.get('project')
            contributor_id = request.data.get('contributor')
            user = request.user

        # Le projet doit exister dans les projets du client
        existing_project = Project.objects.filter(
            author__client=user.client,
            id=project_id,
        ).exists()
        if not existing_project :
            raise serializers.ValidationError("Référence projet incorrecte.")
            
        # Le contributeur ne doit pas être le dernier contributeur
        number_contributor = ProjectContributors.objects.filter(
            project_id=project_id,
        ).count()
        if number_contributor <= 1 :
            raise serializers.ValidationError("Impossible de supprimer le dernier contributeur.")
        
        # Le contributeur doit être contributeur du projet
        existing_contributor = ProjectContributors.objects.filter(
            contributor_id=contributor_id,
            project_id=project_id,
        ).exists()
        if not existing_contributor :
            raise serializers.ValidationError("Contributeur non associé au projet.")
        
        return data
    

class ChangeIssuetAttributionSerializer(serializers.ModelSerializer):

    attribution = serializers.PrimaryKeyRelatedField(queryset=User.objects.none())


    class Meta:
        model = Project
        fields = ['attribution']

    def validate(self, data):

        request = self.context.get('request')

        if not request:
            raise serializers.ValidationError("Object request manquant.")
        else:
            project = self.instance
            attribution_id = request.data.get('attribution')
        
        # L'utilisateur a qui est attribué le projet doit être contributeur du projet
        existing_contributor = ProjectContributors.objects.filter(
            contributor_id=attribution_id,
            project_id=project.id,
        ).exists()
        if not existing_contributor :
            raise serializers.ValidationError("Utilisateur attribué non associé au projet.")


class UpgradeUserSerializer(serializers.ModelSerializer):


    class Meta:
        model = UserModel
        fields = ['is_staff']
