from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from lms.models import Course, Lesson, Subscription
from lms.paginators import LessonPaginator, CoursePaginator
from lms.serialisers import CourseSerializer, LessonSerializer
from users.permissions import (
    IsModerator,
    IsOwnProfile,
    IsOwnerOrModerator,
    IsNotModeratorOrOwner,
)


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = (~IsModerator, IsAuthenticated)
        elif self.action in ["update", "retrieve"]:
            self.permission_classes = (IsModerator | IsOwnProfile, IsAuthenticated)
        elif self.action == "destroy":
            self.permission_classes = (IsOwnProfile, ~IsModerator, IsAuthenticated)
        return super().get_permissions()


class LessonCreateApiView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [
        ~IsModerator,
        IsAuthenticated,
    ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListApiView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsOwnProfile | IsModerator, IsAuthenticated]
    pagination_class = LessonPaginator


class LessonRetrieveApiView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [
        IsOwnerOrModerator,
        IsAuthenticated,
    ]


class LessonUpdateApiView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsOwnerOrModerator, IsAuthenticated)


class LessonDestroyApiView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsNotModeratorOrOwner, IsAuthenticated)


class SubscriptionAPIView(APIView):
    """
    Управление подписками на курс: создание/удаление подписки.
    POST-запрос:
    - Если подписка существует — удаляет её.
    - Если подписки нет — создаёт новую.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")

        # Валидация course_id
        if not course_id:
            return Response(
                {"error": 'Параметр "course_id" обязателен'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Получаем объект курса или возвращаем 404
            course_item = get_object_or_404(Course, id=course_id)
        except Exception:
            return Response(
                {"error": "Курс не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Пытаемся получить существующую подписку
            subscription = Subscription.objects.filter(
                user=user, course=course_item
            ).first()

            if subscription:
                # Подписка существует — удаляем
                subscription.delete()
                message = "Подписка удалена"
                status_code = status.HTTP_200_OK
            else:
                # Подписки нет — создаём новую
                Subscription.objects.create(user=user, course=course_item)
                message = "Подписка добавлена"
                status_code = status.HTTP_201_CREATED

            # Возвращаем ответ с информацией о подписке
            return Response(
                {
                    "message": message,
                    "course_id": course_id,
                    "is_subscribed": not subscription,  # True, если подписка создана; False, если удалена
                },
                status=status_code,
            )

        except Exception as e:
            return Response(
                {"error": "Произошла ошибка при обработке подписки"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
