from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class ReminderType(StrEnum):
    TODO = "TODO"
    FIXME = "FIXME"
    BUG = "BUG"
    HACK = "HACK"
    NOTE = "NOTE"


class ReportFormat(StrEnum):
    JSON = "json"
    JUNITXML = "junitxml"
    CODECLIMATE = "codeclimate"
    TABLE = "table"


@dataclass(frozen=True)
class Finding:
    file: str
    content: str
    type: ReminderType
    line: int


@dataclass(frozen=True)
class Report:
    output_path: Path
    findings: list[Finding]
    report_format: ReportFormat = ReportFormat.JSON
