from dataclasses import dataclass, field, replace
from pathlib import Path

import mashumaro.codecs.json as json_codec
import mashumaro.codecs.toml as toml_codec
import mashumaro.codecs.yaml as yaml_codec

from .types import ReminderType, ReportFormat

DEFAULT_REMINDER_TYPES: tuple[ReminderType, ...] = (
    ReminderType.TODO,
    ReminderType.FIXME,
    ReminderType.HACK,
)


@dataclass(frozen=True)
class ReportConfig:
    format: ReportFormat = ReportFormat.JSON
    path: Path = Path("reminders.json")
    stdout: bool = True


@dataclass(frozen=True)
class ReminderConfig:
    use_default: bool = True
    enabled: tuple[ReminderType, ...] = DEFAULT_REMINDER_TYPES
    disabled: tuple[ReminderType, ...] = ()


@dataclass(frozen=True)
class ReminderAggregatorConfig:
    reminder: ReminderConfig = field(default_factory=ReminderConfig)
    report: ReportConfig = field(default_factory=ReportConfig)
    scan_path: Path = Path("./")


def _load_yaml_config(config_path: Path) -> ReminderAggregatorConfig:
    config_content = config_path.read_text()

    config = yaml_codec.decode(config_content, ReminderAggregatorConfig)

    return config


def _load_json_config(config_path: Path) -> ReminderAggregatorConfig:
    config_content = config_path.read_text()

    config = json_codec.decode(config_content, ReminderAggregatorConfig)

    return config


def _load_toml_config(config_path: Path) -> ReminderAggregatorConfig:
    config_content = config_path.read_text()

    config = toml_codec.decode(config_content, ReminderAggregatorConfig)

    return config


def load_config(config_path: Path | None) -> ReminderAggregatorConfig:
    YAML_CONFIG_EXTENSIONS: tuple[str, ...] = (".yaml", ".yml")
    JSON_CONFIG_EXTENSIONS: tuple[str, ...] = (".json", ".json5")
    TOML_CONFIG_EXTENSIONS: tuple[str, ...] = (".toml",)

    if config_path is None:
        return ReminderAggregatorConfig()

    if config_path.suffix in YAML_CONFIG_EXTENSIONS:
        return _load_yaml_config(config_path)

    if config_path.suffix in JSON_CONFIG_EXTENSIONS:
        return _load_json_config(config_path)

    if config_path.suffix in TOML_CONFIG_EXTENSIONS:
        return _load_toml_config(config_path)

    return ReminderAggregatorConfig()


def get_configured_reminder_types(config: ReminderAggregatorConfig) -> tuple[ReminderType, ...]:
    if config.reminder.use_default:
        return DEFAULT_REMINDER_TYPES

    return tuple(type for type in config.reminder.enabled if type not in config.reminder.disabled)


def override_config_options(
    config: ReminderAggregatorConfig,
    scan_path: Path | None = None,
    reminder_use_default: bool | None = None,
    reminder_enabled: tuple[ReminderType, ...] | None = (),
    reminder_disabled: tuple[ReminderType, ...] | None = (),
    report_format: ReportFormat | None = None,
    report_path: Path | None = None,
    report_stdout: bool | None = True,
) -> ReminderAggregatorConfig:
    config_scan_path = config.scan_path
    config_reminder = config.reminder
    config_report = config.report

    if scan_path is not None:
        config_scan_path = scan_path

    if reminder_use_default is not None:
        config_reminder = replace(config_reminder, use_default=reminder_use_default)

    if reminder_enabled != ():
        config_reminder = replace(config_reminder, enabled=reminder_enabled)

    if reminder_disabled != ():
        config_reminder = replace(config_reminder, disabled=reminder_disabled)

    if report_format is not None:
        config_report = replace(config_report, format=report_format)

    if report_path is not None:
        config_report = replace(config_report, path=report_path)

    if report_stdout is not None:
        config_report = replace(config_report, stdout=report_stdout)

    return replace(
        config,
        scan_path=config_scan_path,
        reminder=config_reminder,
        report=config_report,
    )
