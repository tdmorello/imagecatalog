"""Nox sessions."""

import shutil
from pathlib import Path

from nox import Session, session

python_versions = ["3.10", "3.9", "3.8", "3.7"]


@session(python=python_versions[0])
def docs(session: Session) -> None:
    """Build and serve the documentation with live reloading on file changes."""
    args = session.posargs or ["--open-browser", "docs", "docs/_build"]
    session.install(".")
    session.install("-r", "docs/requirements.txt")
    session.install("sphinx", "sphinx-autobuild", "sphinx-click", "furo")

    build_dir = Path("docs", "_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-autobuild", *args)
