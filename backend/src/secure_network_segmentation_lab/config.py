"""Configuration loading with validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from secure_network_segmentation_lab.models import AppConfig, ConfidenceThresholds
from secure_network_segmentation_lab.paths import config_dir


class PolicyConfigError(ValueError):
    """Raised when declarative policy files contain invalid content."""


class ConfigError(PolicyConfigError):
    """Alias for broader config errors."""


# Re-export for modules that import thresholds from config
__all__ = [
    "AppConfig",
    "ConfidenceThresholds",
    "ConfigError",
    "PolicyConfigError",
    "load_app_config",
    "load_adapter_registry",
    "load_device_classes",
    "load_evidence_weights",
    "load_json",
    "load_reachability_policy",
    "load_reachability_policy_raw",
    "load_segments",
    "load_segmentation_policy",
    "load_segmentation_policy_raw",
    "load_service_catalog",
    "load_synthetic_vendors",
    "load_vendors",
    "load_yaml",
    "load_yaml_safe",
    "validate_policy_structure",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


def load_yaml_safe(path: Path) -> dict[str, Any]:
    return load_yaml(path)


def load_app_config(name: str | Path | None = None) -> AppConfig:
    if name is None:
        path = config_dir() / "default.config.json"
    elif isinstance(name, Path):
        path = name
    else:
        path = config_dir() / name
    raw = load_json(path)
    try:
        return AppConfig.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"Invalid app config {path}: {exc}") from exc


def load_segments() -> dict[str, Any]:
    return load_json(config_dir() / "segments.json")


def load_device_classes() -> list[str]:
    data = load_json(config_dir() / "device-classes.json")
    classes = data.get("classes", [])
    if not isinstance(classes, list):
        raise ValueError("device-classes.json: classes must be a list")
    return [str(c) for c in classes]


def load_evidence_weights() -> dict[str, float]:
    data = load_json(config_dir() / "evidence-weights.json")
    weights = data.get("weights", {})
    if not isinstance(weights, dict):
        raise ValueError("evidence-weights.json: weights must be an object")
    return {str(k): float(v) for k, v in weights.items()}


def load_service_catalog() -> dict[str, Any]:
    return load_json(config_dir() / "service-catalog.json")


def load_synthetic_vendors() -> dict[str, Any]:
    return load_json(config_dir() / "synthetic-vendors.json")


def load_vendors() -> list[dict[str, Any]]:
    return list(load_synthetic_vendors().get("vendors", []))


def load_adapter_registry() -> dict[str, Any]:
    return load_json(config_dir() / "adapter-registry.json")


def load_segmentation_policy_raw() -> dict[str, Any]:
    return load_yaml(config_dir() / "segmentation-policy.yml")


def load_reachability_policy_raw() -> dict[str, Any]:
    return load_yaml(config_dir() / "reachability-policy.yml")


def load_segmentation_policy() -> dict[str, Any]:
    """Raw load without full validation (use policy.load_segmentation_policy for validated)."""
    return load_segmentation_policy_raw()


def load_reachability_policy() -> dict[str, Any]:
    return load_reachability_policy_raw()


SEGMENTATION_RULE_KEYS = frozenset(
    {
        "id",
        "precedence",
        "description",
        "match",
        "recommend_segment",
        "decision",
        "approval",
    }
)
SEGMENTATION_MATCH_KEYS = frozenset(
    {
        "device_class",
        "classification_status",
        "confidence_minimum",
        "confidence_maximum",
        "connection_type",
        "ownership_label",
        "approval_state",
        "security_state",
        "source_segment",
        "destination_segment",
        "tags",
    }
)
SEGMENTATION_TOP_KEYS = frozenset(
    {
        "version",
        "policy_id_prefix",
        "default_decision",
        "implicit_default_permit",
        "note",
        "rules",
    }
)
REACHABILITY_RULE_KEYS = frozenset(
    {
        "id",
        "precedence",
        "description",
        "source",
        "destination",
        "service",
        "decision",
    }
)
REACHABILITY_TOP_KEYS = frozenset(
    {
        "version",
        "policy_id_prefix",
        "implicit_default_permit",
        "default_decision",
        "note",
        "rules",
    }
)

_EXECUTABLE_MARKERS = (
    "eval(",
    "exec(",
    "__import__",
    "subprocess",
    "os.system",
    "{{",
    "{%",
    "#!",
)


def _reject_unknown(obj: dict[str, Any], allowed: frozenset[str], context: str) -> None:
    unknown = set(obj) - allowed
    if unknown:
        raise PolicyConfigError(f"{context}: unknown fields rejected: {sorted(unknown)}")


def _scan_executable(value: Any, context: str) -> None:
    if isinstance(value, str):
        lowered = value.lower()
        for marker in _EXECUTABLE_MARKERS:
            if marker.lower() in lowered:
                raise PolicyConfigError(f"{context}: executable/template content rejected")
    elif isinstance(value, dict):
        for key, child in value.items():
            _scan_executable(child, f"{context}.{key}")
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            _scan_executable(child, f"{context}[{idx}]")


def validate_policy_structure(raw: dict[str, Any], kind: str) -> None:
    """Reject unknown fields and executable markers in policy documents."""
    if kind == "segmentation":
        _reject_unknown(raw, SEGMENTATION_TOP_KEYS, "segmentation-policy")
        rules = raw.get("rules", [])
        if not isinstance(rules, list):
            raise PolicyConfigError("segmentation-policy: rules must be a list")
        for rule in rules:
            if not isinstance(rule, dict):
                raise PolicyConfigError("segmentation-policy: each rule must be a mapping")
            _reject_unknown(rule, SEGMENTATION_RULE_KEYS, f"rule {rule.get('id', '?')}")
            match = rule.get("match", {})
            if match is not None:
                if not isinstance(match, dict):
                    raise PolicyConfigError(f"rule {rule.get('id')}: match must be a mapping")
                _reject_unknown(match, SEGMENTATION_MATCH_KEYS, f"rule {rule.get('id')} match")
            _scan_executable(rule, f"rule {rule.get('id')}")
    elif kind == "reachability":
        _reject_unknown(raw, REACHABILITY_TOP_KEYS, "reachability-policy")
        rules = raw.get("rules", [])
        if not isinstance(rules, list):
            raise PolicyConfigError("reachability-policy: rules must be a list")
        for rule in rules:
            if not isinstance(rule, dict):
                raise PolicyConfigError("reachability-policy: each rule must be a mapping")
            _reject_unknown(rule, REACHABILITY_RULE_KEYS, f"rule {rule.get('id', '?')}")
            _scan_executable(rule, f"rule {rule.get('id')}")
    else:
        raise ValueError(f"Unknown policy kind: {kind}")
