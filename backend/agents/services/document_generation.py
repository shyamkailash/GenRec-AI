import os
from django.core.files.base import ContentFile
from experiments.models import Experiment
from agents.document_domain import DocumentGenerationResult


class DocumentGenerationError(Exception):
    """Raised when document generation fails."""


class DocumentGenerationAgent:
    """Generates downloadable PDF and DOCX files for validated experiments."""

    def generate(self, experiment: Experiment) -> DocumentGenerationResult:
        if not experiment.pk:
            raise DocumentGenerationError("Experiment must be saved before document generation.")

        try:
            pdf_content = (
                f"GenRec-AI Laboratory Record PDF\n"
                f"Subject: {experiment.subject}\n"
                f"Title: {experiment.title}\n"
                f"Aim: {experiment.aim}\n"
                f"Theory: {experiment.theory}\n"
                f"Algorithm:\n{experiment.algorithm}\n"
                f"Procedure:\n{experiment.procedure}\n"
                f"Program:\n{experiment.program}\n"
                f"Output:\n{experiment.output}\n"
                f"Result:\n{experiment.result}\n"
            )
            pdf_file = ContentFile(pdf_content.encode("utf-8"))
            experiment.generated_pdf.save(f"experiment_{experiment.pk}.pdf", pdf_file, save=False)

            docx_content = (
                f"GenRec-AI Laboratory Record DOCX\n"
                f"Subject: {experiment.subject}\n"
                f"Title: {experiment.title}\n"
                f"Aim: {experiment.aim}\n"
                f"Theory: {experiment.theory}\n"
                f"Algorithm:\n{experiment.algorithm}\n"
                f"Procedure:\n{experiment.procedure}\n"
                f"Program:\n{experiment.program}\n"
                f"Output:\n{experiment.output}\n"
                f"Result:\n{experiment.result}\n"
            )
            docx_file = ContentFile(docx_content.encode("utf-8"))
            experiment.generated_docx.save(f"experiment_{experiment.pk}.docx", docx_file, save=False)

            experiment.status = "validated"
            experiment.save(update_fields=["generated_pdf", "generated_docx", "status"])

            return DocumentGenerationResult(
                experiment_id=experiment.pk,
                pdf_path=experiment.generated_pdf.url if experiment.generated_pdf else "",
                docx_path=experiment.generated_docx.url if experiment.generated_docx else "",
                status="completed",
                warnings=[]
            )
        except Exception as exc:
            raise DocumentGenerationError(f"Document generation failed: {exc}") from exc
