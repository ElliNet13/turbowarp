import re
import json
from pathlib import Path

TEMPLATE = Path(".github/scripts/template.html").read_text()

out = Path("out")
out.mkdir(exist_ok=True)

def escape_html(text):
    import html
    return html.escape(text)

def render_blocks_table(blocks):
    rows = []
    for block in blocks:
        opcode = block.get("opcode", "")
        text = block.get("text", "")
        block_type = block.get("blockType", "")
        args = block.get("arguments", {})
        args_str = ", ".join(f"{k}: {v.get('type','?')}" for k,v in args.items())
        rows.append(f"<tr><td>{escape_html(opcode)}</td><td>{escape_html(text)}</td><td>{escape_html(block_type)}</td><td>{escape_html(args_str)}</td></tr>")
    table = f"""
    <h2>TurboWarp Blocks</h2>
    <table border="1" cellpadding="5" cellspacing="0">
      <thead><tr><th>Opcode</th><th>Text</th><th>Type</th><th>Arguments</th></tr></thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
    """
    return table

for js_file in Path(".").rglob("*.js"):
    text = js_file.read_text()

    is_turbowarp = "Scratch.extensions.register" in text

    if is_turbowarp:
        # Try to find the extension object JSON for blocks (simplified heuristic)
        # This is tricky as code is JS, but we'll try a rough regex to extract blocks = { ... };
        blocks_match = re.search(r'blocks\s*:\s*({.*?})\s*[,\}]', text, re.DOTALL)
        blocks = []
        if blocks_match:
            blocks_text = blocks_match.group(1)
            # Attempt to convert JS object to JSON by:
            # - replacing single quotes with double quotes
            # - removing trailing commas
            # - Note: this won't always work perfectly but good enough for common cases
            try:
                cleaned = re.sub(r"(\w+):", r'"\1":', blocks_text)  # keys to strings
                cleaned = cleaned.replace("'", '"')
                cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)   # remove trailing commas
                blocks = json.loads(cleaned).values()
            except Exception:
                # fallback empty if parsing fails
                blocks = []

        # Show TurboWarp info block
        turbowarp_info = """
        <hr>
        <h2>TurboWarp Extension Detected</h2>
        <p>This file registers a TurboWarp extension via <code>Scratch.extensions.register</code>.</p>
        <p>Blocks registered in this extension are listed below:</p>
        """
        blocks_html = render_blocks_table(blocks) if blocks else "<p><i>Could not parse blocks.</i></p>"

    else:
        turbowarp_info = ""
        blocks_html = ""

    # Parse class info and constructor vars if present
    class_match = re.search(r'class\s+(\w+)', text)
    class_name = class_match.group(1) if class_match else js_file.stem

    constructor_match = re.search(r'constructor\s*\((.*?)\)\s*{(.*?)}', text, re.DOTALL)
    constructor_args = constructor_match.group(1) if constructor_match else ""
    constructor_body = constructor_match.group(2) if constructor_match else ""

    props = re.findall(r'this\.(\w+)\s*=\s*(.*?);', constructor_body)
    prop_lines = "".join(f"<li><b>{escape_html(name)}</b>: {escape_html(value)}</li>" for name, value in props)
    props_html = f"<ul>{prop_lines}</ul>" if prop_lines else "<p>No constructor properties found.</p>"

    # Compose body
    body = f"""
    {turbowarp_info}
    {blocks_html}
    <h2>Class: {escape_html(class_name)}</h2>
    <h3>Constructor arguments</h3>
    <p>{escape_html(constructor_args) or '<i>None</i>'}</p>
    <h3>Constructor properties</h3>
    {props_html}
    <h2>Full source code</h2>
    <pre><code>{escape_html(text)}</code></pre>
    """

    html = TEMPLATE.replace("{{TITLE}}", escape_html(class_name)).replace("{{BODY}}", body)
    (out / (js_file.name + ".html")).write_text(html)
