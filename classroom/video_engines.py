"""Separate local transcription and disabled summarization contracts. No API calls."""
from typing import Protocol


class EngineUnavailable(Exception):
    pass


class Transcriber(Protocol):
    def transcribe(self, audio_path: str, *, deadline: float, on_event, on_tick) -> dict: ...


class Summarizer(Protocol):
    def summarize(self, transcript: str, language: str) -> dict: ...


class DisabledTranscriber:
    def transcribe(self, audio_path):
        raise EngineUnavailable('Transcription is disabled and unverified.')


class DisabledSummarizer:
    def summarize(self, transcript, language):
        raise EngineUnavailable('Summarization is disabled and unverified.')


def get_transcriber() -> Transcriber:
    from .local_transcriber import LocalWhisperTranscriber
    return LocalWhisperTranscriber()


def get_summarizer() -> Summarizer:
    return DisabledSummarizer()


FUTURE_TEXT_RETENTION_DAYS = 7  # Transcript retention is active; summaries stay disabled.
