import os
from pathlib import Path
from urllib.parse import quote

TEMPLATE = Path(".github/scripts/template.html").read_text()

out = Path("out")
items = []
for path in sorted(Path(".").iterdir()):
    if path.name.startswith(".") or path.name == "out":
        continue
    label = path.name + ("/" if path.is_dir() else "")
    link = quote(path.name)
    if path.suffix == ".md":
        link = quote(path.with_suffix(".html").name)
    elif path.suffix == ".js":
        link = quote(path.name + ".html")
    items.append(f'<li><a href="{link}">{label}</a></li>')

listing = "<ul>" + "\n".join(items) + "</ul>"

# Append to README.html (already created)
readme_html = out / "README.html"
content = readme_html.read_text()
content += "<hr><h2>Directory Listing</h2>" + listing
(readme_html).write_text(content)

# Duplicate as index.html
(out / "index.html").write_text(content)
