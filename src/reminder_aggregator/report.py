import json
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
from hashlib import md5
from itertools import groupby
from pathlib import Path
from typing import Any, Iterator

from .types import Finding, ReminderType, ReportFormat


def _generate_table_report(findings: tuple[Finding, ...]) -> str:
    output: list[str] = []

    findings_by_file_path = groupby(findings, key=lambda f: f.file)

    for file_path, finding in findings_by_file_path:
        output.append(_generate_table_report_entry(file_path, finding))

    return "\n".join(output)


def _generate_table_report_entry(file_path: Path | str, findings: Iterator[Finding]) -> str:
    table_entry: str = ""

    entry_header: str = f"""
{file_path}
-------------------------------------------------------
"""

    table_entry = entry_header

    for finding in findings:
        finding_line: int = finding.line
        finding_content: str = finding.content.replace("\n", "\t")
        finding_type: ReminderType = finding.type

        table_entry = table_entry + f"{finding_line:<3} {finding_type:<6} {finding_content}\n"
    return table_entry


def _generate_json_report(findings: tuple[Finding, ...]) -> str:
    findings_object: list[dict[str, Any]] = [finding.__dict__ for finding in findings]

    return json.dumps(findings_object, indent=4)


def _generate_junitxml_report(findings: tuple[Finding, ...]) -> str:
    testsuite = ET.Element("testsuite", name="ReminderAggregator", tests=str(len(findings)))

    for finding in findings:
        testcase = ET.SubElement(testsuite, "testcase", classname=finding.file, name=f"Line {finding.line}")

        failure = ET.SubElement(
            testcase,
            "failure",
            message=f"Found {finding.type} tag",
            type=finding.type,
        )
        failure.text = finding.content

    return minidom.parseString(ET.tostring(element=testsuite, method="xml")).toprettyxml()


def _generate_codeclimate_report(findings: tuple[Finding, ...]) -> str:
    report: list[dict[str, Any]] = []

    for finding in findings:
        comment_text = finding.content
        description = f"Usage of {finding.type} tag"
        fingerprint = md5(f"{finding.file}-{finding.line}-{finding.type}".encode()).hexdigest()

        report.append(
            {
                "type": "issue",
                "check_name": finding.type,
                "description": description,
                "content": {
                    "body": comment_text,
                },
                "categories": ["Style"],
                "location": {
                    "path": finding.file,
                    "lines": {
                        "begin": finding.line,
                    },
                },
                "severity": "info",
                "fingerprint": fingerprint,
            }
        )

    return json.dumps(report, indent=4)


REPORT_FORMAT_MAP = {
    ReportFormat.JSON: _generate_json_report,
    ReportFormat.JUNITXML: _generate_junitxml_report,
    ReportFormat.CODECLIMATE: _generate_codeclimate_report,
    ReportFormat.TABLE: _generate_table_report,
}


def generate_report(report_format: ReportFormat, findings: tuple[Finding, ...]) -> str:
    report_function = REPORT_FORMAT_MAP.get(report_format, _generate_json_report)

    return report_function(findings)


def write_report(content: str, path: Path) -> None:
    path.write_text(content)
