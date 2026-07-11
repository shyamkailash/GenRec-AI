from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import models

from experiments.models import Experiment


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".docx",
    ".ipynb",
    ".py",
    ".txt",
}


def validate_document_extension(uploaded_file):
    extension = Path(uploaded_file.name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValidationError(
            f"Unsupported file type '{extension}'. "
            f"Allowed file types: {allowed}"
        )


class ExperimentDocument(models.Model):
    DOCUMENT_TYPES = [
        ("observation", "Observation Record"),
        ("code", "Source Code"),
        ("notebook", "Notebook"),
        ("output", "Output Screenshot"),
        ("reference", "Reference Document"),
        ("other", "Other"),
    ]

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    document_type = models.CharField(
        max_length=30,
        choices=DOCUMENT_TYPES,
        default="observation",
    )

    file = models.FileField(
        upload_to="experiment_documents/%Y/%m/%d/",
        validators=[validate_document_extension],
    )

    original_filename = models.CharField(
        max_length=255,
        blank=True,
    )

    extracted_text = models.TextField(
        blank=True,
    )

    extraction_status = models.CharField(
        max_length=30,
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
        default="pending",
    )

    extraction_error = models.TextField(
        blank=True,
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )

    def save(self, *args, **kwargs):
        if self.file and not self.original_filename:
            self.original_filename = self.file.name

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.experiment.title} - "
            f"{self.original_filename}"
        )