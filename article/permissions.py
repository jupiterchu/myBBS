from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """自定义权限类"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif obj.author == request.user:
            return True
        return False
