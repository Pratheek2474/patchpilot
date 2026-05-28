from __future__ import annotations

from app.pipeline import stages
from app.services import github_service, patch_service, repo_service


async def run_pipeline(repo_full_name: str, issue_number: int, issue_title: str, issue_body: str) -> dict:
    """Run the full pipeline and return { pr_url, branch_name }."""
    repo_path = None
    try:
        repo_path = github_service.clone_repo(repo_full_name)

        tree = repo_service.get_directory_tree(repo_path)
        readme = repo_service.get_readme(repo_path)
        package_json = repo_service.get_package_json(repo_path)
        config_files = repo_service.get_important_files(repo_path)
        print(f"[PatchPilot] Analyzing Repository Structure:\n")
        repo_analysis = stages.analyze_repo(tree, readme, package_json, config_files)
        print(f"[PatchPilot] Analyzing Issue:\nTitle: {issue_title}\nBody: {issue_body[:200]}...")
        issue_analysis = stages.analyze_issue(issue_title, issue_body, repo_analysis)
        print(f"[PatchPilot] Looking for relevant files based on issue and repo analysis...")
        file_locations = stages.locate_files(repo_analysis, issue_analysis, tree)

        file_paths = [f.path for f in file_locations.files]
        print(f"[PatchPilot] Files read by AI: {file_paths}")
        file_contents = repo_service.get_file_contents(repo_path, file_paths)
        print(f"[PatchPilot] Generating patch based on issue analysis and file contents...")
        patch_result = stages.generate_patch(file_contents, issue_analysis, repo_analysis)
        pr_desc = stages.write_pr_description(issue_title, patch_result, issue_analysis)

        branch_name = f"patchpilot/issue-{issue_number}"
        github_service.create_branch(repo_path, branch_name)
        patch_service.apply_patches(repo_path, patch_result.patches)
        github_service.commit_changes(repo_path, pr_desc.title)
        github_service.push_branch(repo_path, branch_name)

        pr_url = github_service.create_pull_request(
            full_name=repo_full_name,
            branch_name=branch_name,
            title=pr_desc.title,
            body=pr_desc.body,
            issue_number=issue_number,
        )

        return {"pr_url": pr_url, "branch_name": branch_name}

    finally:
        if repo_path:
            github_service.cleanup_repo(repo_path)
