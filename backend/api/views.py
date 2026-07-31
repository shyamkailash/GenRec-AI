from django.http import JsonResponse
from rest_framework import parsers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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
            "version": "0.3.0",
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
        """
        Save the uploaded document, extract its text, and structure it
        automatically when it is an observation document.
        """
        uploaded_file = self.request.FILES.get("file")

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
        document.refresh_from_db()

        if (
            document.extraction_status == "completed"
            and document.document_type == "observation"
        ):
            document.process_observation_structure()

    @action(
        detail=True,
        methods=["post"],
        url_path="extract",
    )
    def extract_document(self, request, pk=None):
        """
        Manually rerun text extraction for an uploaded document.
        """
        document = self.get_object()

        document.process_extraction()
        document.refresh_from_db()

        serializer = self.get_serializer(document)

        response_status = (
            status.HTTP_200_OK
            if document.extraction_status == "completed"
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )

        return Response(
            serializer.data,
            status=response_status,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="extract-observation",
    )
    def extract_observation(self, request, pk=None):
        """
        Convert extracted observation text into structured sections.
        """
        document = self.get_object()

        if document.document_type != "observation":
            return Response(
                {
                    "error": (
                        "Only observation documents can be processed "
                        "through this endpoint."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if document.extraction_status != "completed":
            return Response(
                {
                    "error": (
                        "Text extraction must be completed before "
                        "observation section extraction."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        document.process_observation_structure()
        document.refresh_from_db()

        serializer = self.get_serializer(document)

        response_status = (
            status.HTTP_200_OK
            if document.structure_status == "completed"
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )

        return Response(
            serializer.data,
            status=response_status,
        )