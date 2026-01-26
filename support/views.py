from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django.contrib.auth import get_user_model
from rest_framework import status

from support.models import Project
from support.serializers import (
    ProjectDetailSerializer,
    ProjectListSerializer,
    UserInputSerializer
)

UserModel = get_user_model()

class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()
    

class UserAPIView(APIView):

    def post(self, request):
        serializer = UserInputSerializer(data=request.data)

        if serializer.is_valid():
            UserModel.objects.create_user(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password'],
                date_birth=serializer.validated_data['date_birth']
            )
            return Response(
                {'message': f'Nouvel utilisateur créé.'},
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ProjectViewset(MultipleSerializerMixin, ReadOnlyModelViewSet):

    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer

    def get_queryset(self):
        queryset = Project.objects.all()
        type = self.request.GET.get("type")

        if type is not None:
            queryset = queryset.filter(type=type)

        return queryset

# class ProjectAPIView(APIView):

#     def get(self, *args, **kwargs):
#         projects = Project.objects.all()
#         serializer = ProjectSerializer(projects, many=True)
#         return Response(serializer.data)

# Accepte un paramètre type pour filtrer les projets suivant leurs types
class AdminProjectViewset(MultipleSerializerMixin, ModelViewSet):

    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer

    def get_queryset(self):
        queryset = Project.objects.all()
        type = self.request.GET.get("type")

        if type is not None:
            queryset = queryset.filter(type=type)

        return queryset