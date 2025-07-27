import markdown, os
from pathlib import Path

TEMPLATE = Path(".github/scripts/template.html").read_text()

out = Path("out")
out.mkdir(exist_ok=True)

for md_file in Path(".").rglob("*.md"):
    html_path = out / md_file.with_suffix(".html").name
    html_body = markdown.markdown(md_file.read_text())
    html = TEMPLATE.replace("{{TITLE}}", md_file.stem).replace("{{BODY}}", html_body)
    html_path.write_text(html)
