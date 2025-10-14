# Reminder Aggregator

A simple python tool that scans files in a directory for common reminder tags such as `TODO`, `FIXME`, etc. and generates a report from them.

## Requirements

- Python 3.13+

## Installation

With [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended):

```bash
uv sync
```

## Usage

```bash
reminder_aggregator --help
```

## Future Changes

- Filter to check whether a reminder-tag is inside a comment (currently causes false positives)
- Support for multiple output formats
