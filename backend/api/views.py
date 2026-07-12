from django.http import JsonResponse
from rest_framework import parsers, viewsets

from documents.models import ExperimentDocument
from experiments.models import Experiment

from rest_framework import parsers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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
    
    @action(
        detail=True,
        methods=["post"],
        url_path="extract",
    )

    def extract_document(self, request, pk=None):
        document = self.get_object()

        document.process_extraction()
        document.refresh_from_db()

        serializer = self.get_serializer(
            document
        )

        response_status = (
            status.HTTP_200_OK
            if document.extraction_status
            == "completed"
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )

        return Response(
            serializer.data,
            status=response_status,
        )


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
        uploaded_file = self.request.FILES.get(
            "file"
        )

        original_filename = (
            uploaded_file.name
            if uploaded_file
            else ""
        )

        document = serializer.save(
            original_filename=original_filename,
            extraction_status="pending",
        )

        document.process_extraction()