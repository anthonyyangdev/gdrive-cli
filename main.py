import os
import pathlib
import subprocess

import pickle
import os.path

from src.ReferenceVar import ReferenceVar
from src.drive.GDriveApi import GDriveApi, Credentials, login, get_login_token_opt, logout
from src.prompt.Prompt import accept


def main(creds: ReferenceVar[Credentials]):
    """
    Performs the Google Drive CLI file system navigation.
    """
    api = GDriveApi(creds.value)
    online: ReferenceVar[bool] = ReferenceVar(True)
    current_directory = pathlib.Path(__file__).parent.absolute()
    history_path = os.path.join(current_directory, 'history.txt')

    def handle_logout():
        logout(creds)
        creds.value = None
        online.value = None

    while online.value:
        pathway = api.get_current_path_string()
        options = {
            'cd': lambda arg: api.cd(arg),
            'typeof': lambda arg: print(api.typeof(arg)),
            'download': lambda arg: api.download(arg),
            'ls': lambda _: print(api.ls()),
            'quit': lambda _: exit(0),
            'switch': (lambda _: handle_logout()),
            'current': lambda _: print(pathway),
            'record': lambda arg: api.record_filenames(arg),
            'exec': lambda arg: subprocess.call(arg, shell=True)
        }
        autocomplete_options = list(options.keys()) + api.get_names()
        try:
            user_input = accept(pathway, history_path, autocomplete_options)
            if user_input['cmd'] in options:
                options[user_input['cmd']](user_input['argument'])
            else:
                print(f"Unknown command {user_input['cmd']}")
        except KeyboardInterrupt:
            pass


def start():
    """
    The first window of the GDrive CLI. Logs a user into a Google account.
    If a login token already exists, then this step is skipped and goes to the file system.
    """
    creds: ReferenceVar[Credentials] = ReferenceVar(get_login_token_opt())
    current_directory = pathlib.Path(__file__).parent.absolute()
    history_path = os.path.join(current_directory, 'history.txt')
    # If there are no (valid) credentials available, let the user log in.
    while not creds.value or not creds.value.valid:
        options = {
            "login": lambda: login(creds),
            "quit": lambda: exit(0)
        }
        try:
            user_input = accept('', history_path, list(options.keys()))
            if user_input['cmd'] in options:
                options[user_input['cmd']]()
                main(creds)
            else:
                print("Invalid input")
        except KeyboardInterrupt:
            pass
    else:
        main(creds)


if __name__ == "__main__":
    start()
