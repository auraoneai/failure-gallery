from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .render import render_index
from .validate import load_cases, validate_cases

DEFAULT_OUTPUTS = ("site/index.html", "docs/index.html")


def validate(args: argparse.Namespace) -> int:
    errors = validate_cases(args.cases)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("valid")
    return 0


def render(args: argparse.Namespace) -> int:
    errors = validate_cases(args.cases)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(render_index(load_cases(args.cases)), encoding="utf-8")
    return 0


def build(args: argparse.Namespace) -> int:
    errors = validate_cases(args.cases)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    rendered = render_index(load_cases(args.cases))
    outputs = args.out or DEFAULT_OUTPUTS
    for output in outputs:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
        print(f"wrote {path}")
    return 0


def check(args: argparse.Namespace) -> int:
    errors = validate_cases(args.cases)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    rendered = render_index(load_cases(args.cases))
    stale = []
    outputs = args.out or DEFAULT_OUTPUTS
    for output in outputs:
        path = Path(output)
        if not path.exists() or path.read_text(encoding="utf-8") != rendered:
            stale.append(str(path))
    if stale:
        print(
            "generated gallery is stale: "
            + ", ".join(stale)
            + "; run `failure-gallery build cases/`",
            file=sys.stderr,
        )
        return 1
    print("generated gallery is current")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="failure-gallery")
    sub = parser.add_subparsers(dest="command", required=True)
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("cases")
    validate_parser.set_defaults(func=validate)
    render_parser = sub.add_parser("render")
    render_parser.add_argument("cases")
    render_parser.add_argument("--out", required=True)
    render_parser.set_defaults(func=render)
    build_parser = sub.add_parser("build")
    build_parser.add_argument("cases")
    build_parser.add_argument("--out", action="append")
    build_parser.set_defaults(func=build)
    check_parser = sub.add_parser("check")
    check_parser.add_argument("cases")
    check_parser.add_argument("--out", action="append")
    check_parser.set_defaults(func=check)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
