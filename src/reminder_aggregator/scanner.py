import re
from pathlib import Path

from pathspec import GitIgnoreSpec
from pygments.lexer import Lexer
from pygments.lexers import get_lexer_for_filename
from pygments.token import Comment

from .config import ReminderAggregatorConfig, get_configured_reminder_types
from .types import Finding, ReminderType


class Scanner:
    def __init__(self, config: ReminderAggregatorConfig) -> None:
        self.config = config

    def scan(self) -> tuple[Finding, ...]:
        findings: list[Finding] = []

        ignore_spec: GitIgnoreSpec = _get_ignore_spec_from_file(self.config.ignore_file)

        enabled_reminder_types: tuple[ReminderType, ...] = get_configured_reminder_types(self.config)

        for file in self.config.scan_path.rglob("*"):
            if ignore_spec.match_file(file):
                continue
            if not _is_file_parseable(file):
                continue

            findings.extend(get_findings_from_file(file, enabled_reminder_types))

        return tuple(findings)


def _is_file_parseable(path: Path) -> bool:
    if not path.exists():
        return False

    if not path.is_file():
        return False

    if path.stat().st_size == 0:
        return False

    return True


def _process_comment_block(
    comment_start_line: int | None,
    comment_end_line: int | None,
    finding_pattern: re.Pattern[str],
    source: str,
    file_path: Path,
) -> list[Finding]:
    findings: list[Finding] = []

    if comment_start_line is None or comment_end_line is None:
        return findings

    lines = source.splitlines(keepends=True)

    # Lines are 1-based, so convert to 0-based indexes.
    content = "".join(lines[comment_start_line - 1 : comment_end_line])

    for offset, line_content in enumerate(
        content.splitlines(),
        start=comment_start_line,
    ):
        for finding_type, _ in finding_pattern.findall(line_content):
            if finding_type == "":
                continue

            findings.append(
                Finding(
                    line=offset,
                    content=content,
                    type=finding_type,
                    file=str(file_path),
                )
            )

    return findings


def get_findings_from_file(
    file_path: Path,
    reminder_types: tuple[ReminderType, ...],
) -> list[Finding]:
    findings: list[Finding] = []

    try:
        lexer: Lexer = get_lexer_for_filename(file_path)
    except ValueError:
        return findings

    finding_pattern = re.compile(rf"\b({'|'.join(map(re.escape, reminder_types))})\b[:\s\-]*([^\n*\/]+)")

    with open(file_path, encoding="utf-8", errors="ignore") as file:
        source = file.read()

    comment_start_line: int | None = None
    comment_end_line: int | None = None

    current_line = 1

    for token_type, value in lexer.get_tokens(source):
        if not (token_type == Comment or token_type.parent == Comment):
            current_line += value.count("\n")
            continue

        token_start_line = current_line
        token_end_line = current_line + value.count("\n")

        if comment_start_line is None:
            comment_start_line = token_start_line
            comment_end_line = token_end_line

        elif token_start_line == comment_end_line + 1:  # pyright: ignore[reportOptionalOperand]
            # Consecutive comment line -> same block.
            comment_end_line = token_end_line

        else:
            # There was a gap -> finish the previous block.
            findings.extend(
                _process_comment_block(comment_start_line, comment_end_line, finding_pattern, source, file_path)
            )

            comment_start_line = token_start_line
            comment_end_line = token_end_line

        current_line += value.count("\n")

    findings.extend(_process_comment_block(comment_start_line, comment_end_line, finding_pattern, source, file_path))

    return findings


def _get_ignore_spec_from_file(ignore_file: Path) -> GitIgnoreSpec:
    spec: GitIgnoreSpec = GitIgnoreSpec([])

    try:
        with open(ignore_file, encoding="utf-8", errors="ignore") as f:
            lines: list[str] = f.readlines()

            spec: GitIgnoreSpec = GitIgnoreSpec.from_lines(lines)
    except OSError:
        return spec

    return spec
