import io
from typing import TypedDict, Dict, Callable

from google_auth_httplib2 import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

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
        self.page_token = None
        self.folder_stack = []
        self.drive_items: Dict[str, GDriveItem] = {'root': {'id': 'root'}}
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
            folder_id = self.get_item(folder_name)['id']
            self.folder_stack.append({'name': folder_name, 'id': folder_id})
        items = self.service.files().list(q=f"'{folder_id}' in parents and trashed = False",
                                          spaces='drive',
                                          fields='files(id, name, mimeType)',
                                          pageToken=self.page_token).execute().get('files', [])
        self.drive_items = {i['name']: i for i in items}

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

    def download(self, name: str, target_filename: str = None):
        """
        Downloads the file with the given [name] in the current directory and
        saves it in [target_filename] or [name] if a target is not given.
        :param name:
        :param target_filename:
        :return:
        """
        desired_item = self.get_item(name)
        if desired_item is None:
            print("File/Folder does not exist")
        else:
            target_filename = name if target_filename is None else target_filename
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
