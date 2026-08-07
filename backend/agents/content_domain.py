from dataclasses import asdict, dataclass

@dataclass
class GeneratedContent:
    theory: str = ""
    algorithm: str = ""
    procedure: str = ""
    program: str = ""
    output: str = ""
    result: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
