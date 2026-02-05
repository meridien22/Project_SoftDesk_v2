from rest_framework.viewsets import (
    ReadOnlyModelViewSet,
    ModelViewSet,
)
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import (
    ValidationError,
)

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from support.models import (
    Project,
    Comment,
    Issue,
)
from support.serializers import (
    ProjectDetailSerializer,
    ProjectListSerializer,
    IssueAdminSerializer,
    CommentAdminSerializer,
    IssueSerializerResume,
    CommentSerializer,
)
from support.permissions import (
    IsAuthenticated,
    IsObjectAuthor,
    IsProjectContributor,
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
            author=user,
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
    permission_classes = [IsAuthenticated, IsObjectAuthor]

    def get_queryset(self):

        user = self.request.user
        queryset = Project.objects.filter(author=user)
        return queryset
    
    def perform_create(self, serializer):

        project = serializer.save(author=self.request.user)
        project.contributors.add(self.request.user)
    
    def perform_destroy(self, instance):

        instance.is_active = False
        instance.save()


class AdminIssueViewset(ModelViewSet):

    serializer_class = IssueAdminSerializer
    permission_classes = [IsAuthenticated, IsObjectAuthor]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def initial(self, request, *args, **kwargs):
        """Vérifie la présence de project selon l'action demandée."""
        super().initial(request, *args, **kwargs)

        if self.action == "list":
            if not request.query_params.get("project"):
                raise ValidationError({"detail": "Le paramètre d'URL 'project' est requis pour lister les issues."})
        
        elif self.action == "create":
            if 'project' not in request.data:
                raise ValidationError({"project": "Ce champ est obligatoire dans le corps de la requête."})

    def get_queryset(self):

        user = self.request.user
        # filtre de base, s'applique aux actions list, retrieve, create, update, partial_update er destroy
        queryset = Issue.objects.filter(
            author=user,
            project__is_active=True,
        )

        if self.action == "list":
            project_id = self.request.query_params.get('project')
            queryset = queryset.filter(project_id=project_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user, attribution=self.request.user)


class AdminCommentViewset(ModelViewSet):

    serializer_class = CommentAdminSerializer
    permission_classes = [IsAuthenticated, IsObjectAuthor]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def initial(self, request, *args, **kwargs):
        """Vérifie la présence de issue selon l'action demandée."""
        super().initial(request, *args, **kwargs)

        if self.action == "list":
            if not request.query_params.get("issue"):
                raise ValidationError({"detail": "Le paramètre d'URL 'issue' est requis pour lister les commentaires."})
        
        elif self.action == "create":
            if 'issue' not in request.data:
                raise ValidationError({"issue": "Ce champ est obligatoire dans le corps de la requête."})
            
    def get_queryset(self):

        user = self.request.user
        # filtre de base, s'applique aux actions list, retrieve, create, update, partial_update er destroy
        queryset = Comment.objects.filter(
            author=user,
            issue__project__is_active=True,
        )

        if self.action == "list":
            issue_id = self.request.query_params.get('issue')
            queryset = queryset.filter(issue_id=issue_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ProjectIssuesView(APIView):
    
    permission_classes = [IsAuthenticated, IsProjectContributor]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project)
        issues = Issue.objects.filter(project_id=project_id)
        serializer = IssueSerializerResume(issues, many=True)
        return Response(serializer.data)


class IssueCommentsView(APIView):

    permission_classes = [IsAuthenticated, IsProjectContributor]

    def get(self, request, issue_id):
        issue = get_object_or_404(Issue, id=issue_id)
        project = issue.project
        self.check_object_permissions(request, project)
        comments = Comment.objects.filter(issue_id=issue_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

