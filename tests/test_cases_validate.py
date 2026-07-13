from pathlib import Path

import tomllib

from failure_gallery import __version__
from failure_gallery.cli import DEFAULT_OUTPUTS, main
from failure_gallery.render import render_index
from failure_gallery.validate import load_cases, validate_cases


def test_runtime_version_matches_package_metadata():
    project = tomllib.loads(
        (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(
            encoding="utf-8"
        )
    )["project"]
    assert __version__ == project["version"] == "0.2.1"


def test_cases_validate():
    assert validate_cases("cases") == []
    cases = load_cases("cases")
    assert len(cases) >= 12
    assert sum(1 for case in cases if case["domain"] == "agent") >= 6
    assert sum(1 for case in cases if case["domain"] == "robotics") >= 6


def test_static_site_renders(tmp_path: Path):
    out = tmp_path / "index.html"
    assert main(["render", "cases", "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "Failure Gallery | AuraOne Open" in text
    assert "Browse failures" in text
    assert "Synthetic data" in text
    assert "data-filters" in text
    assert "<dialog" in text
    assert "Reproduce locally" in text
    assert "Limitations" in text
    assert "radial-gradient" not in text
    assert "backdrop-filter" not in text


def test_static_site_escapes_case_content():
    case = load_cases("cases")[0] | {"title": "<script>alert(1)</script>"}
    text = render_index([case])
    assert "<script>alert(1)</script>" not in text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in text


def test_build_and_check_generated_outputs(tmp_path: Path):
    outputs = [tmp_path / "site/index.html", tmp_path / "docs/index.html"]
    args = ["build", "cases"]
    for output in outputs:
        args.extend(["--out", str(output)])
    assert main(args) == 0
    assert outputs[0].read_text(encoding="utf-8") == outputs[1].read_text(encoding="utf-8")

    check_args = ["check", "cases"]
    for output in outputs:
        check_args.extend(["--out", str(output)])
    assert main(check_args) == 0
    outputs[0].write_text("stale", encoding="utf-8")
    assert main(check_args) == 1


def test_default_outputs_cover_both_deploy_targets():
    assert DEFAULT_OUTPUTS == ("site/index.html", "docs/index.html")
