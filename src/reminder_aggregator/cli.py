import os
from pathlib import Path

import click

from reminder_aggregator import scanner

CONTEXT_SETTINGS = {"max_content_width": os.get_terminal_size().columns - 10}


@click.command("reminder-aggregator", short_help="Generate a report", context_settings=CONTEXT_SETTINGS)
@click.option(
    "--out-file",
    "-o",
    default="report.json",
    show_default=True,
    type=click.Path(),
    help=" Specify path where the report will be saved",
)
@click.option(
    "--format",
    "-f",
    default="json",
    show_default=True,
    type=click.Choice(["json", "codeclimate"]),
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
def cli(path: Path, out_file: Path, format: str, ignore_file: Path) -> None:
    """
    \b
    positional arguments:
        PATH    Specify the path that will be scanned [default: .]
    """
    # TODO: Add support for multiple output formats (junitxml, json, etc.)

    file_scanner = scanner.Scanner(
        scan_dir=Path(path), out_file=Path(out_file), out_format=format, ignore_file=Path(ignore_file)
    )

    file_scanner.scan()

    file_scanner.create_report()


if __name__ == "__main__":
    cli()
