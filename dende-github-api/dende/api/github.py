import datetime
import logging

import github

logger = logging.getLogger(__name__)


class GithubAPI:
    def __init__(self, api_token, star_filter=None):
        self.api_token = api_token
        self.star_filter = star_filter
        self.github = github.Github(login_or_token=self.api_token, per_page=100)

    def get_repos_between(self, start_date, end_date):
        logger.info(f"getting repos between {start_date.isoformat()} and {end_date.isoformat()}")

        query = f"stars:{self.star_filter} created:{start_date.isoformat()}..{end_date.isoformat()}"
        repositories = self.github.search_repositories(query=query)

        repos = [repo.full_name for repo in repositories]

        return repos

    def get_repo(self, repo_name):
        api_repo = self.github.get_repo(repo_name)
        license = api_repo.raw_data.get("license")
        license_key = None
        license_name = None
        if license is not None:
            if "key" in license:
                license_key = license["key"]
            if "name" in license:
                license_name = license["name"]

        # todo get contributors count with 1-item-per-page query or per website
        # contributors = api_repo.get_contributors("true")
        # todo get number of releases from website (see torvalds/linux and laravel/laravel)
        # releases =

        repo = {
            "github_id": api_repo.id,
            "full_name": api_repo.full_name,
            "description": api_repo.description,
            "fork": api_repo.fork,
            "created_at": api_repo.created_at,
            "updated_at": api_repo.updated_at,
            "homepage": api_repo.homepage,
            "size": api_repo.size,
            "watchers_count": api_repo.watchers_count,
            "language": api_repo.language,
            "forks_count": api_repo.forks_count,
            "archived": api_repo.archived,
            "disabled": api_repo.raw_data.get("disabled"),
            "open_issues_count": api_repo.open_issues_count,
            "network_count": api_repo.network_count,
            "subscribers_count": api_repo.subscribers_count,
            "owner_type": api_repo.owner.type,
            "owner_login": api_repo.owner.login,
            "license_key": license_key,
            "license_name": license_name,
            "timestamp": datetime.datetime.now()
        }

        return repo

    def get_limits(self):
        # todo we could check if the rate returned by gittest actually fits the rate specified by the environment vars
        # (limits.core.reset - now) / limits.core.remaining < (COORDINATOR_RUNTIME / GITHUB_REQUESTS)
        return self.github.get_rate_limit()


if __name__ == '__main__':
    print(f"Hi from dende-github-api from {__file__}")