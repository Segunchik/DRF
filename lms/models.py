from django.contrib.auth.models import AbstractUser
from django.db import models


class Course(models.Model):
    """Модель курса"""

    title = models.CharField(max_length=100, verbose_name="Название")
    preview = models.ImageField(
        upload_to="course/preview/", verbose_name="Превью", blank=True, null=True
    )
    description = models.TextField(verbose_name="Описание курса", blank=True, null=True)

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = [
            "title",
        ]

    def __str__(self):
        return f"Курс: {self.title}"


class Lesson(models.Model):
    """Модель урока"""

    title = models.CharField(max_length=100, verbose_name="Урок")
    description = models.TextField(verbose_name="Описание курса", blank=True, null=True)
    preview = models.ImageField(
        upload_to="lesson/preview/", verbose_name="Превью", blank=True, null=True
    )
    video_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на видео")
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lesson", verbose_name="Курс"
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return f"{self.course.title} - {self.title}"
