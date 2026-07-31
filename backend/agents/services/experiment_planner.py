from experiments.models import Experiment

from agents.planning_domain import ExperimentPlan


class ExperimentPlanningError(Exception):
    """Raised when an experiment plan cannot be created."""


DEFAULT_REQUIRED_SECTIONS = [
    "aim",
    "theory",
    "algorithm",
    "procedure",
    "program",
    "output",
    "result",
]


SUBJECT_RULES = {
    "machine learning": {
        "experiment_type": "machine_learning",
        "programming_language": "python",
        "requires_dataset": True,
        "requires_image_output": True,
    },
    "deep learning": {
        "experiment_type": "deep_learning",
        "programming_language": "python",
        "requires_dataset": True,
        "requires_image_output": True,
    },
    "computer vision": {
        "experiment_type": "computer_vision",
        "programming_language": "python",
        "requires_dataset": False,
        "requires_image_output": True,
    },
    "natural language processing": {
        "experiment_type": "nlp",
        "programming_language": "python",
        "requires_dataset": True,
        "requires_image_output": False,
    },
    "python": {
        "experiment_type": "programming",
        "programming_language": "python",
        "requires_dataset": False,
        "requires_image_output": False,
    },
    "java": {
        "experiment_type": "programming",
        "programming_language": "java",
        "requires_dataset": False,
        "requires_image_output": False,
    },
    "database": {
        "experiment_type": "database",
        "programming_language": "sql",
        "requires_dataset": False,
        "requires_image_output": False,
    },
    "network": {
        "experiment_type": "networking",
        "programming_language": "python",
        "requires_dataset": False,
        "requires_image_output": False,
    },
}


class ExperimentPlanningAgent:
    def plan(self, experiment: Experiment) -> ExperimentPlan:
        subject = experiment.subject.strip()
        title = experiment.title.strip()

        if not subject:
            raise ExperimentPlanningError(
                "Experiment subject is required."
            )

        if not title:
            raise ExperimentPlanningError(
                "Experiment title is required."
            )

        rule = self._detect_subject_rule(subject)

        existing_sections = self._get_existing_sections(
            experiment
        )

        missing_sections = [
            section
            for section in DEFAULT_REQUIRED_SECTIONS
            if section not in existing_sections
        ]

        generation_order = [
            section
            for section in DEFAULT_REQUIRED_SECTIONS
            if section in missing_sections
        ]

        plan = ExperimentPlan(
            experiment_id=experiment.id,
            subject=subject,
            title=title,
            experiment_type=rule["experiment_type"],
            programming_language=rule[
                "programming_language"
            ],
            requires_code=True,
            requires_output=True,
            requires_dataset=rule["requires_dataset"],
            requires_image_output=rule[
                "requires_image_output"
            ],
            required_sections=DEFAULT_REQUIRED_SECTIONS.copy(),
            existing_sections=existing_sections,
            missing_sections=missing_sections,
            rag_queries=self._build_rag_queries(
                subject=subject,
                title=title,
                programming_language=rule[
                    "programming_language"
                ],
            ),
            generation_order=generation_order,
            validation_rules=self._build_validation_rules(
                rule
            ),
        )

        if not experiment.documents.exists():
            plan.warnings.append(
                "No observation or experiment evidence is attached."
            )

        return plan

    def _detect_subject_rule(self, subject: str) -> dict:
        normalized_subject = subject.lower()

        for keyword, rule in SUBJECT_RULES.items():
            if keyword in normalized_subject:
                return rule

        return {
            "experiment_type": "general",
            "programming_language": "python",
            "requires_dataset": False,
            "requires_image_output": False,
        }

    def _get_existing_sections(
        self,
        experiment: Experiment,
    ) -> list[str]:
        existing_sections = []

        for section in DEFAULT_REQUIRED_SECTIONS:
            value = getattr(experiment, section, "")

            if isinstance(value, str) and value.strip():
                existing_sections.append(section)

        for document in experiment.documents.all():
            structured_content = (
                document.structured_content or {}
            )

            for section in DEFAULT_REQUIRED_SECTIONS:
                value = structured_content.get(section)

                if (
                    isinstance(value, str)
                    and value.strip()
                    and section not in existing_sections
                ):
                    existing_sections.append(section)

        return existing_sections

    def _build_rag_queries(
        self,
        subject: str,
        title: str,
        programming_language: str,
    ) -> list[str]:
        return [
            f"{subject} {title} aim theory",
            f"{title} algorithm and procedure",
            (
                f"{title} {programming_language} "
                "program implementation"
            ),
            f"{title} expected output and result",
        ]

    def _build_validation_rules(
        self,
        rule: dict,
    ) -> list[str]:
        rules = [
            "Aim must match the experiment title.",
            "Algorithm must correspond to the program.",
            "Procedure must describe the actual workflow.",
            "Output must be consistent with the program.",
            "Result must summarize the verified output.",
        ]

        if rule["requires_dataset"]:
            rules.append(
                "Dataset name and preprocessing details are required."
            )

        if rule["requires_image_output"]:
            rules.append(
                "Generated graphs or images must be included and validated."
            )

        return rules