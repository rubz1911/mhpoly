# build_static.py
import os, html, pathlib

# Derive owner/repo and base URL for GitHub Pages
repo_full = os.environ.get("GITHUB_REPOSITORY", "rubz1911/mhpoly")
owner, repo = repo_full.split("/")
BASE_PATH = f"/{repo}"
BASE_URL  = f"https://{owner}.github.io/{repo}"
RAW_BASE  = f"https://raw.githubusercontent.com/{owner}/{repo}/main"

lib_dir = pathlib.Path("library")
lib_dir.mkdir(exist_ok=True)

# Find all .txt files in /library (UTF-8)
files = sorted([p for p in lib_dir.glob("*.txt")], key=lambda p: p.name.lower())

# ---- all-policies.txt (plain text aggregator) ----
agg = []
for p in files:
    try:
        txt = p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        txt = f"(Error reading {p.name}: {e})"
    sep = "=" * 80
    agg.append(f"{sep}\n{p.name}\n{sep}\n{txt}\n\n")
pathlib.Path("all-policies.txt").write_text("".join(agg), encoding="utf-8")

# ---- robots.txt ----
robots_txt = f"""User-agent: *
Allow: /
Sitemap: {BASE_URL}/sitemap.xml
"""
pathlib.Path("robots.txt").write_text(robots_txt, encoding="utf-8")

# ---- sitemap.xml ----
urls = [f"{BASE_URL}/",
        f"{BASE_URL}/all-policies.txt"] + \
       [f"{BASE_URL}/library/{p.name}" for p in files]
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    sm.append(f"  <url><loc>{html.escape(u)}</loc></url>")
sm.append("</urlset>\n")
pathlib.Path("sitemap.xml").write_text("\n".join(sm), encoding="utf-8")

# ---- index.html (static, no JS) ----
style = """
:root{--pad:16px;--radius:16px;--shadow:0 8px 20px rgba(0,0,0,0.08);--muted:#666;}
*{box-sizing:border-box;font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,"Helvetica Neue",Arial;}
body{margin:0;background:#f7f7fb;color:#222;line-height:1.55;padding:24px;max-width:1000px;margin-inline:auto;}
header{margin-bottom:20px;}
h1{margin:0 0 6px 0;font-size:1.6rem;}
.note{color:#666;font-size:0.95rem;margin-top:4px}
.doc{background:#fff;border-radius:16px;box-shadow:0 8px 20px rgba(0,0,0,0.08);padding:16px;margin:18px 0;}
.doc h2{margin:0 0 8px 0;font-size:1.15rem}
.doc .meta{color:#666;font-size:0.9rem;margin-bottom:8px}
.doc pre{white-space:pre-wrap;margin:0;overflow-wrap:anywhere}
.btn{border:1px solid #ddd;background:#fafafa;border-radius:12px;padding:6px 10px;text-decoration:none;color:#222}
.btn:hover{background:#f0f0f5}
code{background:#f0f0f5;padding:2px 6px;border-radius:6px}
nav ul{padding-left:20px;margin:8px 0}
nav li{margin:4px 0}
"""

head = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>MH Poly — Policy Library (Static)</title>
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{BASE_URL}/" />
  <style>{style}</style>
</head>
<body>
  <header>
    <h1>MH Poly — Policy Library (Static)</h1>
    <div class="note">
      This page is statically generated on each push. All policy text is inlined below for crawler/copilot access.
    </div>
    <nav>
      <p><strong>Direct links (crawler-friendly):</strong></p>
      <ul>
"""

for p in files:
    head += f'        <li><a href="{BASE_PATH}/library/{html.escape(p.name)}">{html.escape(p.name)}</a> — ' \
            f'<a href="{RAW_BASE}/library/{html.escape(p.name)}" rel="nofollow">raw</a></li>\n'

head += f"""        <li><a href="{BASE_PATH}/all-policies.txt">all-policies.txt</a> — 
            <a href="{RAW_BASE}/all-policies.txt" rel="nofollow">raw</a></li>
      </ul>
    </nav>
  </header>
  <div id="docs">
"""

parts = [head]

if not files:
    parts.append('<article class="doc"><h2>No .txt files found</h2><pre>Place UTF-8 .txt files into /library/</pre></article>')
else:
    for p in files:
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            txt = f"(Error reading file: {e})"
        parts.append(
            f'<article class="doc">'
            f'<h2>{html.escape(p.name)}</h2>'
            f'<div class="meta">'
            f'<a class="btn" href="{BASE_PATH}/library/{html.escape(p.name)}" download>Download</a> '
            f'<span class="note">Source: <code>{BASE_PATH}/library/{html.escape(p.name)}</code></span>'
            f' — <a href="{RAW_BASE}/library/{html.escape(p.name)}">Open raw (text/plain)</a>'
            f'</div>'
            f'<pre>{html.escape(txt)}</pre>'
            f'</article>'
        )

parts.append("""  </div>
</body>
</html>
""")

pathlib.Path("index.html").write_text("".join(parts), encoding="utf-8")
print("Wrote index.html, all-policies.txt, sitemap.xml, robots.txt")
