import re

from agents.observation_domain import ObservationSections


class ObservationExtractionError(Exception):
    """Raised when observation extraction cannot be completed."""


SECTION_ALIASES = {
    "experiment_number": [
        "experiment no",
        "experiment number",
        "exp no",
        "ex no",
    ],
    "subject": [
        "subject",
        "subject name",
        "laboratory",
        "lab name",
    ],
    "title": [
        "title",
        "experiment title",
        "experiment name",
    ],
    "aim": [
        "aim",
        "objective",
    ],
    "theory": [
        "theory",
        "concept",
        "description",
    ],
    "algorithm": [
        "algorithm",
        "steps",
    ],
    "procedure": [
        "procedure",
        "method",
    ],
    "program": [
        "program",
        "code",
        "source code",
    ],
    "expected_output": [
        "expected output",
        "sample output",
        "output",
    ],
    "result": [
        "result",
        "conclusion",
    ],
}


REQUIRED_SECTIONS = [
    "title",
    "aim",
    "algorithm",
    "procedure",
]


def normalize_heading(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9 ]", "", value)
    value = re.sub(r"\s+", " ", value)
    return value


def identify_heading(line: str) -> str | None:
    candidate = normalize_heading(line.split(":", 1)[0])

    for section_name, aliases in SECTION_ALIASES.items():
        if candidate in aliases:
            return section_name

    return None


def clean_section_text(value: str) -> str:
    return value.strip(" \n\t:-")


def extract_inline_content(line: str) -> str:
    if ":" not in line:
        return ""

    return clean_section_text(line.split(":", 1)[1])


def extract_observation_sections(
    extracted_text: str,
) -> ObservationSections:
    if not extracted_text or not extracted_text.strip():
        raise ObservationExtractionError(
            "The observation document contains no extracted text."
        )

    sections: dict[str, list[str]] = {
        key: [] for key in SECTION_ALIASES
    }

    current_section: str | None = None

    for raw_line in extracted_text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        detected_section = identify_heading(line)

        if detected_section:
            current_section = detected_section

            inline_content = extract_inline_content(line)

            if inline_content:
                sections[current_section].append(inline_content)

            continue

        if current_section:
            sections[current_section].append(line)

    observation = ObservationSections(
        experiment_number=clean_section_text(
            "\n".join(sections["experiment_number"])
        ),
        subject=clean_section_text(
            "\n".join(sections["subject"])
        ),
        title=clean_section_text(
            "\n".join(sections["title"])
        ),
        aim=clean_section_text(
            "\n".join(sections["aim"])
        ),
        theory=clean_section_text(
            "\n".join(sections["theory"])
        ),
        algorithm=clean_section_text(
            "\n".join(sections["algorithm"])
        ),
        procedure=clean_section_text(
            "\n".join(sections["procedure"])
        ),
        program=clean_section_text(
            "\n".join(sections["program"])
        ),
        expected_output=clean_section_text(
            "\n".join(sections["expected_output"])
        ),
        result=clean_section_text(
            "\n".join(sections["result"])
        ),
    )

    observation.missing_sections = [
        section
        for section in REQUIRED_SECTIONS
        if not getattr(observation, section)
    ]

    if len(extracted_text.strip()) < 100:
        observation.warnings.append(
            "Very little text was extracted from the observation."
        )

    if not observation.program:
        observation.warnings.append(
            "Program or source code was not detected."
        )

    return observation