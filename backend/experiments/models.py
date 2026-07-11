from django.db import models


class Experiment(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("processing", "Processing"),
        ("generated", "Generated"),
        ("validated", "Validated"),
        ("failed", "Failed"),
    ]

    subject = models.CharField(max_length=200)
    title = models.CharField(max_length=300)

    aim = models.TextField(blank=True)
    theory = models.TextField(blank=True)
    algorithm = models.TextField(blank=True)
    procedure = models.TextField(blank=True)
    program = models.TextField(blank=True)
    output = models.TextField(blank=True)
    result = models.TextField(blank=True)

    generated_record = models.TextField(blank=True)

    observation_file = models.FileField(
        upload_to="observations/",
        blank=True,
        null=True,
    )

    generated_pdf = models.FileField(
        upload_to="generated/pdf/",
        blank=True,
        null=True,
    )

    generated_docx = models.FileField(
        upload_to="generated/docx/",
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="draft",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} - {self.title}"
