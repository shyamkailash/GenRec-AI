from django.urls import path

from .views import (
    ContentGenerationAPIView,
    DocumentGenerationAPIView,
    ExperimentPlanningAPIView,
    PlannerAPIView,
    RetrievalAPIView,
    ValidationAPIView,
)

app_name = "agents"

urlpatterns = [
    path(
        "plan/",
        PlannerAPIView.as_view(),
        name="plan",
    ),
    path(
        "experiment-plan/",
        ExperimentPlanningAPIView.as_view(),
        name="experiment-plan",
    ),
    path(
        "retrieve/",
        RetrievalAPIView.as_view(),
        name="retrieve",
    ),
    path(
        "generate-content/",
        ContentGenerationAPIView.as_view(),
        name="generate-content",
    ),
    path(
        "validate/",
        ValidationAPIView.as_view(),
        name="validate",
    ),
    path(
        "generate-document/",
        DocumentGenerationAPIView.as_view(),
        name="generate-document",
    ),
]

