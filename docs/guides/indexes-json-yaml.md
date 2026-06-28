# JSON and YAML indexes

JSON indexes are written by default. They are the machine-readable audit trail for builds and rebuilds.

```bash
make-markdown-library make sources -o library.md --index-format json
make-markdown-library make sources -o library.md --index-format both
```

YAML requires PyYAML:

```bash
pip install "make-markdown-library[yaml]"
```
