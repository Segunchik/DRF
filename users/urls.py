from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# from .views import MyTokenObtainPairView

from users.apps import UsersConfig
from users.views import UserViewSet, PaymentViewSet  # UserCreateAPIView

app_name = UsersConfig.name

router = SimpleRouter()
router.register("", UserViewSet, basename="users")
router1 = SimpleRouter()
router1.register("", PaymentViewSet, basename="payments")


urlpatterns = [
    #    path("payments/", PaymentViewSet.as_view(), name="payments_list"),
    path(
        "login/",
        TokenObtainPairView.as_view(permission_classes=(AllowAny,)),
        name="login",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(permission_classes=(AllowAny,)),
        name="token_obtain_pair",
    ),
]
urlpatterns += router.urls
urlpatterns += router1.urls
