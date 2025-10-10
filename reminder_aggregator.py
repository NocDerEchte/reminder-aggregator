import re
import os
import pathlib
import pathspec
import json
from typing import Any, Counter

def write_report(filename: str, data: Any) -> None:
  counter = Counter(match["type"].upper() for match in data)
  summary = dict(counter)
  summary["total"] = sum(counter.values())

  report = {
    "summary": summary,
    "details": data,
  }

  with open(filename, "w", encoding="utf-8") as file:
    json.dump(report, file, indent=2)

def parse_file(path: pathlib.Path, path_root: pathlib.Path, pattern: re.Pattern) -> list[dict[str, Any]]:
  # FIXME: Ensure that only comments count to matches.
  matches: list[dict[str, Any]] = []

  try:
    for line_number, line in enumerate(open(path)):
      line = line.strip()

      if match := re.search(pattern, line):
        matches.append({
          "type": match.group(1),
          "file": str(path.relative_to(path_root)),
          "line": line_number+1,
          "pos": match.start(1),
          "content": line.strip(),
        })

  except UnicodeDecodeError:
    print(f'Error reading {path}')

  return matches

def parse_directory(directory: pathlib.Path, path_root: pathlib.Path, match_regex, ignore_spec: pathspec.PathSpec) -> list[dict[str, Any]]:
  matches: list[dict[str, Any]] = []

  for path in directory.rglob('*'):
    if not path.is_file():
      continue

    if ignore_spec.match_file(path):
      continue

    match = parse_file(path, path_root, match_regex)

    if len(match) == 0:
      continue

    matches.extend(match)

  return matches

def load_ignore_spec(file_path: str = '.gitignore') -> pathspec.PathSpec:
  file = pathlib.Path(file_path)
  ignore_spec: pathspec.PathSpec

  if not file.is_file:
    ignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', [])

  with open(file, 'r', encoding='utf-8') as file:
    ignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', file)

  return ignore_spec

def main() -> None:
  # TODO: Add cli flags and env vars for configuration instead of hard-coded values
  # TODO: Add support for multiple output formats (junitxml, json, etc.)

  path_root: pathlib.Path = pathlib.Path(os.environ.get('RA_ROOT_DIR', './'))
  search_directory: pathlib.Path = pathlib.Path(os.environ.get('RA_SEARCH_DIR', './'))

  output_path: str = 'report.json'

  re_match_str: str = r'(TODO|FIXME|HACK|OPTIMIZE|REVIEW)'
  re_match: re.Pattern = re.compile(re_match_str)

  matches: list[dict[str, Any]] = []

  ignore_spec: pathspec.PathSpec = load_ignore_spec()

  matches = parse_directory(search_directory, path_root, re_match, ignore_spec)

  write_report(output_path, matches)

if __name__ == '__main__':
  main()
