from dataclasses import dataclass, field
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


@dataclass(frozen=True)
class ReminderConfig:
    use_default: bool = True
    enabled: tuple[ReminderType, ...] = DEFAULT_REMINDER_TYPES
    disabled: tuple[ReminderType, ...] = ()


@dataclass(frozen=True)
class ReminderAggregatorConfig:
    reminder: ReminderConfig = field(default_factory=ReminderConfig)
    report: ReportConfig = field(default_factory=ReportConfig)
    path: Path = Path("./")


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

    if config.reminder.enabled:
        return config.reminder.enabled

    return ()
