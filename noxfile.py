"""Nox sessions."""

import shutil
import sys
import tempfile
from pathlib import Path

import nox
from nox import Session, session

python_versions = ["3.10", "3.9", "3.8", "3.7"]


@nox.session(python=python_versions)
def tests(session: Session) -> None:
    """Run the test suite."""
    _install_via_pip(session)
    session.install("pytest", "pytest-cov", "xdoctest")
    session.run("pytest")


@nox.session
def lint(session: Session) -> None:
    """Run linting."""
    pass


@session(python=python_versions[0])
def docs(session: Session) -> None:
    """Build and serve the documentation with live reloading on file changes."""
    args = session.posargs or [
        "--open-browser",
        "docs",
        "docs/_build",
    ]
    _install_via_pip(session)
    session.install("-r", "docs/requirements.txt")
    session.install("sphinx", "sphinx-autobuild")

    build_dir = Path("docs", "_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-autobuild", *args)


def _install_via_pip(session: Session) -> None:
    with tempfile.NamedTemporaryFile() as requirements:
        if sys.platform == "win32":
            requirements_path = "requirements.txt"
        else:
            requirements_path = requirements.name
        session.run(
            "poetry",
            "export",
            "--without-hashes",
            "-o",
            requirements_path,
            external=True,
        )
        session.install("-r", requirements_path)
        session.install(".")
