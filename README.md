# Journal.bh Assignment Agent

Python CLI application for automatically solving and submitting Journal.bh assignments.

The agent uses a LangGraph workflow, Journal.bh API, a local git repository for solutions, and an OpenAI-compatible LLM endpoint.

## Features

- Loads Journal.bh OpenAPI schema from `SWAGGER_URL` or `SWAGGER_FILE_PATH`.
- Authenticates with `Authorization: Bearer <JOURNAL_API_TOKEN>`.
- Fetches submissions from `/api/v2/submission/my`.
- Skips assignments that are already accepted or waiting for review.
- Processes remaining assignments one by one.
- Creates or reuses a separate git branch for each assignment.
- Generates repository changes through structured LLM responses.
- Runs sanity checks and LLM diff review before commit.
- Creates a git commit for each assignment.
- Pushes the assignment branch to GitHub.
- Saves commit metadata in Journal.bh.
- Writes the commit link to the submission answer.
- Submits the assignment for review.
- Shows formatted Rich console output for progress and results.

## Project Structure

```text
agent/
  main.py                 CLI entry point
  config.py               Runtime settings
  graph.py                LangGraph workflow
  llm.py                  LLM wrapper
  state.py                Graph state
  ui.py                   Rich console UI

  api/
    journal.py            Journal.bh API client
    openapi_loader.py     Swagger/OpenAPI loader

  nodes/
    assignments.py        Task/submission loading and selection
    analyze.py            Assignment analysis and planning
    branches.py           Per-assignment branch naming and checkout
    edit.py               Repository editing and repair
    git_ops.py            Commit and push operations
    review.py             Sanity checks and LLM diff review
    submit.py             Commit metadata and submission

  tools/
    checks.py             compileall and git diff checks
    git.py                Git subprocess wrapper
    repo_fs.py            Safe repository file operations

prompts/
  analyze_assignment.md
  plan_changes.md
  edit_repository.md
  repair_repository.md
  review_diff.md
```

## Installation

```bash
python -m pip install -e .
```

Python 3.11 or newer is required.

## Configuration

Create a local `.env` file. Do not commit it.

Example:

```env
SWAGGER_URL=https://example.com/openapi.json
SWAGGER_FILE_PATH=
JOURNAL_API_BASE_URL=https://platform.brojs.ru/jrnl-bh
JOURNAL_API_TOKEN=...
COURSE_ID=...

LOCAL_REPO_PATH=...
GITHUB_REPO_URL=...
GIT_AUTHOR_NAME=assignment-agent
GIT_AUTHOR_EMAIL=assignment-agent@example.local

LLM_BASE_URL=...
LLM_API_KEY=...
LLM_MODEL=openai/gpt-oss-120b
LLM_MAX_TOKENS=8192

DRY_RUN=false
LOCAL_SUBMIT=false
PUSH_CHANGES=true
SAVE_COMMIT_METADATA_TO_JOURNAL=true
SUBMIT_TO_JOURNAL=true

FORCE_REPROCESS=false
IGNORE_LOCAL_REPORTS=false
INCLUDE_DONE_SUBMISSIONS=false
MAX_REPAIR_ATTEMPTS=5
ADOPT_EXISTING_CHANGES=false
REQUEST_TIMEOUT_SECONDS=60
```

If `SWAGGER_URL` is set, it is preferred. If it is empty, the agent reads `SWAGGER_FILE_PATH`. A local Swagger file can be kept outside git and should not be committed.

`LOCAL_REPO_PATH` must point to the git repository where assignment solutions will be created.

## Run

```bash
python -m agent.main run
```

or:

```bash
journal-agent run
```

## Assignment Branches

Each assignment is solved in its own branch:

```text
assignment-agent/task/<short-task-id>-<title-slug>
```

Branch selection logic:

- if the branch exists locally, the agent checks it out;
- if it exists on `origin`, the agent fetches and checks it out;
- otherwise, the agent creates it from the repository root commit.

This keeps solutions for different assignments isolated from each other.

## Workflow

The LangGraph workflow runs these stages:

```text
load_api_schema
fetch_tasks
fetch_my_submissions
select_next_assignment
load_task_details
analyze_assignment
plan_code_changes
edit_repository
run_sanity_checks
review_diff
commit_changes
push_changes
save_commit_metadata
submit_assignment
print_summary
```

After every submitted assignment, the agent fetches submissions again so it works with fresh statuses.

## Repository Editing

The LLM does not edit files directly. It returns structured JSON operations, and the agent applies them through safe local tools:

```text
write_file
apply_patch
create_directory
```

The file tools refuse paths outside `LOCAL_REPO_PATH` and refuse edits to `.env` and `.env.example`.

## Checks

Before commit, the agent runs:

```bash
python -m compileall .
git diff --check
```

It also performs an LLM review of the final diff against the assignment requirements. If checks or review fail, the agent runs a repair loop up to `MAX_REPAIR_ATTEMPTS`.

## Submission

For every successful assignment, the agent:

1. creates a git commit;
2. pushes the assignment branch;
3. saves commit metadata through `/api/v2/submission/{submissionId}/commit-data`;
4. updates the submission answer with a GitHub commit link;
5. submits the assignment through `/api/v2/submission/{submissionId}/submit`.

The submitted answer uses:

```json
{
  "answerType": "link",
  "content": "https://github.com/<owner>/<repo>/commit/<commitSha>"
}
```

## Safety

- Secrets are read from local environment files and are not printed.
- `.env` and `.env.example` are not edited by the agent.
- Deprecated `/api/submission/...` endpoints are not used.
- The agent writes assignment solutions only inside `LOCAL_REPO_PATH`.
