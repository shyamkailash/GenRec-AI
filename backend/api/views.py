from django.http import JsonResponse
from rest_framework import parsers, viewsets

from documents.models import ExperimentDocument
from experiments.models import Experiment

from .serializers import (
    ExperimentDocumentSerializer,
    ExperimentSerializer,
)


def home(request):
    return JsonResponse(
        {
            "project": "GenRec-AI",
            "status": "Backend is running",
            "version": "0.2.0",
        }
    )


class ExperimentViewSet(viewsets.ModelViewSet):
    queryset = Experiment.objects.prefetch_related(
        "documents"
    ).all()

    serializer_class = ExperimentSerializer


class ExperimentDocumentViewSet(viewsets.ModelViewSet):
    queryset = ExperimentDocument.objects.select_related(
        "experiment"
    ).all()

    serializer_class = ExperimentDocumentSerializer

    parser_classes = [
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser,
    ]

    def perform_create(self, serializer):
        uploaded_file = self.request.FILES.get("file")

        original_filename = (
            uploaded_file.name if uploaded_file else ""
        )

        serializer.save(
            original_filename=original_filename,
        )