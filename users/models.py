from django.contrib.auth.models import AbstractUser
from django.db import models

from lms.models import Course, Lesson


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")

    avatar = models.ImageField(
        upload_to="users/avatars/",
        verbose_name="Аватар",
        blank=True,
        null=True,
        help_text="Загрузите аватар",
    )
    phone = models.CharField(
        max_length=15,
        verbose_name="Телефон",
        help_text="Введите номер телефона",
        blank=True,
        null=True,
    )
    country = models.CharField(
        max_length=15,
        verbose_name="Страна",
        help_text="Введите свою страну",
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Payment(models.Model):
    """Модель платежа"""
    PAY_METHOD = [("cash","Наличные"),("transfer","Перевод на счет")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment", verbose_name="Пользователь")
    pay_date = models.DateTimeField(auto_now=True, verbose_name="Дата оплаты")
    paid_course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Оплаченный курс")
    paid_lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Оплаченный урок")
    payment_amount = models.DecimalField(verbose_name="Сумма оплаты",max_digits=10, decimal_places=2)
    payment_method = models.CharField(verbose_name="Способ оплаты", max_length=10, choices=PAY_METHOD, default="transfer")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"


    def __str__(self):
        return f'{self.user} - {self.payment_amount}'