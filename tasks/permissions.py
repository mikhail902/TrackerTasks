from rest_framework.permissions import BasePermission


class IsAdminOrManager(BasePermission):
    """Администратор или руководитель"""

    def has_permission(self, request, view):
        return request.user.role in ['admin', 'manager']


class IsAdmin(BasePermission):
    """Только администратор"""

    def has_permission(self, request, view):
        return request.user.role == 'admin'

class IsCreatorOrAssignee(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user or obj.assignee == request.user or request.user.role == 'admin'