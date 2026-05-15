from rest_framework import permissions


class IsOwnerOrModerator(permissions.BasePermission):
    """
    Разрешает доступ владельцу объекта ИЛИ модератору (staff).
    """

    def has_object_permission(self, request, view, obj):
        # Владелец объекта (поле owner)
        if hasattr(obj, "owner") and obj.owner == request.user:
            return True
        # Модератор
        if request.user.groups.filter(name="moderators").exists():
            return True
        return False


class IsNotModeratorOrOwner(permissions.BasePermission):
    """
    Разрешает доступ:
    - владельцу объекта (поле owner)
    - ИЛИ пользователям, которые НЕ являются модераторами (не в группе 'moderators')
    """

    def has_object_permission(self, request, view, obj):
        # Владелец объекта имеет доступ
        if hasattr(obj, "owner") and obj.owner == request.user:
            return True

        # Пользователи, не являющиеся модераторами, имеют доступ
        if not request.user.groups.filter(name="moderators").exists():
            return True

        return False


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
