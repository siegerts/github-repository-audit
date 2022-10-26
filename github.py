import pandas as pd
import requests
import streamlit as st

from constants import CORE_TTL, SEARCH_CACHE_TTL


class GitHubAPIException(Exception):
    """Invalid API Server Responses"""

    def __init__(self, code, resp):
        self.code = code
        self.resp = resp

    def __str__(self):
        return f"Server Response ({self.code}): {self.resp}"


class GitHubAPI:
    def __init__(self, gh_api="https://api.github.com", token=None):
        self.gh_api = gh_api
        self._token = token

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        if not token:
            raise Exception("token cannot be empty")
        self._token = token

    def get(self, url, media_type="vnd.github.v3+json", **params):
        headers = {
            "Accept": "application/" + media_type,
            "Authorization": "token " + self.token,
        }

        if media_type:
            headers["Accept"] = "application/" + media_type

        req_url = self.gh_api + url

        req = requests.get(req_url, headers=headers, params=params)

        if req.status_code not in range(200, 301):
            raise GitHubAPIException(req.status_code, req.json())

        return req.json()

    @st.cache(ttl=CORE_TTL)
    def get_repo(self, org, id):
        print(org, id)
        req = self.get(f"/repos/{org}/{id}")
        df = pd.json_normalize(req)
        return df

    @st.cache(ttl=SEARCH_CACHE_TTL)
    def get_open_for_contrib_issues(self, org, id, deployed=False):
        if not deployed:
            print("Cache miss: get_open_for_contrib_issues(", org, ", ", id, ") ran")

        contrib_issue_count = {}
        contrib_labels = ["good first issue", "question", "open-for-contribution"]

        q = f"repo:{org}/{id} is:open is:issue "

        for label in contrib_labels:
            params = {"q": q + f'label:"{label}"'}

            try:
                req = self.get("/search/issues", **params)
                contrib_issue_count[label] = req["total_count"]
            except GitHubAPIException:
                contrib_issue_count[label] = "pending update..."

        return contrib_issue_count

    @st.cache(ttl=CORE_TTL)
    def get_repo_health(self, org, id):
        url = f"/repos/{org}/{id}/community/profile"
        req = self.get(url, media_type="vnd.github.mercy-preview+json")
        return req

    @st.cache(ttl=CORE_TTL)
    def get_repo_files(self, org, id, filepath):
        url = f"/repos/{org}/{id}/contents/.github/{filepath}"

        try:
            req = self.get(url)
        except GitHubAPIException as err:
            print(err)
            return []

        return req

    @st.cache(ttl=CORE_TTL)
    def get_repo_topics(self, org, id):
        url = f"/repos/{org}/{id}/topics"
        params = {"per_page": 100}
        req = self.get(url, media_type="vnd.github.mercy-preview+json", **params)
        df = pd.json_normalize(req)
        return df

    @st.cache(ttl=CORE_TTL)
    def get_repo_labels(self, org, id):
        url = f"/repos/{org}/{id}/labels"
        params = {"per_page": 100}
        req = self.get(url, **params)
        df = pd.json_normalize(req)
        return df
