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


# class ProjectAPIView(APIView):

#     def post(self, *args, **kwargs):
#         serializer = ProjectListSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(author=request.user)
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)


class AdminProjectViewset(ModelViewSet):
    
    serializer_class = ProjectListSerializer
    permission_classes = [IsStaff]

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
    permission_classes = [IsStaff]

    def get_queryset(self):

        raise_project_id = False
        # si on est dans une action 'list' le project_id doit être dans l'URL
        if self.action == 'list':
            if not self.request.query_params.get('project_id'):
                raise_project_id = True
        # sinon il doit être dans les data
        else:
            if 'project_id' not in self.request.data:
                raise_project_id = True

        if raise_project_id:
            raise ValidationError({"detail": "Le paramètre d'URL 'project_id' est obligatoire."})
        



        user = self.request.user
        # filtre de base, s'applique aux actions list, retrieve, create, update, partial_update er destroy
        queryset = Issue.objects.filter(
            author__client=user.client,
            project__is_active=True,
        )

        # filtre qui ne va s'appliquer que sur l'action list
        if self.action == 'list':
            project_id = self.request.query_params.get('project_id')
            queryset = queryset.filter(project_id=project_id)
            if not queryset.exists():
                raise NotFound({"detail": "Impossible de trouver le projet demandé."})
        
        return queryset
    
    def raise_if_no_projecy_id(self, request):
        """Lève une exception si le paramètre project_id n'est pas présent dans l'URL"""
        if not request.query_params.get('project_id'):
            raise ValidationError({"detail": "Le paramètre d'URL 'project_id' est obligatoire."})

    
    # def list(self, request, *args, **kwargs):
    #     """methode HTTP GET"""
    #     self.raise_if_no_projecy_id(request)
    #     return super().list(request, *args, **kwargs)
    
    # def create(self, request, *args, **kwargs):
    #     """methode HTTP POST"""
    #     self.raise_if_no_projecy_id(request)
    #     return super().create(request, *args, **kwargs)
