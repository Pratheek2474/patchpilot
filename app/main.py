"""PatchPilot — FastAPI application.

Run with: uvicorn app.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.pipeline.orchestrator import run_pipeline
from app.services import github_service


app = FastAPI(
    title="PatchPilot",
    description="AI-powered GitHub issue resolution bot.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SolveRequest(BaseModel):
    repo: str = Field(..., description="Full repo name, e.g. 'owner/repo'")
    issue_number: int = Field(..., description="GitHub issue number")


class SolveResponse(BaseModel):
    status: str
    repo: str
    issue_number: int
    pr_url: str | None = None
    branch_name: str | None = None
    message: str


@app.post("/solve", response_model=SolveResponse)
async def solve_issue(req: SolveRequest) -> SolveResponse:
    """POST repo + issue_number → run the AI pipeline → return the PR URL."""
    try:
        issue_data = github_service.get_issue(req.repo, req.issue_number)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch issue: {e}")

    try:
        print(f"[PatchPilot] Working on the issue - {req.repo}#{req.issue_number}: {issue_data['title']}")
        result = await run_pipeline(
            repo_full_name=req.repo,
            issue_number=req.issue_number,
            issue_title=issue_data["title"],
            issue_body=issue_data.get("body") or "",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")

    return SolveResponse(
        status="completed",
        repo=req.repo,
        issue_number=req.issue_number,
        pr_url=result["pr_url"],
        branch_name=result["branch_name"],
        message=f"PR created: {result['pr_url']}",
    )
