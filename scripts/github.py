import requests

def get_repo():
    response = requests.get("https://api.github.com/repos/Dominiciss/PhonoScribe")

    if response.status_code == 200:
        data = response.json()
        #print(f"Repo Name: {data['full_name']}")
        #print(f"Stars: {data['stargazers_count']}")
        #print(f"Open Issues: {data['open_issues_count']}")

        return data
    else:
        print(f"Error: {response.status_code}")

        return None

def get_latest(repo):
    response = requests.get(repo['tags_url'])

    if response.status_code == 200:
        data = response.json()

        return data[-1]['name']
    else:
        print(f"Error: {response.status_code}")

        return None