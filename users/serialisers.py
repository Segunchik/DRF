from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User, Payment


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Расширенный сериализатор пользователя с историей платежей.
    """

    payments = PaymentSerializer(many=True, read_only=True)  # Вложенный сериализатор
    payments_count = serializers.SerializerMethodField()  # Количество платежей
    total_spent = serializers.SerializerMethodField()  # Общая сумма

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
            "date_joined",
            "payments_count",
            "total_spent",
            "payments",
        )
        read_only_fields = ("id", "date_joined")

    def get_payments_count(self, obj):
        """Получить количество платежей пользователя."""
        return obj.payments.count()

    def get_total_spent(self, obj):
        """Получить общую сумму потраченных денег."""
        total = sum(payment.amount for payment in obj.payments.all())
        return float(total)


class UserSerializer(ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = "__all__"
