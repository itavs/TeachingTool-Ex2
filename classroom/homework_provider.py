"""Replaceable homework contract; experimental local English provider, no runtime fake."""
from typing import Protocol


class ReviewUnavailable(Exception):
    pass


class HomeworkReviewer(Protocol):
    def available(self, language: str) -> bool: ...
    def assess_submission(self, instructions: str, criteria: list, submission: str, language: str) -> dict: ...
    def compare_submissions(self, instructions: str, criteria: list, target: str, peers: list, language: str) -> dict: ...


class DisabledHomeworkReviewer:
    def available(self, language):
        return False

    def assess_submission(self, *args):
        raise ReviewUnavailable('No accepted homework provider is active.')

    def compare_submissions(self, *args):
        raise ReviewUnavailable('No accepted comparison provider is active.')


def get_homework_reviewer() -> HomeworkReviewer:
    from .local_homework_reviewer import LocalHomeworkReviewer
    return LocalHomeworkReviewer()
