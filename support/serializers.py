from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from support.models import Project, Issue, Comment

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

