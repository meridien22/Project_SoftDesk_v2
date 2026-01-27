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

    # Pour un même client, un projet ne peut pas avoir 2 fois le même nom
    def validate_name(self, value):
        user = self.context['request'].user
        if Project.objects.filter(name=value, author__client=user.client).exists():
            raise serializers.ValidationError('Projet already exists')
        return value


class ProjectDetailSerializer(serializers.ModelSerializer):

    issues = IssueSerializer(many=True)

    class Meta:
        model = Project
        fields = ["id", "name", "description", "type", "issues"]
