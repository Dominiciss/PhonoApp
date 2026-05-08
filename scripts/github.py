import requests
import logging

def get_repo():
    """Gets the repository where PhonoScribe resides"""
    response = requests.get("https://api.github.com/repos/Dominiciss/PhonoScribe")

    if response.status_code == 200:
        data = response.json()

        return data
    else:
        logging.error(f"Error: {response.status_code}")
        print(f"Error: {response.status_code}")

        return None

def get_latest(repo):
    """Gets the latest version of PhonoScribe inside GitHub"""
    response = requests.get(repo['tags_url'])

    if response.status_code == 200:
        data = response.json()

        return data[0]['name']
    else:
        logging.error(f"Error: {response.status_code}")
        print(f"Error: {response.status_code}")

        return None