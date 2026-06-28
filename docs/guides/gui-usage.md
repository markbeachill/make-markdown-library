# GUI usage

The GUI is for users who prefer a window over CLI flags.

## Launch

```bash
python -m make_markdown_library gui
```

## Main sections

The v3 GUI is organised around the same workflow as the CLI:

```text
Input
Output
Converters
Markdown handling
Indexing
Advanced LiteParse options
Safety/overwrite behaviour
```

## LiteParse install help

If a LiteParse mode is selected and LiteParse is missing, the GUI explains what LiteParse is used for and offers installation help rather than failing silently.

## Build summary

After a build, the GUI shows:

```text
Library path
Manifest path
Index path
Sources included
Sources skipped
Individual output folder
```

## Open output folder

Use the output-folder button after a successful build to inspect the generated library, manifest, index, and split files.
