from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend


from users.models import User, Payment
from users.permissions import IsOwnProfile, IsModerator
from users.serialisers import UserSerializer, PaymentSerializer, UserProfileSerializer


class UserViewSet(ModelViewSet):
    """
    ViewSet для модели User с регистрацией и гибкой авторизацией.
    """

    # Загружаем только нужные поля
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        """
        Используем расширенный сериализатор для retrieve.
        """
        if self.action == "retrieve":
            return UserProfileSerializer
        return UserSerializer

    def get_permissions(self):
        """
        Разные права для разных действий.
        """
        if self.action == "create":
            # Регистрация доступна всем
            return [AllowAny()]
        elif self.action in ["update", "partial_update", "destroy"]:
            # Редактировать/удалять может только владелец профиля
            return [IsOwnProfile()]
        elif self.action == "retrieve":
            # Просматривать свой профиль может любой авторизованный
            return [IsAuthenticated(), IsOwnProfile()]
        elif self.action == "list":
            # Список пользователей только для модераторов
            return [IsModerator()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Динамическая фильтрация queryset в зависимости от действия.
        """
        user = self.request.user

        if self.action == "list" and user.has_perm("users.view_all_users"):
            # Модераторы видят всех пользователей
            return self.queryset
        elif user.is_authenticated:
            # Обычные пользователи видят только себя
            return self.queryset.filter(id=user.id)
        else:
            return self.queryset.none()

    def get_object(self):
        """
        Возвращает объект пользователя для операций update/destroy/retrieve.
        Гарантирует, что пользователь работает только со своим профилем.
        """
        user_id = self.kwargs.get("pk")
        user = self.request.user

        # Если запрашивается не свой профиль — проверяем права
        if str(user.id) != user_id:
            if not user.has_perm("users.change_other_users"):
                raise PermissionDenied("У вас нет прав для доступа к этому профилю")

        return get_object_or_404(self.get_queryset(), id=user_id)

    def _handle_password(self, user, password):
        """
        Вспомогательный метод для хеширования пароля.
        Вынесен для устранения дублирования кода.
        """
        if password:
            user.set_password(password)
            user.save()

    def perform_create(self, serializer):
        """
        Регистрация нового пользователя с хешированием пароля.
        """
        password = self.request.data.get("password")
        try:
            user = serializer.save()
            self._handle_password(user, password)
        except Exception as e:
            raise ValidationError(f"Ошибка при создании пользователя: {str(e)}")

    def perform_update(self, serializer):
        """
        Обновление пользователя с хешированием пароля (если передан).
        """
        password = self.request.data.get("password")
        try:
            user = serializer.save()
            self._handle_password(user, password)
        except Exception as e:
            raise ValidationError(f"Ошибка при обновлении пользователя: {str(e)}")


class PaymentListAPIView(generics.ListAPIView):
    """
    ViewSet для модели Payment с фильтрацией и сортировкой.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["paid_course", "paid_lesson", "payment_method"]
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]
