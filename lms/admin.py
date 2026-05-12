from django.contrib import admin

from lms.models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "preview", "description", "owner")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "preview",
        "video_url",
        "description",
        "course",
        "owner",
    )
