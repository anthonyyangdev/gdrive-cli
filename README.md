# gdrive-cli

> A CLI that interacts with Google Drive like a file system

## For Developers

Create a Google Developer account to add a Google Developer project to use the Google Drive API. Then, generate the OAuth2 `client_secrets.json`, and add that file to this project in the `src/drive` directory.

## Commands

There are two types of views, `Login` and `File System`. The set of available commands are different for each view.

### Login

| Command | Description | 
|---------|-------------|
| login   | Opens the login screen in your default browser to authenticate your account and permissions |
| quit    | Quit the app |

### File System
| Command | Description |
|---------|-------------|
| cd [Folder name] | Changes the current working directory to the specified folder name |
| typeof [File/Folder name] | Outputs the mime-type of the given file/folder |
| download [File name] | Downloads the given file and saves it in the directory this app was started in | 
| ls | Lists all files/folders in the current working directory. Folders are highlighted |
| current | Outputs the current working directory |
| record | Saves all files/folder names in the current working directory in a filenames.txt file in the directory this app was started in |
| exec [Shell Command] | Executes the shell command following `exec`  in the real file system |
| switch | Logs out of the File System view and returns to the Login view |
| quit | Quit the app |


## License

MIT © [Anthony Yang]()
