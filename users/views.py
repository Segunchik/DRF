from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from users.models import User, Payment
from users.serialisers import UserSerializer, PaymentSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PaymentListAPIView(generics.ListAPIView):
    """
    ViewSet для модели Payment с фильтрацией и сортировкой.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']
