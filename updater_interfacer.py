import requests
import sys
import subprocess

env = {}

with open(".env", "r") as file:
    for line in file:
        env[line.strip().split('=')[0]] = line.strip().split('=')[1]  # Removes any extra newlines
    if env['files-to-exclude'] == '':
        env['files-to-exclude'] = 'None'
version = env['version']
url = f"https://api.github.com/repos/{env['owner']}/{env['repo']}/releases/latest"

def get_latest_release_info(info_to_get):
    if env['version'] == '':
        raise ValueError("Version not set")

    response = requests.get(url)

    if response.status_code == 200:
        if info_to_get == 'version':
            return response.json()["tag_name"]
        elif info_to_get == 'notes':
            return response.json()["body"]
        else:
            raise ValueError()
    else:
        print(f"Failed to get release info! Status Code: {response.status_code}")

def update():
    subprocess.run([sys.executable, "updater.py", env["owner"], env["repo"], env['files-to-exclude']])
    exit()
