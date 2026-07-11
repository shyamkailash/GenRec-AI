from django.contrib import admin

from .models import ExperimentDocument


@admin.register(ExperimentDocument)
class ExperimentDocumentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "experiment",
        "document_type",
        "original_filename",
        "extraction_status",
        "uploaded_at",
    ]

    list_filter = [
        "document_type",
        "extraction_status",
        "uploaded_at",
    ]

    search_fields = [
        "original_filename",
        "experiment__title",
        "experiment__subject",
    ]

    readonly_fields = [
        "uploaded_at",
    ]