import requests
import sys
import subprocess

version = None
env = {}

with open(".env", "r") as file:
    for line in file:
        env[line.strip().split('=')[0]] = line.strip().split('=')[1]  # Removes any extra newlines

url = f"https://api.github.com/repos/{env['owner']}/{env['repo']}/releases/latest"

def get_latest_version():
    if version == None:
        raise ValueError("Version not set")

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()["tag_name"]
    else:
        print(f"Failed to get release info! Status Code: {response.status_code}")

def update():
    subprocess.run([sys.executable, "updater.py", env["owner"], env["repo"]])
    exit()