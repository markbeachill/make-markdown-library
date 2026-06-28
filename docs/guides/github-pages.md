# Deploying the documentation to GitHub Pages

This repository keeps documentation in two forms:

```text
docs/   Editable Markdown source
site/   Generated static HTML website
```

GitHub Pages can publish the generated `site/` folder, but the clean way to do that is with GitHub Actions. The workflow in this repository builds the site from `docs/` every time documentation changes and then deploys the generated HTML.

## One-time GitHub setup

In your GitHub repository:

1. Open **Settings**.
2. Open **Pages**.
3. Under **Build and deployment**, set **Source** to **GitHub Actions**.
4. Save the setting.

After that, pushes to `main` that touch the docs, site generator, `llms.txt`, or the Pages workflow will deploy the documentation site automatically.

## Included workflow

The deployment workflow lives at:

```text
.github/workflows/publish-site.yml
```

It does this:

```text
checkout repository
set up Python
run scripts/build_static_site.py
upload site/ as the GitHub Pages artifact
deploy the artifact to GitHub Pages
```

## Manual deploy

You can also deploy manually:

1. Go to the repository's **Actions** tab.
2. Open **Publish documentation site**.
3. Choose **Run workflow**.

## Local preview before pushing

Rebuild the site locally:

```bash
python scripts/build_static_site.py
```

Then open:

```text
site/index.html
```

## Why the workflow builds before publishing

The editable docs are Markdown files in `docs/`. Those files are good for Git diffs, code review, and agent-readable documentation, but they are not the finished website.

The generated HTML site lives in `site/`. The workflow rebuilds `site/` from `docs/` before deployment so GitHub Pages always receives the browsable HTML output.

## Alternative: MkDocs Material

The repository also includes `mkdocs.yml`. If you prefer a MkDocs Material site, replace the build step with:

```yaml
- name: Install docs dependencies
  run: pip install -e ".[docs]"

- name: Build MkDocs site
  run: mkdocs build
```

The deploy step can stay the same because MkDocs also writes its output to `site/` by default.
