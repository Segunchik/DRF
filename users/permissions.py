from rest_framework import permissions


class IsOwnProfile(permissions.BasePermission):
    """
    Разрешает доступ только к собственному профилю.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsModerator(permissions.BasePermission):
    """
    Разрешает доступ модераторам (с правами на просмотр всех пользователей).
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moderators").exists()

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
