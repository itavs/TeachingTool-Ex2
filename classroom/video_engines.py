"""Replaceable local transcription and summary engines; no external providers."""
from typing import Protocol


class EngineUnavailable(Exception):
    pass


class Transcriber(Protocol):
    def transcribe(self, audio_path: str, *, deadline: float, on_event, on_tick) -> dict: ...


class Summarizer(Protocol):
    def summarize(self, transcript: str, language: str, *, work_dir, deadline, on_event, on_tick) -> dict: ...


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
    from .local_summarizer import LocalQwenSummarizer
    return LocalQwenSummarizer()


FUTURE_TEXT_RETENTION_DAYS = 7  # Summaries never outlive their source transcript.
