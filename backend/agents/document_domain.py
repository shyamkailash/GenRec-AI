from dataclasses import dataclass

@dataclass
class DocumentGenerationResult:
    experiment_id: int
    pdf_path: str = ""
    docx_path: str = ""
    status: str = ""
    warnings: list[str] = None
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "experiment_id": self.experiment_id,
            "pdf_path": self.pdf_path,
            "docx_path": self.docx_path,
            "status": self.status,
            "warnings": self.warnings or [],
            "error": self.error,
        }
