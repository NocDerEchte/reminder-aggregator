import os
from pathlib import Path

import click

from .config import load_config
from .report import generate_report
from .scanner import Scanner


def _get_terminal_width() -> int:
    try:
        return os.get_terminal_size().columns - 10
    except OSError:
        return 80


CONTEXT_SETTINGS = {"max_content_width": _get_terminal_width()}


@click.command("reminder-aggregator", short_help="Generate a report", context_settings=CONTEXT_SETTINGS)
@click.option(
    "--out-file",
    "-o",
    type=click.Path(),
    help=" Specify path where the report will be saved",
)
@click.option(
    "--format",
    "-f",
    default="json",
    show_default=True,
    type=click.Choice(["json", "codeclimate", "junitxml"]),
    help="Specify the format of the generated report",
)
@click.option(
    "--ignore-file",
    default=".gitignore",
    show_default=True,
    type=click.Path(exists=True),
    help="Specify ignore file to use",
)
@click.argument("path", envvar="RA_SEARCH_DIR", default=".", type=click.Path())
def cli(path: Path, out_file: Path | None, format: str, ignore_file: Path) -> None:
    """
    \b
    positional arguments:
        PATH    Specify the path that will be scanned [default: .]
    """
    # TODO: Add support for multiple output formats (junitxml, json, etc.)

    config = load_config(None)

    file_scanner = Scanner(config=config)

    findings = file_scanner.scan()

    print(generate_report(config.report.format, findings))


if __name__ == "__main__":
    cli()
