"""Pydantic schemas for API requests, responses, and AI structured outputs."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── AI Structured Output Schemas ─────────────────────────────────────────────


class RepoAnalysis(BaseModel):
    """Structured output from repository analysis stage."""

    framework: str = Field(description="Primary framework, e.g. 'Next.js 14 with App Router'")
    language: str = Field(description="Primary language, e.g. 'TypeScript'")
    architecture_summary: str = Field(description="High-level architecture description")
    key_directories: list[str] = Field(description="Important directories in the project")
    key_files: list[str] = Field(description="Important files (configs, entry points)")
    build_system: str = Field(default="", description="Build tool / package manager")


class IssueAnalysis(BaseModel):
    """Structured output from issue analysis stage."""

    category: str = Field(description="One of: bug_fix, ui_fix, config_fix, typo_fix, feature_addition, refactor")
    root_cause: str = Field(description="Probable root cause or issue explanation")
    implementation_plan: str = Field(description="Step-by-step plan to fix the issue")
    complexity: str = Field(description="One of: trivial, small, medium")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the analysis (0.0 – 1.0)")


class FileRelevance(BaseModel):
    """A single file identified as relevant to an issue."""

    path: str = Field(description="Relative file path from repo root")
    relevance: str = Field(description="Why this file is relevant")
    action: str = Field(description="One of: modify, read_only")


class FileLocations(BaseModel):
    """Structured output from file locator stage."""

    files: list[FileRelevance] = Field(description="Relevant files ranked by importance")
    reasoning: str = Field(description="Explanation of file selection logic")


class FilePatch(BaseModel):
    """A single file modification."""

    file_path: str = Field(description="Relative file path from repo root")
    original_content: str = Field(description="Original file content (for validation)")
    modified_content: str = Field(description="New file content after modification")
    change_summary: str = Field(description="Brief description of what was changed")


class PatchResult(BaseModel):
    """Structured output from patch generation stage."""

    patches: list[FilePatch] = Field(description="List of file modifications")
    explanation: str = Field(description="Overall explanation of the fix")


class PRDescription(BaseModel):
    """Structured output from PR writer stage."""

    title: str = Field(description="PR title, e.g. 'fix: resolve mobile button alignment'")
    body: str = Field(description="Full PR description in markdown")
    labels: list[str] = Field(default_factory=list, description="Suggested PR labels")
