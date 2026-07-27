import subprocess
from pathlib import Path
from loguru import logger


class GitSync:

    def __init__(self, config):

        self.config = config

        github = config["github"]

        self.enabled = github["enabled"]

        self.branch = github.get("branch", "main")

        self.remote = github.get("remote", "origin")

        self.commit_message = github.get(
            "commit_message",
            "Auto Update"
        )

        # مسیر repo از config خوانده می‌شه
        # اگر خالی بود، مسیر پروژه رو استفاده می‌کنیم
        repo_path = github.get("repo_path", "")

        if repo_path:
            self.repo = Path(repo_path)
        else:
            self.repo = Path(__file__).parent

    def run(self, *args):

        result = subprocess.run(

            args,

            cwd=self.repo,

            capture_output=True,

            text=True

        )

        if result.returncode != 0:

            logger.error(result.stderr)

            return False

        return True

    def push(self):

        if not self.enabled:

            logger.info("Git Sync Disabled")

            return

        logger.info("Git Sync Started")

        if not self.run("git", "add", "."):
            return

        if not self.run(
            "git",
            "commit",
            "-m",
            self.commit_message
        ):
            logger.info("Nothing To Commit")
            return

        if not self.run(
            "git",
            "push",
            self.remote,
            self.branch
        ):
            return

        logger.success("Git Push Completed")
