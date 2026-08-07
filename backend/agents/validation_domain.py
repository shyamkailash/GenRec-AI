from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    is_valid: bool

    missing_sections: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)

    errors: list[str] = field(default_factory=list)

    score: int = 0