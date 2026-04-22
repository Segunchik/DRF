from django.urls import path
from rest_framework.routers import SimpleRouter

from users.apps import UsersConfig
from users.views import UserViewSet

app_name = UsersConfig.name

router = SimpleRouter()
router.register("", UserViewSet, basename="users")

urlpatterns = []
urlpatterns += router.urls
