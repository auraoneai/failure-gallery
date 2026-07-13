#!/usr/bin/env python3
"""Build and validate the Failure Gallery release distributions."""

from __future__ import annotations

import argparse
import email.parser
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from failure_gallery import __version__ as runtime_version


PACKAGE_NAME = "failure-gallery"
IMPORT_NAME = "failure_gallery"
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:[-+][0-9A-Za-z.-]+)?$"
)


def run(*command: str) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def tagged_version() -> str | None:
    ref = os.environ.get("GITHUB_REF", "")
    prefix = "refs/tags/failure-gallery-v"
    return ref.removeprefix(prefix) if ref.startswith(prefix) else None


def metadata_from_wheel(path: Path) -> email.message.Message:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        metadata_names = [
            name for name in names if name.endswith(".dist-info/METADATA")
        ]
        if len(metadata_names) != 1:
            raise ValueError("wheel must contain exactly one METADATA file")
        if not any(name.startswith(f"{IMPORT_NAME}/") for name in names):
            raise ValueError(f"wheel is missing the {IMPORT_NAME} package")
        if not any(name.endswith("/static/gallery.css") for name in names):
            raise ValueError("wheel is missing the canonical gallery stylesheet")
        return email.parser.Parser().parsestr(
            archive.read(metadata_names[0]).decode("utf-8", errors="strict")
        )


def metadata_from_sdist(path: Path) -> email.message.Message:
    with tarfile.open(path, "r:gz") as archive:
        names = archive.getnames()
        metadata_names = [
            name
            for name in names
            if name.count("/") == 1 and name.endswith("/PKG-INFO")
        ]
        if len(metadata_names) != 1:
            raise ValueError("source distribution must contain one top-level PKG-INFO")
        if not any(name.endswith("/README.md") for name in names):
            raise ValueError("source distribution is missing README.md")
        extracted = archive.extractfile(metadata_names[0])
        if extracted is None:
            raise ValueError("could not read source distribution PKG-INFO")
        return email.parser.Parser().parsestr(
            extracted.read().decode("utf-8", errors="strict")
        )


def validate_distributions(dist: Path, version: str) -> None:
    if not dist.is_dir():
        raise SystemExit(f"distribution directory does not exist: {dist}")
    run(sys.executable, "-m", "twine", "check", "--strict", *map(str, dist.iterdir()))

    wheels = sorted(dist.glob("*.whl"))
    sdists = sorted(dist.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise SystemExit("expected exactly one wheel and one source distribution")
    for metadata in (
        metadata_from_wheel(wheels[0]),
        metadata_from_sdist(sdists[0]),
    ):
        if (metadata["Name"], metadata["Version"]) != (PACKAGE_NAME, version):
            raise SystemExit(
                "distribution metadata mismatch: "
                f"Name={metadata['Name']}, Version={metadata['Version']}"
            )

    with tempfile.TemporaryDirectory(prefix="failure-gallery-install-") as temp:
        venv = Path(temp) / "venv"
        run(sys.executable, "-m", "venv", str(venv))
        executable = venv / (
            "Scripts/failure-gallery.exe" if os.name == "nt" else "bin/failure-gallery"
        )
        python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        run(
            str(python),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-deps",
            str(wheels[0]),
        )
        run(str(executable), "--help")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-version")
    parser.add_argument(
        "--dist",
        type=Path,
        help="validate these exact distributions instead of building temporary ones",
    )
    args = parser.parse_args()

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    version = project["version"]
    if runtime_version != version:
        raise SystemExit(
            f"runtime version mismatch: package is {version}, import reports {runtime_version}"
        )
    expected = args.expected_version or tagged_version()
    if not SEMVER.fullmatch(version):
        raise SystemExit(f"invalid semantic version: {version}")
    if expected and expected != version:
        raise SystemExit(
            f"release version mismatch: expected {expected}, package is {version}"
        )
    if project.get("scripts", {}).get("failure-gallery") != "failure_gallery.cli:main":
        raise SystemExit("pyproject.toml is missing the failure-gallery entry point")
    urls = project.get("urls", {})
    if urls.get("Repository") != "https://github.com/auraoneai/failure-gallery.git":
        raise SystemExit("pyproject.toml has an incorrect Failure Gallery repository URL")
    if urls.get("Issues") != "https://github.com/auraoneai/failure-gallery/issues":
        raise SystemExit("pyproject.toml has an incorrect Failure Gallery issue tracker URL")
    if f"## {version} " not in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"):
        raise SystemExit(f"CHANGELOG.md has no section for {version}")

    if args.dist is not None:
        validate_distributions(args.dist.resolve(), version)
    else:
        with tempfile.TemporaryDirectory(prefix="failure-gallery-release-") as temp:
            dist = Path(temp) / "dist"
            run(sys.executable, "-m", "build", "--outdir", str(dist))
            validate_distributions(dist, version)

    print(f"release preflight passed for {PACKAGE_NAME} {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
