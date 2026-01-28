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
    IssueSerializer,
)
from support.permissions import (
    IsAuthenticated,
    IsStaff
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
            author__client=user.client
        ).prefetch_related(
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

    serializer_class = IssueSerializer
    permission_classes = [IsStaff]

    def get_queryset(self):

        user = self.request.user
        queryset = Comment.objects.filter(
            author__client=user.client,
            project_id=self.request.query_params.get('project_id')
        )
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Permet de rendre obligatoire la paramètre project_id dans l'URL"""

        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response(
                {"detail": "Le paramètre 'project_id' est obligatoire pour lister les problèmes."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().list(request, *args, **kwargs)