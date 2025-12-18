"""Clone repositories using GitPython with a ZIP fallback."""

import os
import requests
from urllib.parse import urlparse


try:
    from git import Repo, exc as git_exc
except Exception:
    Repo = None
    git_exc = None


class RepoManager:
    def __init__(self, default_save_path: str = ""):
        self.default_save_path = default_save_path or os.path.join(
            os.getcwd(), "downloaded_repos"
        )
        os.makedirs(self.default_save_path, exist_ok=True)

    def _get_repo_name(self, repo_url: str) -> str:
        parsed = urlparse(repo_url)
        parts = parsed.path.strip("/").split("/")
        if parts:
            return parts[-1].replace(".git", "")
        return "repo"

    def clone_repo(self, repo_url: str, local_path: str = "") -> str:
        name = self._get_repo_name(repo_url)
        dest = os.path.join(local_path or self.default_save_path, name)

        if os.path.exists(dest):
            raise FileExistsError(f"Destination exists: {dest}")

        if Repo is None:
            raise RuntimeError(
                "GitPython not available; install GitPython to enable cloning."
            )

        try:
            Repo.clone_from(repo_url, dest)
            return dest
        except Exception as e:
            raise e

    def download_zip(self, repo_url: str, save_path: str = "") -> str:
        name = self._get_repo_name(repo_url)
        target = save_path or self.default_save_path
        os.makedirs(target, exist_ok=True)
        zip_path = os.path.join(target, f"{name}.zip")

        base = repo_url.rstrip(".git")
        urls = [
            f"{base}/archive/refs/heads/main.zip",
            f"{base}/archive/refs/heads/master.zip",
        ]

        for u in urls:
            r = requests.get(u, stream=True, timeout=15)
            if r.status_code == 200:
                with open(zip_path, "wb") as fh:
                    for chunk in r.iter_content(chunk_size=8192):
                        fh.write(chunk)
                return zip_path

        raise RuntimeError("Failed to download ZIP archive")
