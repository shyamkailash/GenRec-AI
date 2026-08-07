from dataclasses import asdict, dataclass, field


@dataclass
class ExperimentPlan:
    experiment_id: int
    subject: str
    title: str

    experiment_type: str = "general"
    programming_language: str = ""
    requires_code: bool = True
    requires_output: bool = True
    requires_dataset: bool = False
    requires_image_output: bool = False

    required_sections: list[str] = field(default_factory=list)
    existing_sections: list[str] = field(default_factory=list)
    missing_sections: list[str] = field(default_factory=list)

    rag_queries: list[str] = field(default_factory=list)
    generation_order: list[str] = field(default_factory=list)
    validation_rules: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)