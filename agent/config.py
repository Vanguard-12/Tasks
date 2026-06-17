from __future__ import annotations

from pathlib import Path

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    swagger_url: str | None = Field(default=None, alias="SWAGGER_URL")
    swagger_file_path: Path | None = Field(default=Path("swagger.json"), alias="SWAGGER_FILE_PATH")

    journal_api_base_url: str = Field(
        default="https://platform.brojs.ru/jrnl-bh",
        alias="JOURNAL_API_BASE_URL",
    )
    journal_api_token: str = Field(default="", alias="JOURNAL_API_TOKEN")
    course_id: str = Field(default="", alias="COURSE_ID")

    github_token: str = Field(default="", alias="GITHUB_TOKEN")
    github_repo_url: str = Field(default="", alias="GITHUB_REPO_URL")
    local_repo_path: Path = Field(default=Path("."), alias="LOCAL_REPO_PATH")
    git_author_name: str = Field(default="assignment-agent", alias="GIT_AUTHOR_NAME")
    git_author_email: str = Field(default="assignment-agent@example.local", alias="GIT_AUTHOR_EMAIL")
    git_work_branch: str = Field(default="assignment-agent/mvp", alias="GIT_WORK_BRANCH")

    llm_base_url: str = Field(default="", alias="LLM_BASE_URL")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_model: str = Field(default="gpt-oss-120b", alias="LLM_MODEL")
    llm_max_tokens: int = Field(default=8192, alias="LLM_MAX_TOKENS")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    dry_run: bool = Field(default=True, alias="DRY_RUN")
    local_submit: bool = Field(default=True, alias="LOCAL_SUBMIT")
    push_changes: bool | None = Field(default=None, alias="PUSH_CHANGES")
    save_commit_metadata_to_journal: bool | None = Field(
        default=None,
        alias="SAVE_COMMIT_METADATA_TO_JOURNAL",
    )
    submit_to_journal: bool | None = Field(default=None, alias="SUBMIT_TO_JOURNAL")
    local_reports_dir: Path = Field(default=Path(".agent_reports"), alias="LOCAL_REPORTS_DIR")
    force_reprocess: bool = Field(default=False, alias="FORCE_REPROCESS")
    ignore_local_reports: bool = Field(default=False, alias="IGNORE_LOCAL_REPORTS")
    include_done_submissions: bool = Field(default=False, alias="INCLUDE_DONE_SUBMISSIONS")
    max_repair_attempts: int = Field(default=5, alias="MAX_REPAIR_ATTEMPTS")
    adopt_existing_changes: bool = Field(default=False, alias="ADOPT_EXISTING_CHANGES")

    request_timeout_seconds: float = Field(default=60.0, alias="REQUEST_TIMEOUT_SECONDS")

    @field_validator("local_repo_path", mode="before")
    @classmethod
    def default_empty_repo_path(cls, value: object) -> object:
        if value is None or value == "":
            return "."
        return value

    @computed_field
    @property
    def repo_path(self) -> Path:
        return self.local_repo_path.expanduser().resolve()

    def validate_runtime(self) -> list[str]:
        missing: list[str] = []
        if not self.course_id:
            missing.append("COURSE_ID")
        if not self.journal_api_token:
            missing.append("JOURNAL_API_TOKEN")
        if not self.llm_base_url:
            missing.append("LLM_BASE_URL")
        if not self.llm_api_key:
            missing.append("LLM_API_KEY")
        return missing

    def should_push_changes(self) -> bool:
        if self.dry_run:
            return False
        if self.push_changes is not None:
            return self.push_changes
        return not self.local_submit

    def should_save_commit_metadata_to_journal(self) -> bool:
        if self.dry_run:
            return False
        if self.save_commit_metadata_to_journal is not None:
            return self.save_commit_metadata_to_journal
        return not self.local_submit

    def should_submit_to_journal(self) -> bool:
        if self.dry_run:
            return False
        if self.submit_to_journal is not None:
            return self.submit_to_journal
        return not self.local_submit


def load_settings() -> Settings:
    env_file = ".env" if Path(".env").exists() else ".env.example"
    return Settings(_env_file=env_file)
