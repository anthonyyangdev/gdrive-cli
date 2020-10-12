from typing import TypedDict, List, Optional

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory

from src.prompt.AutoCompleter import AutoCompleter


class InputPrompt(TypedDict):
    cmd: str
    options: List[str]
    argument: Optional[str]


class InputOption(TypedDict):
    option: str
    args: List[str]


class UserInputPrompt(TypedDict):
    cmd: str
    options: List[InputPrompt]
    main_arg: str


def get_prompt(pathway: str, history_path: str, autocompletion: List[str]) -> UserInputPrompt:
    user_input = prompt(f"GDrive ∞/{pathway}> ",
                        # history=FileHistory(history_path),
                        completer=AutoCompleter(autocompletion),
                        ).strip().split(' ')
    pass


def accept(pathway: str, history_path: str, autocomplete_options: List[str]) -> InputPrompt:
    user_input = prompt(f"GDrive ∞/{pathway}> ",
                        history=FileHistory(history_path),
                        completer=AutoCompleter(autocomplete_options),
                        ).strip().split(' ')
    cmd = user_input[0]
    if "--" in user_input:
        break_point = user_input.index("--")
        options = user_input[1:break_point]
        argument = " ".join(user_input[break_point + 1:])
    else:
        options = []
        args = []
        for i in user_input[1:]:
            if i.startswith("-"):
                options.append(i)
            else:
                args.append(i)
        argument = " ".join(args)
    return {
        'cmd': cmd,
        'options': options,
        'argument': argument
    }
