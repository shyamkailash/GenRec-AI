from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ExperimentDocumentViewSet,
    ExperimentViewSet,
)


router = DefaultRouter()

router.register(
    "experiments",
    ExperimentViewSet,
    basename="experiment",
)

router.register(
    "documents",
    ExperimentDocumentViewSet,
    basename="document",
)


urlpatterns = [
    path("", include(router.urls)),
]