# Static HTML documentation site

The Markdown files in `docs/` are source files. They are useful for editing, Git diffs, and agent reading, but they are not the finished website.

The finished multi-page HTML documentation lives in:

```text
site/
```

Open locally:

```text
site/index.html
```

## Why both Markdown and HTML?

Markdown is the editable documentation source. HTML is the user-facing docs site with navigation, layout, styling, search affordances, and page structure.

This repository keeps both:

```text
docs/                 Editable Markdown source
site/                 Generated static HTML site
scripts/build_static_site.py  Rebuilds site/ from docs/
```

## Rebuild the site

```bash
python scripts/build_static_site.py
```

The generator has no third-party dependencies. It converts the project docs to static HTML pages, rewrites Markdown links to HTML links, and copies `llms.txt` into the site.

## MkDocs alternative

The repository also includes `mkdocs.yml` for users who prefer MkDocs Material:

Install the docs dependencies:

```bash
pip install "make-markdown-library[docs]"
```

Then start the MkDocs preview server:

```bash
mkdocs serve
```

The checked-in `site/` directory does not require MkDocs to view locally.

## Deploy to GitHub Pages

This repository includes a GitHub Actions workflow that rebuilds `site/` from `docs/` and publishes the generated HTML to GitHub Pages.

Use this setup in GitHub:

```text
Settings → Pages → Build and deployment → Source → GitHub Actions
```

See [Deploying the documentation to GitHub Pages](github-pages.md) for the full workflow and setup steps.
