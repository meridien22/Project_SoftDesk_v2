from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import get_user_model

from django.shortcuts import get_object_or_404

from support.permissions import (
    IsStaff, 
    IsMe,
)
from authentication.serializers import (
    UserInputSerializer,
    ChangeProjectAuthorSerializer,
    AddProjectContributorSerializer,
    DeleteProjectContributorSerializer,
    ChangeIssuetAttributionSerializer,
    UserUpdateSerializer,
)

from support.models import Project, Issue

UserModel = get_user_model()


class UserInscriptionView(APIView):

    def post(self, request):
        serializer = UserInputSerializer(data=request.data)
        if serializer.is_valid():
            # .save() appelle automatiquement la méthode create qui a été surcharhée
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateView(APIView):
    
    permission_classes = [IsMe]

    def patch(self, request, user_id):

        user = get_object_or_404(UserModel.objects, id=user_id)
        serializer = UserUpdateSerializer(
            user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": f"Utilisateur modifié."},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectChangeAuthorView(APIView):
    
    permission_classes = [IsStaff]

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


class ProjectAddContributorView(APIView):

    permission_classes = [IsStaff]

    def post(self, request, project_id):
        
        serializer = AddProjectContributorSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": f"Contributeur ajouté avec succés."},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProjectDeleteContributorView(APIView):

    permission_classes = [IsStaff]

    def delete(self, request, project_id):
        
        serializer = DeleteProjectContributorSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": f"Contributeur supprimé avec succés."},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class IssueChangeAuthorView(APIView):
    
    permission_classes = [IsStaff]

    def patch(self, request, issue_id):

        issue = get_object_or_404(Issue.objects, id=issue_id)
        serializer = ChangeIssuetAttributionSerializer(
            issue,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": f"Atttribution transférée avec succès à {issue.attribution.username}"},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)