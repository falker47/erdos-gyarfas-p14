#!/usr/bin/env python3
"""Reject mutable external Action references in every GitHub workflow."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from typing import Any, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FULL_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
GITHUB_PATH_SEGMENT_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
DOCKER_REFERENCE_PATTERN = re.compile(
    r"^docker://(?P<image>[a-z0-9._:/-]+)@sha256:"
    r"(?P<digest>[0-9a-f]{64})$"
)
CANONICAL_USES_PATTERN = re.compile(
    r"^ *(?:- +)?uses: +(?P<reference>\S+)$"
)
BLOCK_SCALAR_HEADER_PATTERN = re.compile(
    r"^(?P<indent> *)(?P<sequence>- +)?"
    r"[A-Za-z_][A-Za-z0-9_.-]*: *[|>]"
    r"(?P<modifiers>[+-][1-9]?|[1-9][+-]?)? *$"
)
SIMPLE_USES_KEY_PATTERN = re.compile(
    r'''^(?:uses|"uses"|'uses')\s*:'''
)
EXPLICIT_USES_KEY_PATTERN = re.compile(
    r'''^\?\s*(?:uses|"uses"|'uses')(?:\s|:|$)'''
)
MULTILINE_INDICATOR_PATTERN = re.compile(
    r"^[|>](?:[+-][1-9]?|[1-9][+-]?)?$"
)


class PinCheckError(ValueError):
    """A deterministic workflow discovery, parsing, or pinning failure."""


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _write_bytes(stream: Any, payload: bytes) -> None:
    binary_stream = getattr(stream, "buffer", None)
    if binary_stream is not None:
        binary_stream.write(payload)
        binary_stream.flush()
    else:
        stream.write(payload.decode("utf-8", errors="replace"))
        stream.flush()


def _write_json_line(stream: Any, value: dict[str, Any]) -> None:
    payload = (
        json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
        + "\n"
    ).encode("utf-8")
    _write_bytes(stream, payload)


def _code_before_comment(line: str) -> tuple[str, bool]:
    """Return YAML code before an outside-quote comment and quote balance."""

    single_quoted = False
    double_quoted = False
    index = 0
    while index < len(line):
        character = line[index]
        if single_quoted:
            if character == "'":
                if index + 1 < len(line) and line[index + 1] == "'":
                    index += 2
                    continue
                single_quoted = False
            index += 1
            continue
        if double_quoted:
            if character == "\\":
                index += 2
                continue
            if character == '"':
                double_quoted = False
            index += 1
            continue
        if character == "'":
            single_quoted = True
        elif character == '"':
            double_quoted = True
        elif character == "#" and (
            index == 0 or line[index - 1].isspace()
        ):
            return line[:index].rstrip(" \t"), True
        index += 1
    return line.rstrip(" \t"), not (single_quoted or double_quoted)


def _structural_prefix(code: str) -> str:
    prefix = code.lstrip(" \t")
    if prefix.startswith("-") and len(prefix) > 1 and prefix[1].isspace():
        prefix = prefix[2:].lstrip(" \t")
    return prefix


def _quoted_token(
    text: str,
    start: int,
) -> tuple[str | None, int]:
    quote = text[start]
    index = start + 1
    characters: list[str] = []
    escaped_double_quote = False
    while index < len(text):
        character = text[index]
        if quote == "'":
            if character == "'":
                if index + 1 < len(text) and text[index + 1] == "'":
                    characters.append("'")
                    index += 2
                    continue
                return "".join(characters), index + 1
            characters.append(character)
            index += 1
            continue
        if character == "\\":
            escaped_double_quote = True
            index += 2
            continue
        if character == '"':
            return (
                None if escaped_double_quote else "".join(characters),
                index + 1,
            )
        characters.append(character)
        index += 1
    return None, len(text)


def _contains_flow_uses_key(code: str) -> bool:
    """Detect a uses key in unsupported YAML flow syntax."""

    depth = 0
    index = 0
    while index < len(code):
        if code.startswith("${{", index):
            end = code.find("}}", index + 3)
            if end < 0:
                return False
            index = end + 2
            continue
        character = code[index]
        if character in "[{":
            depth += 1
            index += 1
            continue
        if character in "]}":
            depth = max(0, depth - 1)
            index += 1
            continue
        if character in "'\"":
            token, end = _quoted_token(code, index)
            if depth > 0:
                tail = code[end:]
                if token == "uses" and re.match(r"^\s*:", tail):
                    return True
                if token is None and re.match(r"^\s*:", tail):
                    return True
            index = end
            continue
        if depth > 0 and code.startswith("uses", index):
            before_ok = index == 0 or not (
                code[index - 1].isalnum() or code[index - 1] in "_.-"
            )
            end = index + len("uses")
            after = re.match(r"^\s*:", code[end:])
            if before_ok and after is not None:
                return True
        index += 1
    return False


def _possible_uses_key(code: str, quotes_balanced: bool) -> bool:
    prefix = _structural_prefix(code)
    if SIMPLE_USES_KEY_PATTERN.match(prefix) is not None:
        return True
    if EXPLICIT_USES_KEY_PATTERN.match(prefix) is not None:
        return True
    if not quotes_balanced and re.match(r'''^(?:uses|["']uses)\b''', prefix):
        return True
    return _contains_flow_uses_key(code)


def _has_noncanonical_mapping_key(code: str) -> bool:
    prefix = _structural_prefix(code)
    if prefix.startswith("?"):
        return True
    if re.match(r"^[*&][^:]*:", prefix) is not None:
        return True
    if prefix.startswith("!") and ":" in prefix:
        return True
    if prefix.startswith('"'):
        _, end = _quoted_token(prefix, 0)
        if re.match(r"^\s*:", prefix[end:]) is not None:
            raw_key = prefix[1 : max(1, end - 1)]
            if "\\" in raw_key:
                return True
    index = 0
    while index < len(code):
        if code.startswith("${{", index):
            end = code.find("}}", index + 3)
            if end < 0:
                break
            index = end + 2
            continue
        character = code[index]
        if character in "'\"":
            _, index = _quoted_token(code, index)
            continue
        if character in "{,":
            lookahead = index + 1
            while lookahead < len(code) and code[lookahead].isspace():
                lookahead += 1
            if lookahead < len(code) and code[lookahead] in "?*!&":
                return True
        index += 1
    return False


def _github_reference(reference: str) -> tuple[str, str]:
    if reference.count("@") != 1:
        raise PinCheckError(
            "external Action reference must use owner/repository[/subpath]@ref"
        )
    action_path, commit = reference.rsplit("@", 1)
    parts = action_path.split("/")
    if (
        len(parts) < 2
        or any(
            not part
            or part in {".", ".."}
            or GITHUB_PATH_SEGMENT_PATTERN.fullmatch(part) is None
            for part in parts
        )
    ):
        raise PinCheckError(
            "external Action reference must use owner/repository[/subpath]@ref"
        )
    if FULL_COMMIT_PATTERN.fullmatch(commit) is None:
        raise PinCheckError(
            "external GitHub Action ref must be a lowercase 40-character "
            "commit SHA"
        )
    return "/".join(parts[:2]), commit


def _docker_reference(reference: str) -> None:
    match = DOCKER_REFERENCE_PATTERN.fullmatch(reference)
    if match is None:
        raise PinCheckError(
            "remote Docker Action must use docker://image@sha256:<64-lowercase-hex>"
        )
    image = match.group("image")
    image_parts = image.split("/")
    if (
        image.startswith("/")
        or image.endswith("/")
        or any(not part or part in {".", ".."} for part in image_parts)
        or ":" in image_parts[-1]
    ):
        raise PinCheckError(
            "remote Docker Action image must be canonical and must not include "
            "a mutable tag"
        )


def _external_record(
    reference: str,
    *,
    workflow: str,
    line_number: int,
) -> dict[str, Any] | None:
    if "${{" in reference:
        raise PinCheckError("dynamic expressions are not permitted in uses references")
    if reference.startswith("./"):
        return None
    if reference.startswith("docker://"):
        _docker_reference(reference)
        return {
            "kind": "docker",
            "line": line_number,
            "reference": reference,
            "workflow": workflow,
        }
    repository, commit = _github_reference(reference)
    return {
        "commit": commit,
        "kind": "github",
        "line": line_number,
        "reference": reference,
        "repository": repository,
        "workflow": workflow,
    }


def _workflow_files(root: Path) -> list[Path]:
    workflows = root / ".github" / "workflows"
    if workflows.is_symlink() or not workflows.is_dir():
        raise PinCheckError(
            "workflow directory is missing or not a regular directory: "
            ".github/workflows"
        )
    paths: list[Path] = []
    try:
        candidates = sorted(
            workflows.rglob("*"),
            key=lambda path: _display_path(path, root),
        )
    except OSError as exc:
        raise PinCheckError("workflow directory cannot be enumerated") from exc
    for path in candidates:
        if path.suffix not in {".yml", ".yaml"}:
            continue
        display = _display_path(path, root)
        if path.is_symlink() or not path.is_file():
            raise PinCheckError(
                f"workflow is missing or not a regular file: {display}"
            )
        paths.append(path)
    return sorted(paths, key=lambda path: _display_path(path, root))


def _scan_workflow(path: Path, root: Path) -> list[dict[str, Any]]:
    display = _display_path(path, root)
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise PinCheckError(f"workflow cannot be read: {display}") from exc
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PinCheckError(f"workflow is not valid UTF-8: {display}") from exc
    if "\ufeff" in text:
        raise PinCheckError(f"workflow contains a UTF-8 BOM: {display}")
    if "\x00" in text:
        raise PinCheckError(f"workflow contains a NUL character: {display}")

    records: list[dict[str, Any]] = []
    block_scalar_key_indent: int | None = None
    block_scalar_content_indent: int | None = None
    for line_number, line in enumerate(text.splitlines(), start=1):
        if block_scalar_key_indent is not None:
            if not line.strip():
                continue
            indentation = len(line) - len(line.lstrip(" "))
            if block_scalar_content_indent is None:
                if indentation > block_scalar_key_indent:
                    block_scalar_content_indent = indentation
                    continue
            elif indentation >= block_scalar_content_indent:
                continue
            block_scalar_key_indent = None
            block_scalar_content_indent = None

        if not line.strip() or line.lstrip(" \t").startswith("#"):
            continue
        code, quotes_balanced = _code_before_comment(line)
        if not code.strip():
            continue

        match = CANONICAL_USES_PATTERN.fullmatch(code)
        if match is not None:
            reference = match.group("reference")
            if MULTILINE_INDICATOR_PATTERN.fullmatch(reference) is not None:
                raise PinCheckError(
                    f"{display}:{line_number}: multiline uses values are not "
                    "permitted"
                )
            try:
                record = _external_record(
                    reference,
                    workflow=display,
                    line_number=line_number,
                )
            except PinCheckError as exc:
                raise PinCheckError(f"{display}:{line_number}: {exc}") from exc
            if record is not None:
                records.append(record)
            continue

        if _possible_uses_key(code, quotes_balanced):
            raise PinCheckError(
                f"{display}:{line_number}: uses must use the canonical "
                "single-line form 'uses: <reference>'"
            )
        if _has_noncanonical_mapping_key(code):
            raise PinCheckError(
                f"{display}:{line_number}: noncanonical YAML mapping-key "
                "syntax is not supported"
            )
        block_header = BLOCK_SCALAR_HEADER_PATTERN.fullmatch(code)
        if block_header is not None:
            sequence = block_header.group("sequence") or ""
            block_scalar_key_indent = len(block_header.group("indent")) + len(
                sequence
            )
            modifiers = block_header.group("modifiers") or ""
            indicator = next(
                (int(character) for character in modifiers if character.isdigit()),
                None,
            )
            block_scalar_content_indent = (
                None
                if indicator is None
                else block_scalar_key_indent + indicator
            )
    return records


def scan_workflows(
    repository_root: Path = REPOSITORY_ROOT,
) -> dict[str, Any]:
    """Return a deterministic success record or raise ``PinCheckError``."""

    try:
        root = repository_root.resolve(strict=True)
    except OSError as exc:
        raise PinCheckError("repository root is missing or inaccessible") from exc
    if not root.is_dir():
        raise PinCheckError("repository root is not a directory")

    paths = _workflow_files(root)
    workflow_names = [_display_path(path, root) for path in paths]
    references: list[dict[str, Any]] = []
    for path in paths:
        references.extend(_scan_workflow(path, root))
    references.sort(
        key=lambda item: (
            item["workflow"],
            item["line"],
            item["reference"],
            item["kind"],
        )
    )
    return {
        "external_reference_count": len(references),
        "external_references": references,
        "ok": True,
        "workflow_count": len(workflow_names),
        "workflows": workflow_names,
    }


def main(
    argv: Sequence[str] | None = None,
    *,
    repository_root: Path = REPOSITORY_ROOT,
) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments:
        _write_bytes(
            sys.stderr,
            b"check_github_action_pins: error: no arguments are accepted\n",
        )
        return 1
    try:
        result = scan_workflows(repository_root)
    except PinCheckError as exc:
        _write_bytes(
            sys.stderr,
            f"check_github_action_pins: error: {exc}\n".encode("utf-8"),
        )
        return 1
    _write_json_line(sys.stdout, result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
