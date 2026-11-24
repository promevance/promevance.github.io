# site-src: how the portfolio pages are generated

The live site is plain static HTML. These files are the source it is generated from, so the header, footer and project cards stay consistent as the portfolio grows.

```
site-src/
├── gen.py            ← the generator (Python)
├── requirements.txt  ← jinja2, markdown-it-py, PyYAML
├── templates/        ← page layouts (Jinja2 HTML)
└── content/
    ├── project-01-spotify.md   ← one file per project (front matter + Markdown body)
    ├── project-02-mall.md
    ├── project-03-covid.md
    └── about.md
```

## Rebuild the site

```bash
pip install -r site-src/requirements.txt
python site-src/gen.py          # regenerates index.html, projects/, about/, 404.html, sitemap.xml, robots.txt
python -m http.server 8000      # preview at http://localhost:8000
```

Commit the regenerated HTML together with your content changes. GitHub Pages serves the files as they are (the `.nojekyll` file turns off the Jekyll build).

## Add a new project

1. Create a folder `projects/<slug>/` with a `README.md`, an `images/` folder, and any data, notebooks or files.
2. Copy `content/project-03-covid.md` to `content/project-04-<name>.md` and edit:
   - **Front matter**: `slug`, `order`, `title`, `subtitle`, `category`, `year`, `role`, `tools`, `tags`, `cover`, `thumb`, `card_blurb`, `summary`, optional `kpis` (shown as a strip under the header) and `actions` (header buttons).
   - **Body**: Markdown with a few HTML components. Keep the headings `## At a glance {#at-a-glance}` and `## Under the hood {#under-the-hood}` so the "Summary" and "Technical details" links on the project cards work.
3. Run `python site-src/gen.py`. The home page, the Data Analytics hub (including the tag filters), the footer and the previous/next links all update automatically.

## Reusable components (used inside the Markdown body)

| Component | HTML |
|---|---|
| Summary box | `<div class="callout navy"><h3>…</h3><ul>…</ul></div>` |
| Three tiles | `<div class="cols-3"><div class="tile h"><h4>…</h4><p>…</p></div>…</div>` |
| Zoomable figure | `<figure class="zoomable"><img src="…" alt="…"><figcaption>…</figcaption></figure>` |
| Image gallery | `<div class="gallery">` + figures |
| Bar chart | `<div class="chart"><div class="bars"><div class="bar"><span class="l">…</span><span class="t"><i style="width:54%"></i></span><span class="v">54%</span></div>…` |
| Horizon timeline | `<div class="timeline"><div class="horizon">…</div></div>` |
| File list | `<div class="files"><a class="file" href="…"><span class="ext">CSV</span><span><b>…</b><span class="d">…</span></span><span class="go">Download</span></a></div>` |

Copy any of these from `content/project-01-spotify.md`. In HTML blocks, avoid blank lines inside a component (Markdown ends an HTML block at a blank line).

## Brand tokens

Defined at the top of `assets/site.css`: deep navy `#0F2847`, blue `#1B3F6B`, gold `#C9993A` / `#E0B86A`, ivory `#FAF8F4`. Fonts are Poppins (headings, UI) and Inter (body).
