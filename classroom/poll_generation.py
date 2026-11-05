"""Replaceable generation contract. Normal application has no working AI provider."""
from typing import Protocol


class GenerationUnavailable(Exception):
    pass


class PollGenerator(Protocol):
    def generate(self, material: str, kind: str, language: str) -> dict:
        """Return question/options and comprehension-only answer/explanation."""
        ...


class DisabledPollGenerator:
    def generate(self, material, kind, language):
        raise GenerationUnavailable('Real AI generation is not active or verified. No draft was generated. You can retry after a real provider is integrated.')


def get_poll_generator() -> PollGenerator:
    # No environment switch, credentials, HTTP, SDK or fake-provider fallback.
    return DisabledPollGenerator()
