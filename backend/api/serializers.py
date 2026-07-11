from rest_framework import serializers

from documents.models import ExperimentDocument
from experiments.models import Experiment


class ExperimentDocumentSerializer(
    serializers.ModelSerializer
):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ExperimentDocument
        fields = [
            "id",
            "experiment",
            "document_type",
            "file",
            "file_url",
            "original_filename",
            "extracted_text",
            "extraction_status",
            "extraction_error",
            "uploaded_at",
        ]

        read_only_fields = [
            "id",
            "file_url",
            "original_filename",
            "extracted_text",
            "extraction_status",
            "extraction_error",
            "uploaded_at",
        ]

    def get_file_url(self, obj):
        request = self.context.get("request")

        if not obj.file:
            return None

        if request:
            return request.build_absolute_uri(obj.file.url)

        return obj.file.url


class ExperimentSerializer(serializers.ModelSerializer):
    documents = ExperimentDocumentSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Experiment
        fields = "__all__"

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]