from github import Auth
from github import Github
import csv
import os

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

def get_contributors():

    repo = 'apache/iceberg'
    print(f"Fetching {repo} contributors...")

    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)

    repo = g.get_repo(repo)
    contributors = repo.get_contributors()
    
    contributor_list = []
    for contributor in contributors:
        contributor_list.append({
            'login': contributor.login,
            'contributions': contributor.contributions
        })
    
    return contributor_list

contributors = get_contributors()
with open('contributors.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['login', 'contributions'])
    writer.writeheader()
    writer.writerows(contributors)

print("Contributors written to contributors.csv")
