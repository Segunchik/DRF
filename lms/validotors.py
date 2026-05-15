import re
from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _


class VideoUrlValidator:
    """
    Валидатор для проверки, что ссылка ведёт на YouTube.
    Разрешённые форматы:
    - https://www.youtube.com/watch?v=...
    - https://youtu.be/...
    - https://www.youtube.com/embed/...
    """

    YOUTUBE_PATTERNS = [
        r'^(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?v=|embed/|v/|shorts/)|youtu\.be/)[\w=-]{11}(?:\?[\w=&-]*)?$',
    ]

    def __call__(self, value):
        """
        Вызываемый метод для валидации.
        :param value: строка с URL
        :raises ValidationError: если ссылка не YouTube или некорректна
        """
        if not value:  # Пропускаем пустые значения
            return

        # Проверяем, соответствует ли URL хотя бы одному YouTube‑паттерну
        if not any(re.match(pattern, value) for pattern in self.YOUTUBE_PATTERNS):
            raise ValidationError('Разрешены только ссылки на YouTube (youtube.com или youtu.be)')
