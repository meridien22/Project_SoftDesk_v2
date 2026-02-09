from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
)

from django.contrib.auth import get_user_model

from django.shortcuts import get_object_or_404

from support.permissions import (
    IsStaff, 
    IsMe,
    IsAuthenticated,
    IsObjectAuthor,
    IsSuperUser,
)
from authentication.serializers import (
    UserInputSerializer,
    ChangeProjectAuthorSerializer,
    AddProjectContributorSerializer,
    DeleteProjectContributorSerializer,
    ChangeIssuetAttributionSerializer,
    UserUpdateSerializer,
    ChangeIssueAuthorSerializer,
    ChangeCommentAuthorSerializer,
    UpgradeUserSerializer,
)

from support.models import Project, Issue, ProjectContributors, Comment

UserModel = get_user_model()


class UserInscriptionView(APIView):

    def post(self, request):
        serializer = UserInputSerializer(data=request.data)
        if serializer.is_valid():
            # .save() appelle automatiquement la méthode create qui a été surcharhée
            user = serializer.save() 

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateView(APIView):
    
    permission_classes = [IsAuthenticated, IsMe]

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
    

class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsStaff]

    def delete(self, request, user_id):
        user = get_object_or_404(UserModel.objects, id=user_id)

        remaining_comment = Comment.objects.filter(author=user).exists()
        if remaining_comment:
            raise ValidationError({"detail": "Cet utilisateur est encore auteur d'au moins un commentaire."})

        remaining_issue_author = Issue.objects.filter(author=user).exists()
        if remaining_issue_author:
            raise ValidationError({"detail": "Cet utilisateur est encore auteur d'au moins un problème."})
        
        remaining_issue_attribution = Issue.objects.filter(attribution=user).exists()
        if remaining_issue_attribution:
            raise ValidationError({"detail": "Cet utilisateur est encore en charge d'au moins un problème."})
        
        remaining_project_author = Project.objects.filter(author=user).exists()
        if remaining_project_author:
            raise ValidationError({"detail": "Cet utilisateur est encore auteur d'au moins un projet."})
        
        remaining_project_contributor = ProjectContributors.objects.filter(contributor_id=user.id).exists()
        if remaining_project_contributor:
            raise ValidationError({"detail": "Cet utilisateur est encore contributeur d'au moins un projet."})
        
        user.delete()

        return Response(
                {"detail": "Utilisateur supprimé."},
                status=status.HTTP_200_OK
        )


class ProjectChangeAuthorView(APIView):
    
    permission_classes = [IsAuthenticated, IsObjectAuthor]

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

            is_contributor = ProjectContributors.objects.filter(
                project=project, 
                contributor=request.user
            ).exists()
            # si le nouvel auteur n'est pas contributeur du projet, on l'ajoute aux contributeurs
            if not is_contributor:
                project.contributors.add(request.user)

            return Response(
                {"detail": f"Propriété transférée avec succès à {project.author.username}"},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class IssueChangeAuthorView(APIView):

    permission_classes = [IsAuthenticated, IsObjectAuthor]

    def patch(self, request, issue_id):

        issue = get_object_or_404(Issue.objects, id=issue_id)
        # il faut appeler check_object_permissions manuellement car on a fait un
        # get_object_or_404 et pas un get_object
        self.check_object_permissions(request, issue)
        serializer = ChangeIssueAuthorSerializer(
            issue,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": f"Propriété transférée avec succès à {issue.author.username}"},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CommentChangeAuthorView(APIView):

    permission_classes = [IsAuthenticated, IsObjectAuthor]

    def patch(self, request, comment_id):

        comment = get_object_or_404(Comment.objects, id=comment_id)
        serializer = ChangeCommentAuthorSerializer(
            comment,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": f"Propriété transférée avec succès à {comment.author.username}"},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectAddContributorView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        
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

    permission_classes = [IsAuthenticated, IsObjectAuthor]

    def delete(self, request):
        
        serializer = DeleteProjectContributorSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            ProjectContributors.objects.filter(
                project_id=serializer.validated_data['project'],
                contributor_id=serializer.validated_data['contributor'],
            ).delete()

            return Response(
                {"detail": f"Contributeur supprimé avec succés."},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class IssueChangeAttributionView(APIView):
    
    permission_classes = [IsAuthenticated, IsObjectAuthor]

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


class UserUpgradeView(APIView):

    permission_classes = [IsAuthenticated, IsSuperUser]

    def patch(self, request, user_id):
        user = get_object_or_404(UserModel.objects, id=user_id)
        serializer = UpgradeUserSerializer(
            user,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": f"L'utilisateur {user.username} fait maintenant partie du staff"},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)