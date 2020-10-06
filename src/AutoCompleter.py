from typing import List

from fuzzyfinder.main import fuzzyfinder
from prompt_toolkit.completion import Completer, Completion


class AutoCompleter(Completer):

    def __init__(self, keywords: List[str]):
        self.keywords = keywords

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor(WORD=True)
        matches = fuzzyfinder(word_before_cursor, self.keywords)
        for m in matches:
            yield Completion(m, start_position=-len(word_before_cursor))
