from django.urls import include, path
from rest_framework.routers import DefaultRouter

from board_app.api.views import BoardViewSet

router = DefaultRouter()
router.register(r"boards", BoardViewSet, basename="board")

urlpatterns = [
    path("", include(router.urls)),
]
