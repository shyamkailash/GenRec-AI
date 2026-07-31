from django.urls import path

from .views import (
    ExperimentPlanningAPIView,
    PlannerAPIView,
    RetrievalAPIView,
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
]
