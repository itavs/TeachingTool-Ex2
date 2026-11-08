"""Separate future contracts; no model, HTTP, credentials or runtime fake option."""
from typing import Protocol


class EngineUnavailable(Exception):
    pass


class Transcriber(Protocol):
    def transcribe(self, audio_path: str) -> dict: ...


class Summarizer(Protocol):
    def summarize(self, transcript: str, language: str) -> dict: ...


class DisabledTranscriber:
    def transcribe(self, audio_path):
        raise EngineUnavailable('Transcription is disabled and unverified.')


class DisabledSummarizer:
    def summarize(self, transcript, language):
        raise EngineUnavailable('Summarization is disabled and unverified.')


def get_transcriber() -> Transcriber:
    return DisabledTranscriber()


def get_summarizer() -> Summarizer:
    return DisabledSummarizer()


FUTURE_TEXT_RETENTION_DAYS = 7  # No transcript/summary is produced or stored yet.
