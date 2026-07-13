from __future__ import annotations

import html
import json
from pathlib import Path

ASSET_ROOT = Path(__file__).with_name("static")


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _case_source(case: dict) -> str:
    return f"cases/{case['id']}/case.json"


def _case_limitations(case: dict) -> str:
    return (
        "Synthetic tutorial evidence only. This record does not represent a "
        "customer incident, production benchmark, or validated model comparison."
    )


def _case_card(case: dict) -> str:
    case_id = _escape(case["id"])
    domain = _escape(case["domain"])
    tool = _escape(case["related_tool"])
    title = _escape(case["title"])
    description = _escape(case["description"])
    expected = _escape(case["expected_finding"])
    source = _escape(_case_source(case))
    search = _escape(
        " ".join(
            [
                case["id"],
                case["domain"],
                case["title"],
                case["description"],
                case["review_label"],
                case["expected_finding"],
                case["related_tool"],
            ]
        ).lower()
    )
    return f"""
      <article class="case-card" id="{case_id}" data-case data-domain="{domain}" data-tool="{tool}" data-search="{search}">
        <div class="case-card__meta">
          <span class="domain-label">{domain}</span>
          <span class="data-label">Synthetic data</span>
        </div>
        <h2>{title}</h2>
        <p>{description}</p>
        <dl>
          <div><dt>Tool</dt><dd>{tool}</dd></div>
          <div><dt>Source</dt><dd><code>{source}</code></dd></div>
          <div><dt>Expected behavior</dt><dd>{expected}</dd></div>
        </dl>
        <button class="case-action" type="button" data-open-case="{case_id}" aria-haspopup="dialog">
          Review evidence
          <span aria-hidden="true">→</span>
        </button>
      </article>"""


def _case_dialog(case: dict) -> str:
    case_id = _escape(case["id"])
    title = _escape(case["title"])
    domain = _escape(case["domain"])
    tool = _escape(case["related_tool"])
    source = _escape(_case_source(case))
    command = _escape(case["reproduce_command"])
    return f"""
    <dialog class="case-dialog" id="dialog-{case_id}" aria-labelledby="dialog-{case_id}-title">
      <div class="dialog-shell">
        <header>
          <div>
            <p class="eyebrow">{domain} failure record</p>
            <h2 id="dialog-{case_id}-title">{title}</h2>
          </div>
          <button class="icon-button" type="button" data-close-dialog aria-label="Close failure record">×</button>
        </header>
        <div class="dialog-body">
          <section class="record-section" aria-labelledby="failure-{case_id}">
            <h3 id="failure-{case_id}">Failure</h3>
            <p>{_escape(case["description"])}</p>
          </section>
          <div class="record-grid">
            <section class="record-section">
              <h3>Domain</h3>
              <p>{domain}</p>
            </section>
            <section class="record-section">
              <h3>Related tool</h3>
              <p>{tool}</p>
            </section>
            <section class="record-section">
              <h3>Review label</h3>
              <p><code>{_escape(case["review_label"])}</code></p>
            </section>
            <section class="record-section">
              <h3>Source</h3>
              <p><code>{source}</code></p>
            </section>
          </div>
          <section class="record-section">
            <h3>Expected behavior</h3>
            <p>{_escape(case["expected_finding"])}</p>
          </section>
          <section class="record-section">
            <h3>Evidence</h3>
            <p>
              The fixture is designed to produce the <code>{_escape(case["review_label"])}</code>
              finding when reviewed with {tool}. Compare the tool output with the expected
              behavior above; no production result is asserted by this gallery.
            </p>
          </section>
          <section class="record-section">
            <h3>Reproduce locally</h3>
            <div class="command-block">
              <code>{command}</code>
              <button type="button" data-copy-command="{command}">Copy command</button>
            </div>
          </section>
          <section class="record-section limitations">
            <h3>Limitations</h3>
            <p>{_escape(_case_limitations(case))}</p>
          </section>
        </div>
        <footer>
          <a href="#{case_id}" data-copy-record-link>Link to this record</a>
          <button class="secondary-button" type="button" data-close-dialog>Done</button>
        </footer>
      </div>
    </dialog>"""


def render_index(cases: list[dict]) -> str:
    sorted_cases = sorted(cases, key=lambda case: (case.get("domain", ""), case["title"]))
    tools = sorted({case["related_tool"] for case in sorted_cases})
    cards = "\n".join(_case_card(case) for case in sorted_cases)
    dialogs = "\n".join(_case_dialog(case) for case in sorted_cases)
    styles = (ASSET_ROOT / "gallery.css").read_text(encoding="utf-8")
    script = (ASSET_ROOT / "gallery.js").read_text(encoding="utf-8")
    cases_json = json.dumps(sorted_cases, separators=(",", ":"), ensure_ascii=True).replace("</", "<\\/")
    tool_options = "\n".join(f'          <option value="{_escape(tool)}">{_escape(tool)}</option>' for tool in tools)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="AuraOne Failure Gallery publishes synthetic agent and robotics failures with reproducible local commands and review evidence.">
  <meta name="color-scheme" content="light">
  <title>Failure Gallery | AuraOne Open</title>
  <style>
{styles}
  </style>
</head>
<body>
  <a class="skip-link" href="#case-index">Skip to failure records</a>
  <header class="site-header">
    <a class="brand" href="https://www.auraone.ai/open">
      <strong>AuraOne</strong>
      <span>Open</span>
      <span class="brand-divider" aria-hidden="true"></span>
      <span>Failure Gallery</span>
    </a>
    <nav aria-label="Open source links">
      <a href="https://www.auraone.ai/open/trust-toolkit">Trust Toolkit</a>
      <a href="https://github.com/auraoneai/failure-gallery">GitHub</a>
    </nav>
  </header>

  <main>
    <section class="intro" aria-labelledby="page-title">
      <p class="eyebrow">Reproducible review records</p>
      <h1 id="page-title">Failure Gallery</h1>
      <p class="lede">
        Synthetic agent and robotics failures with the source, expected finding,
        evidence boundary, and local command required to reproduce each review path.
      </p>
      <div class="disclosure" role="note">
        <strong>Approved public data:</strong>
        All {len(sorted_cases)} records are synthetic tutorial fixtures. They contain no customer or private lab data.
      </div>
    </section>

    <section class="catalog" id="case-index" aria-labelledby="catalog-title">
      <div class="catalog-heading">
        <div>
          <p class="eyebrow">Record index</p>
          <h2 id="catalog-title">Browse failures</h2>
        </div>
        <p class="result-count" aria-live="polite"><strong data-visible-count>{len(sorted_cases)}</strong> of {len(sorted_cases)} records</p>
      </div>

      <form class="filters" role="search" data-filters>
        <label class="search-field">
          <span>Search records</span>
          <input type="search" name="query" placeholder="Search failure, tool, label…" autocomplete="off">
        </label>
        <fieldset>
          <legend>Domain</legend>
          <div class="segmented-control">
            <label><input type="radio" name="domain" value="all" checked><span>All</span></label>
            <label><input type="radio" name="domain" value="agent"><span>Agent</span></label>
            <label><input type="radio" name="domain" value="robotics"><span>Robotics</span></label>
          </div>
        </fieldset>
        <label class="select-field">
          <span>Related tool</span>
          <select name="tool">
            <option value="all">All tools</option>
{tool_options}
          </select>
        </label>
        <button class="reset-button" type="reset">Reset filters</button>
      </form>

      <div class="case-grid" data-case-grid>
{cards}
      </div>
      <div class="no-results" data-no-results hidden>
        <strong>No matching records</strong>
        <p>Clear filters or search for a domain, tool, review label, or expected finding.</p>
      </div>
    </section>

    <section class="method" aria-labelledby="method-title">
      <div>
        <p class="eyebrow">Evidence contract</p>
        <h2 id="method-title">Read the record before running the command.</h2>
      </div>
      <ol>
        <li><strong>Inspect</strong><span>Confirm the synthetic source and stated failure.</span></li>
        <li><strong>Reproduce</strong><span>Run the exact local command in the linked tool.</span></li>
        <li><strong>Compare</strong><span>Check observed evidence against the expected behavior and limitations.</span></li>
      </ol>
    </section>
  </main>

  <footer class="site-footer">
    <span>AuraOne Open · Synthetic evidence only</span>
    <a href="https://www.auraone.ai/open/robotics-studio/failure-gallery">Canonical AuraOne route</a>
  </footer>

{dialogs}
  <script type="application/json" id="failure-gallery-data">{cases_json}</script>
  <script>
{script}
  </script>
</body>
</html>
"""
