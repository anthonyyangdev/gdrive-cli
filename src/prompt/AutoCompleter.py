from enum import Enum
from typing import List, Iterable

from fuzzyfinder.main import fuzzyfinder
from prompt_toolkit.completion import Completer, Completion, CompleteEvent
from prompt_toolkit.document import Document


class AutoCompleter(Completer):

    def __init__(self, keywords: List[str]):
        self.keywords = keywords

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor(WORD=True)
        matches = fuzzyfinder(word_before_cursor, self.keywords)
        for m in matches:
            yield Completion(m, start_position=-len(word_before_cursor))


class AutoCompleteState(Enum):
    COMMAND = 1
    OPTION_OR_MAIN_ARG = 2
    OPTION_ARG = 3


class OptionAutoCompleter(Completer):

    def __init__(self, commands: List[str]):
        self.commands = commands
        self.current_command = None
        self.state: AutoCompleteState = AutoCompleteState.COMMAND

    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
        word_before_cursor = document.get_word_before_cursor(WORD=True)
        if self.state == AutoCompleteState.COMMAND:
            matches = fuzzyfinder(word_before_cursor, self.commands)
            for m in matches:
                yield Completion(m, start_position=-len(word_before_cursor))
        elif self.state == AutoCompleteState.OPTION_OR_MAIN_ARG:
            pass
