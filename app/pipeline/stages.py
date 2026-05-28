"""Pipeline stages — AI-powered analysis and code generation."""

from __future__ import annotations

import json

from app.models.schemas import FileLocations, IssueAnalysis, PatchResult, PRDescription, RepoAnalysis
from app.services.ai_service import ai_service


def analyze_repo(tree: str, readme: str | None, package_json: dict | None, config_files: dict | None = None) -> RepoAnalysis:
    config_str = "None found"
    if config_files:
        parts = [f"### {name}\n```\n{content[:2000]}\n```" for name, content in config_files.items() if content]
        config_str = "\n\n".join(parts) or "None found"

    pkg_summary = "Not found"
    if package_json:
        pkg_summary = json.dumps(
            {k: v for k, v in package_json.items() if k in {"name", "description", "dependencies", "devDependencies", "scripts"}},
            indent=2,
        )

    return ai_service.chat_structured(
        system_prompt="You are an expert software architect. Analyze the repository structure and produce a concise structured summary of its framework, language, architecture, key directories, key files, and build system.",
        user_prompt=f"## Directory Tree\n```\n{tree[:5000]}\n```\n\n## README\n```\n{readme[:3000] if readme else 'Not found'}\n```\n\n## package.json\n```\n{pkg_summary}\n```\n\n## Config Files\n{config_str}",
        response_model=RepoAnalysis,
    )


def analyze_issue(issue_title: str, issue_body: str, repo_analysis: RepoAnalysis) -> IssueAnalysis:
    return ai_service.chat_structured(
        system_prompt="You are an expert software engineer. Analyze the GitHub issue, determine the root cause, write a focused implementation plan, and assess category, complexity (trivial/small/medium), and confidence.",
        user_prompt=f"## Repository\n{repo_analysis.architecture_summary}\n\n## Issue: {issue_title}\n{issue_body or '(No description)'}",
        response_model=IssueAnalysis,
    )


def locate_files(repo_analysis: RepoAnalysis, issue_analysis: IssueAnalysis, tree: str) -> FileLocations:
    return ai_service.chat_structured(
        system_prompt="You are an expert at navigating codebases. Identify which files need to be modified or read to resolve the issue. Max 8 files, ranked by relevance. Only include files that exist in the tree.",
        user_prompt=f"## Repository\n{repo_analysis.architecture_summary}\n\n## Issue\nCategory: {issue_analysis.category}\nRoot cause: {issue_analysis.root_cause}\nPlan: {issue_analysis.implementation_plan}\n\n## Directory Tree\n```\n{tree[:5000]}\n```",
        response_model=FileLocations,
    )


def generate_patch(file_contents: dict[str, str], issue_analysis: IssueAnalysis, repo_analysis: RepoAnalysis) -> PatchResult:
    files_str = "\n\n".join(f"### `{path}`\n```\n{content}\n```" for path, content in file_contents.items())
    return ai_service.chat_structured(
        system_prompt="You are an expert software engineer. Generate EXACT minimal file modifications to fix the issue. original_content must match the file exactly. modified_content is the complete new file. Preserve code style. No unrelated changes.",
        user_prompt=f"## Issue\nCategory: {issue_analysis.category}\nRoot cause: {issue_analysis.root_cause}\nPlan: {issue_analysis.implementation_plan}\n\n## Repo\n{repo_analysis.architecture_summary}\n\n## Files\n{files_str}",
        response_model=PatchResult,
        max_tokens=16384,
    )


def write_pr_description(issue_title: str, patch_result: PatchResult, issue_analysis: IssueAnalysis) -> PRDescription:
    patch_summary = "\n".join(f"- `{p.file_path}`: {p.change_summary}" for p in patch_result.patches)
    return ai_service.chat_structured(
        system_prompt="You are a senior engineer. Write a concise PR title (conventional commit format) and a clear markdown description with ## Summary, ## Changes, ## Testing sections.",
        user_prompt=f"## Issue\n{issue_title}\n\n## Changes\n{patch_summary}\n\n## Reasoning\n{issue_analysis.root_cause}",
        response_model=PRDescription,
    )
