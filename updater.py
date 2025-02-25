import requests
import zipfile
import os
import stat
import shutil
import time
import sys
from pathlib import Path

def force_remove_readonly(func, path, _):
    """ Change read-only files so they can be deleted """
    os.chmod(path, stat.S_IWRITE)  # Make writable
    func(path)  # Retry deletion

# Replace with the actual owner and repository name
OWNER = sys.argv[1]
REPO = sys.argv[2]

# GitHub API URL for the latest release
api_url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"

# Get the latest release data
response = requests.get(api_url)
response.raise_for_status()  # Raise an error for bad responses

release_data = response.json()
download_url = release_data["zipball_url"]  # Can also use "zipball_url" for a .zip file

# Download the latest release
download_response = requests.get(download_url, stream=True)
download_response.raise_for_status()

# Save the file locally
file_name = f"{REPO}_latest.zip"
with open(file_name, "wb") as file:
    for chunk in download_response.iter_content(chunk_size=8192):
        file.write(chunk)

print(f"Latest release downloaded as {file_name}")
time.sleep(1)
print("Deleting old project...")
script_path = Path(__file__).resolve()
zip_path = Path(file_name).resolve()
script_dir = script_path.parent  # Script's directory
items_to_skip = []
if not sys.argv[3] == 'None':
    sys.argv[3] = sys.argv[3].split(',')
for item in sys.argv[3]:
    items_to_skip.append(Path(item).resolve())
# Iterate over all files and folders in the directory
for item in script_dir.iterdir():
    if item == script_path or item == zip_path or item in items_to_skip:
        continue  # Skip the script itself
    # Delete files
    if item.is_file():
        item.unlink()
    # Delete directories
    elif item.is_dir():
        shutil.rmtree(item, onerror=force_remove_readonly)
print("Done Deleting!")
print("Extracting...")
github_file_name = ""
with zipfile.ZipFile(file_name, "r") as zipped_file:
    #files_to_extract = [f for f in zipped_file.namelist() if f != "updater.py"]
    
    # Extract only the selected files
    zipped_file.extractall(os.path.dirname(os.path.abspath(__file__)))
    print(f"Extracted {zipped_file.namelist()[0]}")
    github_file_name = zipped_file.namelist()[0]
Path(os.path.abspath(file_name)).unlink()
print("Done Extracting!")

source_dir = Path(os.path.abspath(github_file_name)).resolve()
# Ensure the source directory exists
if source_dir.exists() and source_dir.is_dir():
    for item in source_dir.iterdir():
        destination = script_dir / item.name  # Keep the same name in the new location
        if item == script_path:
            print(f"Skipping {item}")
            continue  # Skip the script itself
        if item.is_file():  # Copy files
            shutil.copy2(item, destination)
            print(f"Copied {item}")
        elif item.is_dir():  # Copy directories
            shutil.copytree(item, destination, dirs_exist_ok=True)
            print(f"Copied {item}")
shutil.rmtree(source_dir, onerror=force_remove_readonly)
print(f"Copied everything from '{source_dir}' to '{script_dir}'")
print("Done Updating!")
