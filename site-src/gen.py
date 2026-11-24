#!/usr/bin/env python3
"""Static-site generator for promevance.github.io (renders into the repository root).
Templates are Jinja2, long-form content is Markdown (+ inline HTML components)."""
import os, re, shutil, sys
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown_it import MarkdownIt

SRC = Path(__file__).parent
# Pages are written to the repository root (the parent of site-src/). Override with SITE_OUT for previews.
OUT = Path(os.environ.get("SITE_OUT", SRC.parent))
GH = "https://github.com/promevance/promevance.github.io"
GH_TREE = GH + "/tree/main/"
GH_BLOB = GH + "/blob/main/"

md = MarkdownIt("commonmark", {"html": True, "typographer": False}).enable("table")


def slug(text):
    t = re.sub(r"<[^>]+>", "", text).lower()
    t = re.sub(r"[^a-z0-9\s-]", "", t)
    return re.sub(r"\s+", "-", t.strip())


def render_md(text):
    html = md.render(text)
    # headings in the body get ids (explicit {#id} wins)
    def h2(m):
        inner = m.group(2)
        mm = re.search(r"\s*\{#([\w-]+)\}\s*$", inner)
        if mm:
            return f'<h{m.group(1)} id="{mm.group(1)}">{inner[:mm.start()]}</h{m.group(1)}>'
        return f'<h{m.group(1)} id="{slug(inner)}">{inner}</h{m.group(1)}>'
    html = re.sub(r"<h([23])>(.*?)</h\1>", h2, html)
    return html


def load_content(name):
    raw = (SRC / "content" / name).read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    meta, body = (yaml.safe_load(m.group(1)), m.group(2)) if m else ({}, raw)
    return meta, body


env = Environment(loader=FileSystemLoader(str(SRC / "templates")), autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)

SITE = {
    "name": "Evan Promise",
    "full_name": "Evan Promise Chukwubueze",
    "tagline": "Brand & Growth · GTM Engineering · Data",
    "role": "Brand and growth specialist, GTM engineer and budding data engineer",
    "url": "https://promevance.github.io",
    "website": "https://evanpromise.com",
    "website_label": "evanpromise.com",
    "linkedin": "https://www.linkedin.com/in/evan-promise-c/",
    "github": "https://github.com/promevance",
    "repo": GH,
    "email": "hello@evanpromise.com",
    "email_alt": "promevance@gmail.com",
    "description": ("Data and technical portfolio of Evan Promise Chukwubueze, brand and growth specialist, GTM engineer "
                    "and budding data engineer: Tableau dashboards, Python analysis and data-backed strategy, each with a "
                    "plain-language summary and a technical deep dive."),
}

PROJECTS = []
for f in sorted((SRC / "content").glob("project-*.md")):
    meta, body = load_content(f.name)
    meta["body_html"] = render_md(body)
    meta["url"] = f"/projects/{meta['slug']}/"
    meta["folder"] = f"projects/{meta['slug']}/"
    PROJECTS.append(meta)
PROJECTS.sort(key=lambda p: p["order"])


def write(path, html):
    p = OUT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")
    print("wrote", path, f"({len(html)//1024} KB)")


def page(template, **ctx):
    ctx.setdefault("site", SITE)
    ctx.setdefault("projects", PROJECTS)
    ctx.setdefault("gh_tree", GH_TREE)
    ctx.setdefault("gh_blob", GH_BLOB)
    return env.get_template(template).render(**ctx)


# ---- home
write("index.html", page("home.html", title=None, nav="home", path="/", description=SITE["description"]))

# ---- projects hub
tags = []
for p in PROJECTS:
    for t in p["tags"]:
        if t not in tags:
            tags.append(t)
write("projects/index.html", page("projects.html", title="Data Analytics projects", nav="projects", path="/projects/", tags=tags,
                                  description="Data analytics case studies: Tableau dashboards, Python analysis and machine learning."))

# ---- project pages
for i, p in enumerate(PROJECTS):
    prev_p = PROJECTS[i - 1] if i > 0 else None
    next_p = PROJECTS[i + 1] if i < len(PROJECTS) - 1 else None
    write(f"projects/{p['slug']}/index.html",
          page("project.html", p=p, title=p["title"], nav="projects", path=p["url"], description=p["summary"], prev_p=prev_p, next_p=next_p,
               og_image=p.get("cover")))

# ---- about
meta, body = load_content("about.md")
write("about/index.html", page("about.html", title="About", nav="about", path="/about/", body_html=render_md(body), description=meta.get("description", SITE["description"])))

# ---- 404
write("404.html", page("404.html", title="Page not found", nav="", path="/404.html", description="Page not found"))

# sitemap + robots (static sites don't get these for free)
urls = ["/", "/projects/", "/about/"] + [p["url"] for p in PROJECTS]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
    f"  <url><loc>{SITE['url']}{u}</loc></url>\n" for u in urls) + "</urlset>\n"
write("sitemap.xml", sm)
write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n")
