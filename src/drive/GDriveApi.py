import io
import os
import pathlib
import pickle
from typing import TypedDict, Dict, Callable, Optional, List

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from src.ReferenceVar import ReferenceVar
from src.prompt import ColorText


class Credentials:
    expired: bool
    refresh: Callable[[Request], None]
    refresh_token: str
    valid: bool


class GDriveItem(TypedDict):
    id: str
    name: str
    mimeType: str


class GDriveApi:
    """
    A wrapper interface of the Google Drive API.
    """

    def __init__(self, credentials: Credentials):
        self.service = build('drive', 'v3', credentials=credentials)
        self.folder_stack = []
        self.drive_items: Dict[str, GDriveItem] = {'root': {'id': 'root'}}
        self.cache = {}
        self.cd('root')

    def cd(self, folder_name: str):
        """
        Changes the directory to the relative directory specified by [folder_name].
        :param folder_name:
        :return:
        """
        folder_id: str
        if folder_name == '..' and len(self.folder_stack) > 1:
            self.folder_stack.pop()
            parent = self.folder_stack[len(self.folder_stack) - 1]
            folder_id = parent['id']
        else:
            desired_item = self.get_item(folder_name)
            if desired_item is None:
                print("Cannot find folder.")
                return
            folder_id = desired_item['id']
            self.folder_stack.append({'name': folder_name, 'id': folder_id})
        if folder_id in self.cache:
            self.drive_items = self.cache[folder_id]
        else:
            self.drive_items = {}
            page_token = None
            while True:
                results = self.service.files().list(q=f"'{folder_id}' in parents and trashed = False",
                                                    spaces='drive',
                                                    fields='nextPageToken, files(id, name, mimeType)',
                                                    pageToken=page_token).execute()
                items = results.get('files', [])
                page_token = results.get('nextPageToken', None)
                self.drive_items.update({i['name']: i for i in items})
                if page_token is None:
                    break
            self.cache[folder_id] = self.drive_items

    def typeof(self, name: str) -> str:
        """
        Returns the filetype of the given name, or an error message if a file with that name
        does not exist.
        :param name:
        :return:
        """
        desired_item = self.get_item(name)
        return "File/Folder does not exist" if desired_item is None else desired_item['mimeType']

    def get_names(self):
        """
        Returns a list of all file names in the current directory.
        :return:
        """
        return list(self.drive_items.keys())

    def ls(self) -> str:
        """
        Returns a newline-separated string of all file names in the current directory.
        :return:
        """
        output = []
        for name, item in self.drive_items.items():
            is_folder = item['mimeType'] == "application/vnd.google-apps.folder"
            if is_folder:
                output.append(ColorText.bcolors.OKBLUE)
            output.append(name + "\n")
            if is_folder:
                output.append(ColorText.bcolors.ENDC)
        return "".join(output)

    def get_current_path_string(self):
        """
        Returns the current directory path string.
        :return:
        """
        return "/".join(map(lambda d: d['name'], self.folder_stack))

    def get_item(self, name: str):
        """
        Returns the Google file item with the given [name].
        :param name:
        :return:
        """
        return self.drive_items[name] if name in self.drive_items else None

    def download(self, name: str, options: List[str] = None, target_filename: str = None):
        """
        Downloads the file with the given [name] in the current directory and
        saves it in [target_filename] or [name] if a target is not given.
        :param options:
        :param name:
        :param target_filename:
        :return:
        """
        if options is None:
            options = []
        mime_type_options = {
            "-pdf": "application/pdf",
            "-docs": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "-excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "-powerpoint": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        }
        mime_type = None
        for opt in options:
            if opt in mime_type_options:
                mime_type = mime_type_options[opt]
        mime_type = mime_type if mime_type is not None else "application/pdf"

        desired_item = self.get_item(name)
        if desired_item is None:
            print("File/Folder does not exist")
        else:
            target_filename = name if target_filename is None else target_filename
            if desired_item['mimeType'].startswith("application/vnd.google-apps"):
                request = self.service.files().export_media(fileId=desired_item['id'],
                                                            mimeType=mime_type)
            else:
                request = self.service.files().get_media(fileId=desired_item['id'])
            fh = io.FileIO(target_filename, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            try:
                while done is False:
                    status, done = downloader.next_chunk()
                    print("Download %d%%." % int(status.progress() * 100))
            except HttpError as http:
                print(http.content.decode('utf-8'))

    def record_filenames(self, target_filename: str = None):
        """
        Saves the names of all files in the current directory in a newline-separated
        file with the given [target_filename] or "filenames.txt" if a target name is
        not given.
        :param target_filename:
        """
        content = "\n".join(self.get_names())
        target_filename = 'filenames.txt' if target_filename is None else target_filename
        with open(target_filename, 'w') as f:
            f.write(content)


current_directory = pathlib.Path(__file__).parent.absolute()
token_path = os.path.join(current_directory, 'token.pickle')


def get_login_token_opt() -> Optional[Credentials]:
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            return pickle.load(token)
    return None


def login(credentials: ReferenceVar[Credentials]):
    """
    Performs Google login and saves login information in a token.
    """
    if credentials.value and credentials.value.expired and credentials.value.refresh_token:
        credentials.value.refresh(Request())
    else:
        cred_files = os.path.join(current_directory, 'credentials.json')
        flow = InstalledAppFlow.from_client_secrets_file(
            cred_files, ['https://www.googleapis.com/auth/drive'])
        credentials.value = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(token_path, 'wb') as token:
        pickle.dump(credentials.value, token)


def logout(creds: ReferenceVar[Credentials]):
    if os.path.exists(token_path):
        os.remove(token_path)
