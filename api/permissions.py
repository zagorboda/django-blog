from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission to only allow owner of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to allow owner of an object to edit it, and all users to retrieve it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user


class IsSelfUserOrReadOnly(permissions.BasePermission):
    """
    Permission to allow owner of an user profile to edit it, and all users to retrieve it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj == request.user


class IsOwnerOrIsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Permission to allow owner of an object to edit it, authenticated users to make POST request and all user to retrieve it.
    """

    def has_object_permission(self, request, view, obj):

        if request.method == 'PATCH' and obj.author == request.user and request.user.is_authenticated:
            return True

        if request.method == 'POST' and request.user.is_authenticated:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        return False
