from rest_framework.viewsets import (
    ReadOnlyModelViewSet,
    ModelViewSet,
)
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from support.models import (
    Project,
    Comment,
    Issue,
)
from support.serializers import (
    ProjectDetailSerializer,
    ProjectListSerializer,
    IssueAdminSerializer,
    CommentAdminSerializer
)
from support.permissions import (
    IsAuthenticated,
    IsStaff
)

from rest_framework.exceptions import (
    ValidationError,
    NotFound
)

UserModel = get_user_model()


class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()
    

class ProjectViewset(MultipleSerializerMixin, ReadOnlyModelViewSet):

    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user
        queryset = Project.objects.filter(
            author__client=user.client,
            contributors=user,
        ).distinct().prefetch_related(
            'contributors',
            'issues__comments',
            'issues__comments__author'
        )

        type = self.request.query_params.get('type')

        if type is not None:
            queryset = queryset.filter(type=type)

        return queryset


class AdminProjectViewset(ModelViewSet):
    
    serializer_class = ProjectListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user
        queryset = Project.objects.filter(author__client=user.client)
        return queryset
    
    def perform_create(self, serializer):

        project = serializer.save(author=self.request.user)
        project.contributors.add(self.request.user)
    
    def perform_destroy(self, instance):

        instance.is_active = False
        instance.save()


class AdminIssueViewset(ModelViewSet):

    serializer_class = IssueAdminSerializer
    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        """Vérifie la présence de project selon l'action demandée."""
        super().initial(request, *args, **kwargs)

        if self.action == "list":
            if not request.query_params.get("project"):
                raise ValidationError({
                    "detail": "Le paramètre d'URL 'project' est requis pour lister les issues."
                })
        elif self.action in ["create", "update", "partial_update", "retrieve"]:
            if 'project' not in request.data:
                raise ValidationError({
                    "project": "Ce champ est obligatoire dans le corps de la requête."
                })

    def get_queryset(self):

        user = self.request.user
        # filtre de base, s'applique aux actions list, retrieve, create, update, partial_update er destroy
        queryset = Issue.objects.filter(
            author=user,
            project__is_active=True,
        )

        project_id = (
                    self.request.query_params.get('project') or 
                    self.request.data.get('project')
        )
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class AdminCommentViewset(ModelViewSet):

    serializer_class = CommentAdminSerializer
    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        """Vérifie la présence de issue selon l'action demandée."""
        super().initial(request, *args, **kwargs)

        if self.action == "list":
            if not request.query_params.get("issue"):
                raise ValidationError({
                    "detail": "Le paramètre d'URL 'issue' est requis pour lister les commentaires."
                })
        elif self.action in ["create", "update", "partial_update", "retrieve"]:
            if 'issue' not in request.data:
                raise ValidationError({
                    "issue": "Ce champ est obligatoire dans le corps de la requête."
                })
            
    def get_queryset(self):

        user = self.request.user
        # filtre de base, s'applique aux actions list, retrieve, create, update, partial_update er destroy
        queryset = Comment.objects.filter(
            author=user,
            issue__project__is_active=True,
        )

        issue_id = (
                    self.request.query_params.get('issue') or 
                    self.request.data.get('issue')
        )
        if issue_id:
            queryset = queryset.filter(issue_id=issue_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)