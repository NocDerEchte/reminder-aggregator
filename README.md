# Reminder Aggregator

A simple python tool that scans files in a directory for common reminder tags such as `TODO`, `FIXME`, etc. and generates a report from them.

## Requirements

- Python 3.13+

## Installation

With [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended):

```bash
uv venv
uv pip install --upgrade pip
uv pip install -r requirements.txt
```

Without uv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Optionally, set environment variables:

```bash
export RA_SEARCH_DIR=/relative/or/absolute/path 
python3 reminder_aggregator.py
```

## Future Changes

- Configure input/output paths via CLI flags
- Filter to check whether a reminder-tag is inside a comment (currently causes false positives)
- Support for multiple output formats
- Creation of a container image
