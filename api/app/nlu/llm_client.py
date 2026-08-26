"""Provider-isolated client for converting messages into validated NLU results."""

import json
from collections.abc import Mapping
from typing import Any, Protocol

import httpx
from pydantic import ValidationError

from app.config.settings import Settings
from app.nlu.schemas import NLUResult


class LLMClientError(Exception):
    """Base class for safe-to-report NLU client errors."""


class LLMConfigurationError(LLMClientError):
    """Raised when the configured provider cannot be used."""


class LLMProviderError(LLMClientError):
    """Raised when a provider cannot complete a request."""


class LLMTimeoutError(LLMProviderError):
    """Raised when a provider request exceeds its timeout."""


class MalformedLLMResponseError(LLMClientError):
    """Raised when model output cannot be trusted as an NLU result."""


class LLMProvider(Protocol):
    """Minimal provider boundary used by the NLU client."""

    async def complete(self, system_prompt: str, user_payload: Mapping[str, Any]) -> str:
        """Return a structured-output response as text."""


class OpenAICompatibleProvider:
    """HTTP implementation for providers exposing a Chat Completions-compatible API."""

    def __init__(self, settings: Settings) -> None:
        if not settings.llm_api_key or not settings.llm_base_url or not settings.llm_model:
            raise LLMConfigurationError(
                "LLM_API_KEY, LLM_BASE_URL, and LLM_MODEL must be configured."
            )
        self._api_key = settings.llm_api_key.get_secret_value()
        self._base_url = settings.llm_base_url.rstrip("/")
        self._model = settings.llm_model
        self._timeout_seconds = settings.llm_timeout_seconds

    async def complete(self, system_prompt: str, user_payload: Mapping[str, Any]) -> str:
        request_url = f"{self._base_url}/chat/completions"
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload)},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0,
        }
        headers = {"Authorization": f"Bearer {self._api_key}"}

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(request_url, json=payload, headers=headers)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise LLMTimeoutError("The LLM provider timed out.") from exc
        except httpx.HTTPError as exc:
            raise LLMProviderError("The LLM provider request failed.") from exc

        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise MalformedLLMResponseError(
                "The LLM provider returned an unexpected response format."
            ) from exc

        if not isinstance(content, str):
            raise MalformedLLMResponseError("The LLM response content was not text.")
        return content


class LLMClient:
    """Coordinates prompt loading, provider calls, and NLU schema validation."""

    def __init__(self, provider: LLMProvider, system_prompt: str) -> None:
        self._provider = provider
        self._system_prompt = system_prompt

    async def analyze_message(
        self,
        message: str,
        conversation_context: list[dict[str, Any]] | None = None,
    ) -> NLUResult:
        """Interpret a message without performing actions or authorization."""
        raw_output = await self._provider.complete(
            self._system_prompt,
            {
                "message": message,
                "conversation_context": conversation_context or [],
            },
        )
        return self._validate_output(raw_output)

    @staticmethod
    def _validate_output(raw_output: str) -> NLUResult:
        try:
            payload = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise MalformedLLMResponseError("The LLM response was not valid JSON.") from exc

        try:
            return NLUResult.model_validate(payload)
        except ValidationError as exc:
            raise MalformedLLMResponseError(
                "The LLM response did not match the NLU schema."
            ) from exc


def create_llm_client(settings: Settings) -> LLMClient:
    """Create the configured NLU client without leaking provider details to callers."""
    provider_name = (settings.llm_provider or "").lower()
    if provider_name not in {"deepseek", "openai_compatible"}:
        raise LLMConfigurationError(
            "LLM_PROVIDER must be 'deepseek' or 'openai_compatible'."
        )
    prompt_path = __file__.parent / "prompts" / "nlu_system.txt"
    return LLMClient(OpenAICompatibleProvider(settings), prompt_path.read_text(encoding="utf-8"))
