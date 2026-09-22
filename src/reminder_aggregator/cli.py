import os
from pathlib import Path

import click

from .config import load_config, override_config_options
from .report import generate_report, write_report
from .scanner import Scanner
from .types import ReminderType, ReportFormat


def _get_terminal_width() -> int:
    try:
        return os.get_terminal_size().columns - 10
    except OSError:
        return 80


CONTEXT_SETTINGS = {"max_content_width": _get_terminal_width()}


@click.command("reminder-aggregator", short_help="Generate a report", context_settings=CONTEXT_SETTINGS)
@click.version_option()
@click.option(
    "--report-path",
    "-o",
    type=Path,
    help=" Specify path where the report will be saved",
)
@click.option(
    "--report-format",
    "-f",
    type=click.Choice(ReportFormat),
    help="Specify the format of the generated report",
)
@click.option(
    "--config",
    "-c",
    "config_path",
    type=click.Path(exists=True),
)
@click.option(
    "--ignore-file",
    default=".gitignore",
    show_default=True,
    type=click.Path(exists=True),
    help="Specify ignore file to use",
)
@click.option(
    "--reminder-enabled",
    type=click.Choice(ReminderType),
    multiple=True,
)
@click.option(
    "--reminder-disabled",
    type=click.Choice(ReminderType),
    multiple=True,
)
@click.option(
    "--stdout",
    "report_stdout",
    type=bool,
)
@click.argument(
    "scan-path",
    envvar="RA_SCAN_PATH",
    type=Path,
    required=False,
    default=None,
)
def cli(
    scan_path: Path | None,
    report_path: Path | None,
    report_format: ReportFormat | None,
    ignore_file: Path,
    config_path: Path,
    reminder_enabled: tuple[ReminderType, ...] | None,
    reminder_disabled: tuple[ReminderType, ...] | None,
    report_stdout: bool | None,
) -> None:
    initial_config = load_config(config_path)

    config = override_config_options(
        initial_config,
        report_format=report_format,
        report_path=report_path,
        scan_path=scan_path,
        reminder_enabled=reminder_enabled,
        reminder_disabled=reminder_disabled,
        report_stdout=report_stdout,
    )

    file_scanner = Scanner(config)

    findings = file_scanner.scan()

    report: str = generate_report(config.report.format, findings)

    if config.report.path is not None:
        write_report(report, config.report.path)

    if config.report.stdout:
        print(report)


if __name__ == "__main__":
    cli()
