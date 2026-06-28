# Folders that already contain Markdown

Folders often already contain Markdown notes, generated libraries, README files, or previous split outputs. Make Markdown Library treats these cases differently.

## Normal Markdown

Normal `.md` and `.markdown` files are source files. They are included directly and not sent through MarkItDown or LiteParse.

```text
project/notes.md      included directly
project/README.md     included directly
```

The converter is recorded as:

```text
direct-markdown
```

## Existing generated libraries

Existing Make Markdown Library outputs can be imported as source sections when the Markdown policy allows it.

Default policy:

```text
--md-policy include
```

This includes normal Markdown and imports existing library sections.

## Generated manifests, indexes, and split files

Generated outputs are skipped by default:

```text
markdown-library-manifest.md
markdown-library.index.json
markdown-library.index.yaml
markdown-library-files/*.md
```

This prevents recursive ingestion.

## Markdown policies

```text
--md-policy include       Include normal Markdown and import generated libraries. Default.
--md-policy import-libs   Import generated libraries; skip normal Markdown.
--md-policy skip          Skip Markdown files entirely.
```

## Repeated runs with individual files

If you run with:

```text
--individual-files
```

then generated split files are outputs, not inputs. A second run skips the split directory and the generated files inside it.

## User-authored Markdown is protected

If a generated split output would collide with a user-authored Markdown file, the tool chooses a numbered output name unless `--overwrite-individual` is set.

```text
project.md      # existing user file, preserved
project-2.md    # generated split output
```

## Include generated files intentionally

Use this only for deliberate meta-library workflows:

```text
--include-generated
```

It disables generated-output skipping and can create duplicates or recursive libraries.
