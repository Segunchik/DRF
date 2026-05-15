from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from lms.models import Course, Lesson
from lms.validotors import VideoUrlValidator


class LessonSerializer(ModelSerializer):
    video_url = serializers.URLField(required=False, validators=[VideoUrlValidator()])

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(ModelSerializer):
    lesson_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = "__all__"

    # @staticmethod
    def get_lesson_count(self, instance):
        return instance.lesson.count()

    def get_is_subscribed(self, obj):
        """
        Определяет, подписан ли текущий пользователь на курс.
        Возвращает True/False.
        """
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(user=request.user, course=obj).exists()
