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


class IssueSerializerResume(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)
    attribution = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

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
            "comments_count",
        ]

    def get_comments_count(self, obj):
            # 'obj' est l'instance de l'Issue en cours de traitement
            return obj.comments.count()


class CommentAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = [
            "id",
            "description",
            "issue",
        ]

    def validate_issue(self, value):
        client = self.context['request'].user.client
        is_valid = Issue.objects.filter(
            # le problème doit exister
            id=value.id,
            # il doit être un des projets du clients
            project__author__client=client,
            # l'utilisateur doit être contributeur du projet
            project__contributors=self.context['request'].user,
        ).exists()
        if not is_valid:
            raise serializers.ValidationError("Référence inconnue")

        return value   


class IssueAdminSerializer(serializers.ModelSerializer):


    class Meta:
        model = Issue
        fields = [
            "id",
            "name",
            "description",
            "priority",
            "balise",
            "progression",
            "project",
            "attribution",
        ]


    def validate_project(self, value):
        # On interdit ici qu'un PATCH change l'auteur de l'issue
        if self.instance and self.instance.project != value:
            raise serializers.ValidationError("Le changement de projet est interdit.")
        # S'il n'y a pas d'instance il s'agit d'un POST
        else:
            user = self.context['request'].user
            is_valid = Project.objects.filter(
                # le projet doit exister
                id=value.id,
                # il doit être un des projets du clients
                author__client=user.client,
                # l'utilisateur doit être contributeur du projet
                contributors=user,
            ).exists()
            if not is_valid:
                raise serializers.ValidationError("Référence inconnue")

        return value 
    

class ProjectListSerializer(serializers.ModelSerializer):

    issues_count = serializers.IntegerField(source='total_issues', read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "type",
            "issues_count",
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
