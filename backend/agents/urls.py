"""URL routes for the agents application."""

from django.urls import path

from .views import PlannerAPIView


app_name = "agents"

urlpatterns = [
    path("plan/", PlannerAPIView.as_view(), name="plan"),
]
