from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated)
    

class IsStaff(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.is_staff)
    

class IsMe(BasePermission):

    def has_permission(self, request, view):
        user_id = view.kwargs.get('user_id')
        return str(request.user.id) == str(user_id)
    

class IsObjectAuthor(BasePermission):
# La méthode has_object_permission n'est appelée que pour les actions 
# qui concernent un seul objet (retrieve, update, partial_update, destroy).

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
    

class IsProjectContributor(BasePermission):


    def has_object_permission(self, request, view, obj):
        return obj.contributors.filter(id=request.user.id).exists()
        # on aurait pu aussi passer par la table de liaison
        # return obj.contributor_links.filter(contributor_id=request.user.id).exists():