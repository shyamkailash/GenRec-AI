from dataclasses import asdict, dataclass, field


@dataclass
class ObservationSections:
    experiment_number: str = ""
    subject: str = ""
    title: str = ""
    aim: str = ""
    theory: str = ""
    algorithm: str = ""
    procedure: str = ""
    program: str = ""
    expected_output: str = ""
    result: str = ""

    missing_sections: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)