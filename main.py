import os
import subprocess
from typing import Any

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory

from src.AutoCompleter import AutoCompleter

import pickle
import os.path

from src.ReferenceVar import ReferenceVar
from src.drive.GDriveApi import GDriveApi

SCOPES = ['https://www.googleapis.com/auth/drive']


def main(creds):
    """
    Performs the Google Drive CLI file system navigation.
    """
    api = GDriveApi(creds)
    online: ReferenceVar[bool] = ReferenceVar(True)

    def remove_login_token():
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')
        online.value = False

    while online.value:
        options = {
            'cd': lambda cmd: api.cd(" ".join(cmd[1:])),
            'typeof': lambda cmd: print(api.typeof(" ".join(cmd[1:]))),
            'download': lambda cmd: api.download(" ".join(cmd[1:])),
            'ls': lambda _: print(api.ls()),
            'quit': lambda _: exit(0),
            'switch': lambda _: remove_login_token(),
            'current': lambda _: print(api.get_current_path_string()),
            'record': lambda _: api.record_filenames(),
            'exec': lambda cmd: subprocess.call(" ".join(cmd[1:]), shell=True)
        }

        autocomplete_options = list(options.keys()) + api.get_names()
        pathway = api.get_current_path_string()
        try:
            user_input = prompt(f"GDrive ∞/{pathway}> ",
                                history=FileHistory('history.txt'),
                                completer=AutoCompleter(autocomplete_options),
                                ).strip().split(' ')
            if user_input[0] in options:
                options[user_input[0]](user_input)
            else:
                print(f"Unknown command {user_input[0]}")
        except KeyboardInterrupt:
            pass


def login(credentials: ReferenceVar[Any]):
    """
    Performs Google login and saves login information in a token.
    """
    if credentials.value and credentials.value.expired and credentials.value.refresh_token:
        credentials.value.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        credentials.value = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(credentials.value, token)


def start():
    """
    The first window of the GDrive CLI. Logs a user into a Google account.
    If a login token already exists, then this step is skipped and goes to the file system.
    """
    creds: ReferenceVar[Any] = ReferenceVar()
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds.value = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    while not creds.value or not creds.value.valid:
        options = {
            "login": lambda: login(creds),
            "quit": lambda: exit(0)
        }
        user_input = prompt('GDrive ∞> ',
                            history=FileHistory('history.txt'),
                            completer=AutoCompleter(list(options.keys())),
                            ).strip()
        if user_input in options:
            options[user_input]()
            main(creds.value)
        else:
            print("Invalid input")
    else:
        main(creds.value)


if __name__ == "__main__":
    start()
