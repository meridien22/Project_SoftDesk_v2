from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import get_user_model

from django.shortcuts import get_object_or_404

from authentication.permissions import IsSuperUser
from authentication.serializers import (
    UserInputSerializer,
)

from support.models import Project

from authentication.serializers import ChangeProjectAuthorSerializer

UserModel = get_user_model()


class UserAPIView(APIView):

    permission_classes = [IsSuperUser]

    def post(self, request):
        serializer = UserInputSerializer(data=request.data)
        if serializer.is_valid():
            # .save() appelle automatiquement la méthode create qui a été surcharhée
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectChangeAuthorView (APIView):
    
    permission_classes = [IsSuperUser]

    def patch(self, request, project_id):

        project = get_object_or_404(Project.objects, id=project_id)
        serializer = ChangeProjectAuthorSerializer(
            project,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": f"Propriété transférée avec succès à {project.author.username}"},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)