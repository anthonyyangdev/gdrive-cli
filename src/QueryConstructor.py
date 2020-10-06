def root_content():
    return "'root' in parents and trashed = False"


def get_folders():
    return "mimeType = 'application/vnd.google-apps.folder'"


def get_files():
    return "mimeType != 'application/vnd.google-apps.folder'"


def find_filename(title: str):
    return f"name = '{title}'"


def list_all_in_folder(folder_id: str):
    return f"'{folder_id}' in parents and trashed = False"
