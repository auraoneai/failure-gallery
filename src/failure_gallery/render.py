from __future__ import annotations

import html


def render_index(cases: list[dict]) -> str:
    cards = []
    for case in cases:
        cards.append(
            "<article>"
            f"<h2>{html.escape(case['title'])}</h2>"
            f"<p>{html.escape(case['description'])}</p>"
            f"<p><strong>Label:</strong> {html.escape(case['review_label'])}</p>"
            f"<p><strong>Finding:</strong> {html.escape(case['expected_finding'])}</p>"
            f"<p><strong>Tool:</strong> {html.escape(case['related_tool'])}</p>"
            f"<code>{html.escape(case['reproduce_command'])}</code>"
            "</article>"
        )
    return """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>AuraOne Failure Gallery</title>
  <style>
    body { font-family: Inter, system-ui, sans-serif; margin: 0; color: #111827; background: #f8fafc; }
    header { padding: 48px 32px 24px; background: #0f172a; color: white; }
    main { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); padding: 32px; }
    article { background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 18px; }
    h1, h2 { margin: 0 0 12px; }
    code { display: block; white-space: normal; background: #f1f5f9; padding: 10px; border-radius: 6px; }
  </style>
</head>
<body>
  <header>
    <h1>AuraOne Failure Gallery</h1>
    <p>Synthetic tutorial failures for reproducible agent and robotics diagnostics.</p>
  </header>
  <main>
""" + "\n".join(cards) + """
  </main>
</body>
</html>
"""

