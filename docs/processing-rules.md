# Processing rules and safety contract

This page is the behaviour contract for Make Markdown Library. It describes, in order, what the tool does and which files it may read, skip, write, back up, overwrite, or refuse to touch.

## Default paths

If you run:

```bash
make-markdown-library make
```

then the source is:

```text
sources/
```

relative to the current working directory, and the output library is:

```text
markdown-library.md
```

relative to the current working directory.

Set the source explicitly:

```bash
make-markdown-library make my-folder
make-markdown-library make my-file.pdf
make-markdown-library make archive.zip
```

Set the output file explicitly:

```bash
make-markdown-library make my-folder -o out/library.md
```

Or provide a destination folder/file as the second positional path:

```bash
make-markdown-library make my-folder out/
make-markdown-library make my-folder out/library.md
```

If the destination path has a Markdown suffix, it is treated as the exact output file. Otherwise, it is treated as a folder and the tool writes `markdown-library.md` inside it.

## Output files

For a library output named:

```text
library.md
```

the companion outputs are:

```text
library-manifest.md
library.index.json
library.index.yaml        # only with --index-format yaml or both
library-files/            # only with --individual-files
```

## Step-by-step processing order

The `make` command follows this process:

1. Resolve the source path.
2. Resolve the output library path.
3. Resolve companion paths: manifest, JSON/YAML index, and optional individual output directory.
4. Check unsafe path combinations.
5. Apply overwrite or backup policy for output files.
6. Build the exclusion list.
7. Walk the source recursively, or process the single source file.
8. Safely extract ZIP files and nested ZIP files.
9. Classify each found file.
10. Apply Markdown policy.
11. Compute SHA-256 and short fingerprint.
12. Skip duplicates unless `--allow-duplicates` is set.
13. Convert, import, or directly ingest the file.
14. Validate converter output.
15. Apply fallback routing where configured.
16. Write the combined library.
17. Write the manifest.
18. Write the JSON/YAML index.
19. Write individual Markdown files if requested.
20. Print the summary.

## Overwrite rules

The `make` command is non-destructive by default.

If any output file already exists, `make` refuses to run unless you choose one of these behaviours:

```bash
--overwrite
```

Replace existing library, manifest, and index outputs without backups.

```bash
--backup-existing
```

Create backups first, then replace the outputs.

Backups are written next to the original file, for example:

```text
library.backup.md
library-manifest.backup.md
library.index.backup.json
```

If a backup already exists, numbered backup names are used.

## Source and destination in the same folder

It is OK for the source folder and output folder to be the same folder:

```bash
make-markdown-library make project project --backup-existing
```

The tool excludes its own current output library, manifest, index files, and individual output directory from the scan.

It is not OK for a single source file and the output file to be the same exact file:

```bash
make-markdown-library make notes.md -o notes.md
```

That is refused.

## Excluded generated outputs

Unless `--include-generated` is set, the tool skips:

```text
current output library file
current manifest file
current JSON/YAML index files
current individual output directory
*.index.json
*.index.yaml
*.index.yml
*-manifest.md
Markdown split files starting with <!-- source:
```

This prevents recursive libraries and repeated ingestion of generated Markdown.

## Supported source files

The tool handles these directly:

```text
.md, .markdown
.txt, .csv, .json, .jsonl, .xml, .log
```

MarkItDown-supported inputs in this repository include:

```text
.doc, .docx, .ppt, .pptx, .xls, .xlsx, .pdf,
.html, .htm, .rtf, .txt, .csv, .json, .jsonl, .xml, .log
```

LiteParse-supported inputs in this repository include:

```text
.pdf, .doc, .docx, .ppt, .pptx, .xls, .xlsx,
.odt, .ods, .odp,
.png, .jpg, .jpeg, .tif, .tiff, .bmp, .webp
```

ZIP files are containers, not source sections. They are extracted safely and the files inside are processed.

Unsupported files are recorded as skipped in the manifest/index.

## Markdown files

Normal Markdown files are first-class source files. They are read directly and are not sent through MarkItDown or LiteParse.

Default policy:

```bash
--md-policy include
```

This means:

- normal `.md` files are included directly;
- existing generated Markdown libraries are imported as source sections;
- generated manifests, indexes, and split files are skipped.

Other policies:

```bash
--md-policy import-libs
```

Import sections from existing Markdown libraries, but skip ordinary Markdown files.

```bash
--md-policy skip
```

Skip Markdown files entirely.

## JSON and YAML files

Normal `.json` files are included as direct text inputs.

Generated index files are skipped by default:

```text
*.index.json
*.index.yaml
*.index.yml
```

Normal `.yaml` and `.yml` files are not currently source types in v3.1, so they are skipped as unsupported unless support is added later.

## Duplicate handling

Duplicates are detected by file content, not filename.

The tool computes a full SHA-256 hash and a short visible fingerprint. By default, only the first source with a given fingerprint is included. Later duplicates are recorded as skipped:

```text
not added: duplicate source fingerprint
```

To include duplicate content anyway:

```bash
--allow-duplicates
```

## Adding to an existing library

The `add` command reads existing source fingerprints from the library. New sources with matching fingerprints are skipped unless `--allow-duplicates` is used.

By default, `add` backs up the existing library before modifying it. To disable that:

```bash
make-markdown-library add library.md new-files --no-backup-existing
```

`add` appends new sections. It does not replace old sections with the same filename. If a source changed and you want replacement, remove the old section first or rebuild from an index.

## Rebuilds

The `rebuild` command reads a previous JSON index, compares current source hashes, and reuses unchanged sections where possible.

By default, rebuild backs up existing outputs before replacing them.

Use dry run to inspect changes without writing:

```bash
make-markdown-library rebuild library.index.json --dry-run
```

Use `--no-backup-existing --overwrite` if you want to replace without backups.

## Individual Markdown files

With:

```bash
--individual-files
```

the tool writes one Markdown file per included source into:

```text
library-files/
```

These split files are generated outputs. They start with a source marker:

```text
<!-- source: ... -->
```

On later runs, generated split files are skipped by default and may be overwritten safely by new generated split files.

Existing user-authored Markdown files are protected. If a generated split file would collide with an existing non-generated Markdown file, the tool chooses a numbered filename instead:

```text
project.md          # existing user file, preserved
project-2.md        # generated output
```

To deliberately allow overwrite of non-generated split output files:

```bash
--overwrite-individual
```

## Individual directory safety

The default split directory is safe because it is separate from the source files and is excluded from future scans.

This is refused by default:

```bash
make-markdown-library make project -o project/library.md --individual-dir project
```

because it writes individual generated Markdown directly into the source folder and can collide with real Markdown sources.

To allow it intentionally:

```bash
--allow-individual-in-source
```

A safer choice is:

```bash
--individual-dir project/converted-md
```

Custom individual output directories are excluded from source scanning on the same run.

## Generated output cleanup

The tool does not delete arbitrary files from the split directory.

To remove old generated split files before writing new ones:

```bash
--clean-individual-dir
```

This removes only generated split Markdown files with the source marker. It does not remove user-authored Markdown.

## Summary contract

By default, Make Markdown Library:

- reads source files but does not modify them;
- refuses to overwrite existing main outputs during `make`;
- backs up existing libraries during `add` and `rebuild`;
- excludes generated outputs from scanning;
- includes ordinary Markdown files directly;
- skips generated manifests, indexes, and split Markdown files;
- protects user-authored Markdown from individual-file collisions;
- refuses source-file-equals-output-file;
- refuses individual output directly in the source folder unless explicitly allowed.
