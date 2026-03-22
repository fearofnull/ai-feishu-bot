# -*- coding: utf-8 -*-
"""Cron task executor."""
import asyncio
from typing import Any, Optional

from .models import CronJobRequest, CronJobRequestInput, CronJobSpec


class CronExecutor:
    """Execute cron jobs (text or agent)."""

    def __init__(self, runner: Any, channel_manager: Any):
        """Initialize executor.

        Args:
            runner: Async runner used for agent tasks.
            channel_manager: Channel manager used to send messages.
        """
        self._runner = runner
        self._channel_manager = channel_manager

    async def execute(self, job: CronJobSpec) -> None:
        """Execute a cron job."""
        if job.task_type == "text":
            await self._execute_text_task(job)
        elif job.task_type == "agent":
            await self._execute_agent_task(job)
        else:
            raise ValueError(f"Unsupported task type: {job.task_type}")

    async def _execute_text_task(self, job: CronJobSpec) -> None:
        """Execute a text task."""
        if not job.text:
            raise ValueError("Text task requires non-empty text")

        target_chat_id = job.dispatch.target.chat_id
        target_user_id = job.dispatch.target.user_id

        if not target_chat_id and not target_user_id:
            raise ValueError("chat_id or user_id is required")

        await self._send_message(
            channel=job.dispatch.channel,
            chat_id=target_chat_id,
            user_id=target_user_id,
            content=job.text,
            mode=job.dispatch.mode,
        )

    async def _execute_agent_task(self, job: CronJobSpec) -> None:
        """Execute an agent task."""
        request = job.request
        if not request:
            if job.text:
                request = self._build_request_from_text(job.text)
            else:
                raise ValueError("Agent task requires request")

        try:
            response = await asyncio.wait_for(
                self._runner.run(
                    input=request.input,
                    session_id=request.session_id,
                    user_id=request.user_id,
                ),
                timeout=job.runtime.timeout_seconds,
            )
        except asyncio.TimeoutError:
            response = f"Task timed out after {job.runtime.timeout_seconds} seconds"
        except Exception as exc:
            response = f"Task failed: {str(exc)}"

        response = self._normalize_agent_response(response)

        target_chat_id = job.dispatch.target.chat_id
        target_user_id = job.dispatch.target.user_id

        await self._send_message(
            channel=job.dispatch.channel,
            chat_id=target_chat_id,
            user_id=target_user_id,
            content=response,
            mode=job.dispatch.mode,
        )

    def _build_request_from_text(self, text: str) -> CronJobRequest:
        """Build a minimal agent request from plain text."""
        return CronJobRequest(
            input=[
                CronJobRequestInput(
                    role="user",
                    type="text",
                    content=[{"type": "text", "text": text}],
                )
            ],
            session_id=None,
            user_id="cron",
        )

    def _normalize_agent_response(self, response: Any) -> str:
        """Normalize agent runner response to a string."""
        if response is None:
            return ""
        if isinstance(response, str):
            return response
        if hasattr(response, "stdout"):
            try:
                return str(response.stdout or "")
            except Exception:
                return ""
        if hasattr(response, "content"):
            content = getattr(response, "content", None)
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, dict):
                        text = item.get("text")
                        if text:
                            parts.append(str(text))
                    else:
                        parts.append(str(item))
                return "".join(parts)
        return str(response)

    async def _send_message(
        self,
        channel: str,
        chat_id: Optional[str],
        user_id: Optional[str],
        content: str,
        mode: str,
        msg_type: str = "post",
    ) -> None:
        """Send a message via channel manager."""
        if self._channel_manager:
            try:
                await self._channel_manager.send_message(
                    channel=channel,
                    chat_id=chat_id,
                    user_id=user_id,
                    content=content,
                    mode=mode,
                    msg_type=msg_type,
                )
            except Exception as exc:
                print(f"Failed to send message: {str(exc)}")
