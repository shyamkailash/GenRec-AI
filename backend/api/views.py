from django.http import JsonResponse
from rest_framework import viewsets

from experiments.models import Experiment

from .serializers import ExperimentSerializer


def home(request):
    return JsonResponse(
        {
            "project": "GenRec-AI",
            "status": "Backend is running",
            "version": "0.1.0",
        }
    )


class ExperimentViewSet(viewsets.ModelViewSet):
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer
