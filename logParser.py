from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


LOG_LINE_PATTERN = re.compile(
	r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
	r"(?P<level>[A-Z]+) "
	r"(?P<message>.+)$"
)


@dataclass(frozen=True)
class LogEntry:
	timestamp: str
	level: str
	message: str


def parse_log_line(line: str) -> LogEntry | None:
	match = LOG_LINE_PATTERN.match(line.strip())
	if not match:
		return None

	return LogEntry(
		timestamp=match.group("timestamp"),
		level=match.group("level"),
		message=match.group("message"),
	)


def parse_log_file(file_path: Path) -> list[LogEntry]:
	entries: list[LogEntry] = []

	with file_path.open("r", encoding="utf-8") as log_file:
		for line_number, line in enumerate(log_file, start=1):
			parsed_line = parse_log_line(line)
			if parsed_line is None:
				print(f"Ignoring invalid line {line_number}: {line.rstrip()}")
				continue

			entries.append(parsed_line)

	return entries


def print_summary(entries: list[LogEntry]) -> None:
	if not entries:
		print("No valid log entries found.")
		return

	counts = Counter(entry.level for entry in entries)

	print(f"Parsed {len(entries)} log entries")
	for level in sorted(counts):
		print(f"{level}: {counts[level]}")

	print("\nError entries:")
	error_entries = [entry for entry in entries if entry.level == "ERROR"]
	if not error_entries:
		print("  None")
		return

	for entry in error_entries:
		print(f"  {entry.timestamp} - {entry.message}")


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="Parse a simple application log file.")
	parser.add_argument(
		"file",
		nargs="?",
		default=Path("logs/sample.log"),
		type=Path,
		help="Path to the log file to parse.",
	)
	return parser


def main() -> int:
	parser = build_parser()
	args = parser.parse_args()

	if not args.file.exists():
		print(f"Log file not found: {args.file}")
		return 1

	entries = parse_log_file(args.file)
	print_summary(entries)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())