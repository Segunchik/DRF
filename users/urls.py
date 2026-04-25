from django.urls import path
from rest_framework.routers import SimpleRouter

from users.apps import UsersConfig
from users.views import UserViewSet, PaymentListAPIView

app_name = UsersConfig.name

router = SimpleRouter()
router.register("", UserViewSet, basename="users")


urlpatterns = [path('payments/', PaymentListAPIView.as_view(), name='payments_list'),]
urlpatterns += router.urls
