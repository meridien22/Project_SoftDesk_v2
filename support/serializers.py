from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from support.models import Project, Issue, Comment
from authentication.models import User

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserModel
        fields = [
            'id',
            'username',
        ]


class CommentSerializer(serializers.ModelSerializer):
    
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "description",
            "time_created",
            "author"
        ]


class IssueSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)
    attribution = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = [
            "id",
            "name",
            "description",
            "priority",
            "attribution",
            "author",
            "balise",
            "progression",
            "time_created",
            "comments",
        ]


class IssueAdminSerializer(serializers.ModelSerializer):


    class Meta:
        model = Issue
        fields = [
            "id",
            "name",
            "description",
            "priority",
            "attribution",
            "author",
            "balise",
            "progression",
            "project",
        ]
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Issue.objects.all(),
                fields=['name', 'project'],
                message="Un problème avec ce nom existe déjà dans ce projet."
            )
        ]

    def raise_if_not_contributor(self, instance, user_id):
        # On est en modification (PUT ou PATCH), self.instance existe et contient l'issue
        
        if instance is not None:
            project = instance.project
        else:
            request = self.context.get('request')
            project_id = request.query_params.get('project_id')
            project = Project.objects.filter(id=project_id).first()

        if project is not None:
            if not project.contributors.filter(id=user_id).exists():
                raise serializers.ValidationError("L'utilisateur n'est pas contributeur")
        else:
            raise serializers.ValidationError("Le projet est invalide.")

    def validate_author(self, value):
        # value contien déjà l'objet user qui a été initialisé par le framework
        self.raise_if_not_contributor(self.instance, value.id)
        return value
    
    def validate_attribution(self, value):
        # value contien déjà l'objet user qui a été initialisé par le framework
        self.raise_if_not_contributor(self.instance, value.id)
        return value
    
    def validate_project(self, value):
        client = self.context['request'].user.client
        is_valid = Project.objects.filter(
            # le projet doit exister
            id=value.id,
            # il doit être un des projets du clients
            author__client=client,
            # l'utilisateur doit être contributeur du projet
            contributors=self.context['request'].user,
        ).exists()
        if not is_valid:
            raise serializers.ValidationError("Référence inconnue")

        return value
    
    def validate(self, data):

        if 'project' not in data or (data.get("project") == "" or data.get("project")  is None):
            raise serializers.ValidationError({"name": "Ce champ est obligatoire."})
    
    

class ProjectListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "type",
        ]

    # Pour un même client, un projet ne peut pas avoir 2 fois le même nom
    def validate_name(self, value):
        user = self.context['request'].user
        if Project.objects.filter(name=value, author__client=user.client).exists():
            raise serializers.ValidationError('Le projet existe déjà')
        return value


class ProjectDetailSerializer(serializers.ModelSerializer):

    issues = IssueSerializer(many=True)
    author = UserSerializer(read_only=True)
    contributors = UserSerializer(many=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "type",
            "time_created",
            "author",
            "contributors",
            "issues"
        ]
