"""GitHub GraphQL API'den kart istatistiklerini çekip cache/stats.json'a yazar.

GITHUB_TOKEN ortam değişkeni gerekir (Actions'ta otomatik gelir).
Sadece standart kütüphane kullanır.
"""
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "profile.json").read_text())
API = "https://api.github.com/graphql"


def gql(query, variables):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"bearer {os.environ['GITHUB_TOKEN']}",
            "Content-Type": "application/json",
            "User-Agent": "profile-card",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body:
        raise SystemExit(f"GraphQL hatası: {body['errors']}")
    return body["data"]


USER_Q = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    following { totalCount }
    contributionsCollection { contributionYears }
  }
}"""

REPOS_Q = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, isFork: false) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes { stargazerCount forkCount }
    }
  }
}"""

YEAR_Q = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
      contributionCalendar { totalContributions }
    }
  }
}"""


def main():
    login = CONFIG["username"]
    user = gql(USER_Q, {"login": login})["user"]

    repos, stars, forks, cursor = 0, 0, 0, None
    while True:
        page = gql(REPOS_Q, {"login": login, "cursor": cursor})["user"]["repositories"]
        repos = page["totalCount"]
        for n in page["nodes"]:
            stars += n["stargazerCount"]
            forks += n["forkCount"]
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]

    commits = prs = contrib_total = this_year = 0
    current_year = datetime.now(timezone.utc).year
    for year in user["contributionsCollection"]["contributionYears"]:
        c = gql(
            YEAR_Q,
            {"login": login, "from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"},
        )["user"]["contributionsCollection"]
        commits += c["totalCommitContributions"] + c["restrictedContributionsCount"]
        prs += c["totalPullRequestContributions"]
        total = c["contributionCalendar"]["totalContributions"]
        contrib_total += total
        if year == current_year:
            this_year = total

    stats = {
        "created_at": user["createdAt"],
        "repos": repos,
        "stars": stars,
        "forks": forks,
        "followers": user["followers"]["totalCount"],
        "following": user["following"]["totalCount"],
        "commits": commits,
        "pull_requests": prs,
        "contributions": contrib_total,
        "contributions_this_year": this_year,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (ROOT / "cache").mkdir(exist_ok=True)
    (ROOT / "cache/stats.json").write_text(json.dumps(stats, indent=2) + "\n")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
