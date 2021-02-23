import json
import logging
import time
import urllib

import requests

logger = logging.getLogger(__name__)


class ApiException(Exception):
    pass


class GitlabAPI:
    def __init__(self, api_token, star_filter=None):
        self.api_token = api_token
        self.gitlab_session = requests.Session()
        headers = {"PRIVATE-TOKEN": self.api_token}
        self.gitlab_session.headers.update(headers)
        self.initial_params = {
            "pagination": "keyset",
            "per_page": 100,
            "order_by": "id",
            "sort": "asc"
        }
        self.star_filter = star_filter

    def get_repos_after_id(self, id_after):
        params = self.initial_params.copy()
        params["id_after"] = id_after
        retries = 0

        while retries < 3:
            r = self.gitlab_session.get("https://gitlab.com/api/v4/projects", params=params)
            if r.status_code != 200:
                logger.warning(f"API responded with [{r.status_code}]: {r.text}")
                logger.info("retrying in 3 seconds")
                retries = retries + 1
                time.sleep(3)
                continue

            try:
                next_url = r.links["next"]["url"]
                o = urllib.parse.urlparse(next_url)
                query = urllib.parse.parse_qs(o.query)
                id_after = int(query["id_after"][0])
            except Exception as e:
                logger.warning(f"Something went wrong when parsing the next url: {e}, maybe we're done")
                logger.warning(f"content: {r.text}")
                logger.warning(f"headers: {json.dumps(dict(r.headers), indent=4)}")
            data = []
            try:
                data = r.json()
            except Exception as e:
                logger.warning(f"Something went wrong when getting the repositories: {e}")

            repos = []
            for repo in data:
                if repo["star_count"] > self.star_filter:
                    repos.append(repo["path_with_namespace"])

            return repos, id_after

        raise ApiException

    def get_repo(self, id_or_path):
        url = f"https://gitlab.com/api/v4/projects/{urllib.parse.quote_plus(id_or_path)}"
        params = {
            "license": True,
            "statistics": True,
        }
        r = self.gitlab_session.get(url, params=params)
        return r.json()

    def get_user_status(self):
        url = "https://gitlab.com/api/v4/user/status"
        r = self.gitlab_session.get(url)
        return r.json()


if __name__ == '__main__':
    print(f"Hi from dende-gitlab-api from {__file__}")