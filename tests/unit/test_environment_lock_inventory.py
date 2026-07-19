from __future__ import annotations

from collections.abc import Iterable
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tomllib
from typing import Any

from jsonschema import FormatChecker
from jsonschema.validators import validator_for


ROOT = Path(__file__).parents[2]
INVENTORY_PATH = ROOT / "research" / "ENVIRONMENT_LOCK_INVENTORY.json"
SCHEMA_PATH = ROOT / "schemas" / "environment-lock-inventory.schema.json"
DOCUMENT_PATH = ROOT / "research" / "ENVIRONMENT_TRUST_BOUNDARY.md"
WORKFLOW_PATHS = (
    ROOT / ".github" / "workflows" / "ci.yml",
    ROOT / ".github" / "workflows" / "heavy-search.yml",
)
EXPECTED_COMMIT = "41fb0a9b64ff2c6deeeb8080f41d1ea82bcb568d"

CLASSIFICATIONS = {
    "IMMUTABLE_PIN",
    "VERSION_PIN_ONLY",
    "MUTABLE_RESOLUTION",
    "CAPTURE_REQUIRED",
    "EXTERNAL_SERVICE_TRUST",
}
LOCKABILITIES = {
    "REPOSITORY_PINNABLE",
    "CAPTURE_ONLY",
    "NOT_REPOSITORY_CONTROLLED",
}
TOP_KEYS = [
    "schema_version",
    "repository",
    "inspected_project_commit",
    "task_id",
    "generated_at_utc",
    "scope_statement",
    "entries",
    "limitations",
]
ENTRY_KEYS = [
    "id",
    "layer",
    "category",
    "source_locations",
    "current_selector",
    "observed_state",
    "outcome_relevance",
    "classification",
    "repository_lockability",
    "external_trust_dependencies",
    "evidence",
    "required_next_action",
    "blocks_evidence",
]
SOURCE_KEYS = [
    "path",
    "line_start",
    "line_end",
    "selector_kind",
    "expression",
]


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def _load_inventory() -> dict[str, Any]:
    raw = INVENTORY_PATH.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8", errors="strict")
    data = json.loads(
        text,
        object_pairs_hook=_strict_object,
        parse_constant=_reject_nonfinite,
    )
    assert isinstance(data, dict)
    return data


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _source_records(
    inventory: dict[str, Any], selector_kind: str
) -> list[tuple[str, int, str]]:
    records = []
    for entry in inventory["entries"]:
        for source in entry["source_locations"]:
            if source["selector_kind"] == selector_kind:
                assert source["line_start"] == source["line_end"]
                records.append(
                    (
                        source["path"],
                        source["line_start"],
                        source["expression"],
                    )
                )
    return sorted(records)


def _workflow_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _current_runs_on() -> list[tuple[str, int, str]]:
    pattern = re.compile(r"^\s*runs-on:\s*([^#\s]+)\s*(?:#.*)?$")
    records = []
    for path in WORKFLOW_PATHS:
        for line_number, line in enumerate(_workflow_lines(path), start=1):
            if "runs-on:" not in line or line.lstrip().startswith("#"):
                continue
            match = pattern.fullmatch(line)
            assert match is not None, f"unsupported runs-on syntax at {path}:{line_number}"
            records.append(
                (_relative(path), line_number, f"runs-on: {match.group(1)}")
            )
    return sorted(records)


def _action_pin_output() -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, "tools/check_github_action_pins.py"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == b""
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    return payload


def _current_actions(payload: dict[str, Any]) -> list[tuple[str, int, str]]:
    return sorted(
        (
            record["workflow"],
            record["line"],
            f"uses: {record['reference']}",
        )
        for record in payload["external_references"]
    )


def _setup_python_sources(
    payload: dict[str, Any],
) -> tuple[list[tuple[str, int, str]], set[str]]:
    setup_steps = [
        record
        for record in payload["external_references"]
        if record["repository"] == "actions/setup-python"
    ]
    records: list[tuple[str, int, str]] = []
    values: set[str] = set()
    dynamic_matrix_used = False

    for step in setup_steps:
        path = ROOT / step["workflow"]
        lines = _workflow_lines(path)
        selector_record: tuple[str, int, str] | None = None
        for index in range(step["line"], len(lines)):
            line = lines[index]
            if index + 1 > step["line"] and re.match(r"^\s*-\s+name:", line):
                break
            match = re.match(r"^\s*python-version:\s*(.+?)\s*$", line)
            if match is None:
                continue
            expression = f"python-version: {match.group(1)}"
            selector_record = (_relative(path), index + 1, expression)
            literal = match.group(1).strip("\"'")
            if literal == "${{ matrix.python-version }}":
                dynamic_matrix_used = True
            else:
                assert re.fullmatch(r"[0-9]+\.[0-9]+", literal)
                values.add(literal)
            break
        assert selector_record is not None, f"setup-python step lacks python-version: {step}"
        records.append(selector_record)

    if dynamic_matrix_used:
        ci_path = WORKFLOW_PATHS[0]
        lines = _workflow_lines(ci_path)
        matrix_key = next(
            index
            for index, line in enumerate(lines)
            if re.fullmatch(r"\s*python-version:\s*", line)
        )
        key_indent = len(lines[matrix_key]) - len(lines[matrix_key].lstrip())
        for index in range(matrix_key + 1, len(lines)):
            line = lines[index]
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip())
            if indent <= key_indent:
                break
            match = re.fullmatch(r'\s*-\s*"([0-9]+\.[0-9]+)"\s*', line)
            assert match is not None, f"unsupported python-version matrix value: {line}"
            values.add(match.group(1))
            records.append((_relative(ci_path), index + 1, line.strip()))

    return sorted(records), values


def _docker_from() -> tuple[str, int, str]:
    lines = _workflow_lines(ROOT / "Dockerfile")
    records = [
        ("Dockerfile", index, line.strip())
        for index, line in enumerate(lines, start=1)
        if re.match(r"^FROM\s+\S+\s*$", line)
    ]
    assert len(records) == 1
    return records[0]


def _docker_apt_packages() -> list[tuple[str, int, str]]:
    lines = _workflow_lines(ROOT / "Dockerfile")
    install_index = next(
        index
        for index, line in enumerate(lines)
        if "apt-get install --yes --no-install-recommends" in line
    )
    records = []
    for index in range(install_index + 1, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("&&"):
            break
        token = stripped.removesuffix("\\").strip()
        assert re.fullmatch(r"[a-z0-9][a-z0-9+.-]*", token)
        records.append(("Dockerfile", index + 1, token))
    assert records
    return records


def _docker_pip_route() -> tuple[str, int, str]:
    for line_number, line in enumerate(_workflow_lines(ROOT / "Dockerfile"), start=1):
        marker = "python -m pip install"
        if marker not in line:
            continue
        command = line[line.index(marker) :].strip().removesuffix("\\").strip()
        return ("Dockerfile", line_number, command)
    raise AssertionError("Dockerfile has no python -m pip install route")


def _pyproject_sources() -> tuple[list[tuple[str, int, str]], tuple[str, int, str]]:
    path = ROOT / "pyproject.toml"
    lines = _workflow_lines(path)
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    dependencies = [
        *data["build-system"]["requires"],
        *data["project"]["dependencies"],
    ]
    for group in sorted(data["project"].get("optional-dependencies", {})):
        dependencies.extend(data["project"]["optional-dependencies"][group])

    records = []
    for dependency in dependencies:
        matching_lines = [
            index
            for index, line in enumerate(lines, start=1)
            if f'"{dependency}"' in line
        ]
        assert len(matching_lines) == 1
        records.append(("pyproject.toml", matching_lines[0], dependency))

    backend = data["build-system"]["build-backend"]
    backend_lines = [
        index
        for index, line in enumerate(lines, start=1)
        if re.fullmatch(rf'build-backend\s*=\s*"{re.escape(backend)}"', line)
    ]
    assert len(backend_lines) == 1
    backend_record = (
        "pyproject.toml",
        backend_lines[0],
        f'build-backend = "{backend}"',
    )
    return sorted(records), backend_record


def _all_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _all_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_strings(item)


def test_inventory_is_strict_canonical_and_schema_valid() -> None:
    inventory = _load_inventory()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator_type = validator_for(schema)
    validator_type.check_schema(schema)
    validator_type(schema, format_checker=FormatChecker()).validate(inventory)

    assert list(inventory) == TOP_KEYS
    assert inventory["inspected_project_commit"] == EXPECTED_COMMIT
    assert INVENTORY_PATH.read_bytes() == (
        json.dumps(inventory, ensure_ascii=True, indent=2) + "\n"
    ).encode("utf-8")

    ids = [entry["id"] for entry in inventory["entries"]]
    assert len(ids) == len(set(ids))
    assert ids == sorted(ids)
    for entry in inventory["entries"]:
        assert list(entry) == ENTRY_KEYS
        assert entry["classification"] in CLASSIFICATIONS
        assert entry["repository_lockability"] in LOCKABILITIES
        assert list(entry["blocks_evidence"]) == ["V1", "V3", "V4"]
        source_sort_key = lambda source: (
            source["path"],
            source["line_start"],
            source["line_end"],
            source["selector_kind"],
            source["expression"],
        )
        assert entry["source_locations"] == sorted(
            entry["source_locations"], key=source_sort_key
        )
        for source in entry["source_locations"]:
            assert list(source) == SOURCE_KEYS
            assert source["line_end"] >= source["line_start"]
            assert "\\" not in source["path"]
            pure_path = PurePosixPath(source["path"])
            assert not pure_path.is_absolute()
            assert pure_path.parts
            assert all(part not in {"", ".", ".."} for part in pure_path.parts)
            source_path = ROOT.joinpath(*pure_path.parts)
            assert source_path.is_file()
            lines = source_path.read_text(encoding="utf-8").splitlines()
            assert source["line_end"] <= len(lines)
            selected = "\n".join(
                lines[source["line_start"] - 1 : source["line_end"]]
            )
            assert source["expression"] in selected

    placeholder = re.compile(r"(?i)^(?:TBD|TODO|FIXME|PLACEHOLDER|\?{3})$")
    angle_template = re.compile(r"^<[^<>]+>$")
    for value in _all_strings(inventory):
        assert placeholder.fullmatch(value.strip()) is None
        assert angle_template.fullmatch(value.strip()) is None
        assert not re.fullmatch(r"0{40}|0{64}", value)


def test_inventory_matches_workflow_runners_actions_and_python_selectors() -> None:
    inventory = _load_inventory()
    action_payload = _action_pin_output()

    assert _source_records(inventory, "WORKFLOW_RUNNER") == _current_runs_on()
    assert _source_records(inventory, "WORKFLOW_ACTION") == _current_actions(
        action_payload
    )

    python_sources, python_values = _setup_python_sources(action_payload)
    assert _source_records(inventory, "WORKFLOW_PYTHON_VERSION") == python_sources
    inventoried_values = {
        entry["current_selector"]
        for entry in inventory["entries"]
        if entry["category"] == "PYTHON_VERSION_SELECTOR"
    }
    assert inventoried_values == python_values


def test_inventory_matches_docker_selectors() -> None:
    inventory = _load_inventory()
    assert _source_records(inventory, "DOCKER_FROM") == [_docker_from()]
    assert _source_records(inventory, "DOCKER_APT_PACKAGE") == sorted(
        _docker_apt_packages()
    )
    assert _source_records(inventory, "DOCKER_PYTHON_INSTALL") == [
        _docker_pip_route()
    ]


def test_inventory_matches_all_direct_python_dependencies_and_backend() -> None:
    inventory = _load_inventory()
    dependencies, backend = _pyproject_sources()
    assert _source_records(inventory, "PYPROJECT_DEPENDENCY") == dependencies
    assert _source_records(inventory, "PYPROJECT_BUILD_BACKEND") == [backend]


def test_required_selector_classifications_are_not_overstated() -> None:
    inventory = _load_inventory()
    entries = inventory["entries"]
    expected = {
        "RUNNER_SELECTOR": "MUTABLE_RESOLUTION",
        "EXTERNAL_ACTION": "IMMUTABLE_PIN",
        "PYTHON_VERSION_SELECTOR": "VERSION_PIN_ONLY",
        "CONTAINER_BASE_IMAGE": "IMMUTABLE_PIN",
        "APT_PACKAGE": "MUTABLE_RESOLUTION",
        "PYTHON_INSTALL_ROUTE": "MUTABLE_RESOLUTION",
        "PYTHON_DIRECT_DEPENDENCY": "VERSION_PIN_ONLY",
    }
    for category, classification in expected.items():
        selected = [entry for entry in entries if entry["category"] == category]
        assert selected, f"missing category: {category}"
        assert {entry["classification"] for entry in selected} == {classification}


def test_markdown_interpretation_matches_every_inventory_entry() -> None:
    inventory = _load_inventory()
    document = DOCUMENT_PATH.read_text(encoding="utf-8")
    ids = [entry["id"] for entry in inventory["entries"]]
    headings = re.findall(r"(?m)^### (ENV-[A-Z0-9-]+)$", document)
    assert headings == ids
    assert inventory["inspected_project_commit"] in document
    assert "research/ENVIRONMENT_LOCK_INVENTORY.json" in document

    all_references = set(
        re.findall(r"(?<![A-Z0-9-])ENV-[A-Z0-9-]+\b", document)
    )
    assert all_references == set(ids)
    sections = re.split(r"(?m)^### ENV-[A-Z0-9-]+$", document)[1:]
    assert len(sections) == len(inventory["entries"])
    for entry, section in zip(inventory["entries"], sections, strict=True):
        blocks = entry["blocks_evidence"]
        assert f"- Classification: `{entry['classification']}`" in section
        assert (
            f"- Repository lockability: `{entry['repository_lockability']}`"
            in section
        )
        assert (
            f"- Evidence blockers: `V1={str(blocks['V1']).lower()}`, "
            f"`V3={str(blocks['V3']).lower()}`, "
            f"`V4={str(blocks['V4']).lower()}`"
        ) in section
