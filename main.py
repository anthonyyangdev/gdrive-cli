import pathlib

import os.path

from src.drive.GDriveApi import GDriveApi
from src.prompt.Prompt import accept

current_directory = pathlib.Path(__file__).parent.absolute()
history_path = os.path.join(current_directory, 'history.txt')


def main(api: GDriveApi):
    """
    Performs the Google Drive CLI file system navigation.
    """
    while api.active:
        pathway = api.get_current_path_string()
        options = api.get_options()
        autocomplete_options = list(options.keys()) + api.get_names()
        try:
            user_input = accept(pathway, history_path, autocomplete_options)
            if user_input['cmd'] in options:
                options[user_input['cmd']](user_input['argument'], user_input['options'])
            else:
                print(f"Unknown command {user_input['cmd']}")
        except KeyboardInterrupt:
            pass


def start():
    """
    The first window of the GDrive CLI. Logs a user into a Google account.
    If a login token already exists, then this step is skipped and goes to the file system.
    """
    api = GDriveApi()
    # If there are no (valid) credentials available, let the user log in.
    while api.credentials is None or not api.credentials.valid:
        options = {
            "login": lambda: api.login(),
            "quit": lambda: exit(0)
        }
        try:
            user_input = accept('', history_path, list(options.keys()))
            if user_input['cmd'] in options:
                options[user_input['cmd']]()
                main(api)
            else:
                print("Invalid input")
        except KeyboardInterrupt:
            pass
    else:
        main(api)


if __name__ == "__main__":
    start()
