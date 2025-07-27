import re
from pathlib import Path

TEMPLATE = Path(".github/scripts/template.html").read_text()
JS_TIPS = Path(".github/scripts/js_tip_turbowarp.html").read_text()

out = Path("out")
out.mkdir(exist_ok=True)

for js_file in Path(".").rglob("*.js"):
    text = js_file.read_text()
    class_match = re.search(r"class\s+(\w+)\s*", text)
    if not class_match:
        continue
    class_name = class_match.group(1)
    constructor_match = re.search(r"constructor\s*\((.*?)\)\s*{(.*?)}", text, re.DOTALL)
    constructor_args = constructor_match.group(1) if constructor_match else "None"
    constructor_body = constructor_match.group(2) if constructor_match else ""

    # Extract this.var = ...
    props = re.findall(r"this\.(\w+)\s*=\s*(.*?);", constructor_body)

    prop_lines = "\n".join([f"<li><b>{name}</b>: {value}</li>" for name, value in props])
    prop_html = f"<ul>{prop_lines}</ul>" if prop_lines else "<p>No properties found.</p>"

    body = f"""
    <h1>{class_name}</h1>
    <h2>Constructor Arguments</h2>
    <p>{constructor_args}</p>
    <h2>Constructor Properties</h2>
    {prop_html}
    <h2>Full Code</h2>
    <pre><code>{text}</code></pre>
    {JS_TIPS}
    """

    html = TEMPLATE.replace("{{TITLE}}", class_name).replace("{{BODY}}", body)
    (out / (js_file.name + ".html")).write_text(html)
