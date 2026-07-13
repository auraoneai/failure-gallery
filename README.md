# failure-gallery

Validate and build a searchable gallery of reproducible synthetic agent and robotics failure records.

`failure-gallery` is for evaluation educators, review-tool maintainers, and robotics or agent teams that need inspectable fixtures for failure-review workflows. Its differentiator is evidence-first synthetic case design: every record names the failure, domain, expected review label, expected finding, related tool, exact reproduction command, source JSON path, and synthetic-data boundary.

## Inspectable Output

- `validate`: checks case fields, requires at least 12 records, and requires both agent and robotics domains.
- `render`: writes one requested HTML file from the case records.
- `build`: deterministically writes both `site/index.html` and `docs/index.html` by default.
- `check`: fails when either generated deploy target differs from the canonical renderer output.

The case JSON under `cases/` is the review evidence. `src/failure_gallery/render.py` and packaged local CSS/JavaScript assets are the canonical generator inputs; generated HTML should not be edited by hand.

## Runtime Boundary

Validation and rendering read local JSON, CSS, and JavaScript files and make no network requests. The generated page is standalone, although its navigation links point to public AuraOne and GitHub pages when a browser follows them. No customer, private-lab, or production incident data is bundled.

## Install

Install the current package from PyPI:

```bash
python -m pip install "failure-gallery==0.2.1"
```

## Quickstart

```bash
failure-gallery validate cases/
failure-gallery build cases/
failure-gallery check cases/
```

## Release Status

Registry status verified July 13, 2026:

- PyPI: [`failure-gallery==0.2.1`](https://pypi.org/project/failure-gallery/0.2.1/)
- GitHub release: [`v0.2.1`](https://github.com/auraoneai/failure-gallery/releases/tag/v0.2.1)
- The wheel includes the `failure-gallery` CLI and canonical local CSS and
  JavaScript assets used by `render`, `build`, and `check`.

The project is alpha software. No incident-volume, customer, benchmark, or adoption claim is made.

## Limits

The records are synthetic tutorials with expected review outcomes. They are not real incidents, benchmark results, model comparisons, or proof that a related tool will detect every production failure.

## Next Action

Run `validate`, `build`, and `check`, then choose one record and execute its `reproduce_command`; investigate any mismatch with the documented `expected_finding`.
