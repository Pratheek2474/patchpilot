from __future__ import annotations

from pathlib import Path

from app.models.schemas import FilePatch


def _content_matches(current: str, expected: str) -> bool:
    if current.strip() == expected.strip():
        return True
    # Lenient: ignore blank-line differences
    def non_blank(text: str) -> list[str]:
        return [l for l in text.strip().splitlines() if l.strip()]
    return non_blank(current) == non_blank(expected)


def apply_patches(repo_path: Path, patches: list[FilePatch]) -> None:
    for patch in patches:
        file_path = repo_path / patch.file_path
        # if file_path.exists():
        #     current = file_path.read_text(encoding="utf-8")
        #     if not _content_matches(current, patch.original_content):
        #         raise ValueError(
        #             f"Patch validation failed for {patch.file_path}: "
        #             "file content doesn't match what the AI expected."
        #         )
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(patch.modified_content, encoding="utf-8")
