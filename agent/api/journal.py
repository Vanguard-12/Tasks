from __future__ import annotations

from typing import Any

import httpx


class JournalAPIError(RuntimeError):
    pass


class JournalClient:
    def __init__(self, *, base_url: str, token: str, timeout: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._headers = {"Authorization": f"Bearer {token}"} if token else {}

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=self.timeout, headers=self._headers) as client:
            response = await client.request(method, url, params=params, json=json)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            body = response.text[:500]
            raise JournalAPIError(
                f"Journal API {method} {path} failed with HTTP {response.status_code}: {body}"
            ) from exc
        if not response.content:
            return None
        return response.json()

    async def list_tasks(self, course_id: str) -> Any:
        return await self._request("GET", f"/api/task/list/{course_id}")

    async def get_task(self, task_id: str) -> Any:
        return await self._request("GET", f"/api/task/{task_id}")

    async def my_submissions(self, course_id: str) -> Any:
        return await self._request("GET", "/api/v2/submission/my", params={"courseId": course_id})

    async def get_submission(self, submission_id: str) -> Any:
        return await self._request("GET", f"/api/v2/submission/{submission_id}")

    async def update_submission(self, submission_id: str, *, content: str, answer_type: str = "link") -> Any:
        return await self._request(
            "PUT",
            f"/api/v2/submission/{submission_id}",
            json={"answerType": answer_type, "content": content},
        )

    async def save_commit_metadata(self, submission_id: str, payload: dict[str, Any]) -> Any:
        return await self._request(
            "PATCH",
            f"/api/v2/submission/{submission_id}/commit-data",
            json=payload,
        )

    async def submit(self, submission_id: str) -> Any:
        return await self._request("POST", f"/api/v2/submission/{submission_id}/submit")

