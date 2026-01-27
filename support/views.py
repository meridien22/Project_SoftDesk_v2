from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet,
)

from django.contrib.auth import get_user_model


from support.models import Project

from support.serializers import (
    ProjectDetailSerializer,
    ProjectListSerializer,
)

from support.permissions import (
    IsAuthenticated
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
        queryset = Project.objects.filter(author__client=user.client)
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