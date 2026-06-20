"""A small click-to-use window for Make Markdown Library.

This is the GUI face. It is deliberately tiny: pick a source folder, pick where
to save, tick whether you also want individual files, press Make. All the real
work happens in `core`. No conversion logic lives here.

Tkinter ships with Python, so there is nothing extra to install.
"""

from __future__ import annotations

import threading
from pathlib import Path

from .core import DEFAULT_LIBRARY_NAME, MarkItDownMissing, build_library


def main() -> int:
    try:
        import tkinter as tk
        from tkinter import filedialog, scrolledtext, ttk
    except ImportError:
        print(
            "This needs Tkinter, which usually ships with Python.\n"
            "On Linux you may need to install it, e.g.  sudo apt install python3-tk"
        )
        return 1

    root = tk.Tk()
    root.title("Make Markdown Library")
    root.minsize(560, 460)

    source_var = tk.StringVar()
    output_var = tk.StringVar()
    split_var = tk.BooleanVar(value=False)

    pad = {"padx": 10, "pady": 6}

    frame = ttk.Frame(root, padding=14)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(1, weight=1)

    ttk.Label(frame, text="Make Markdown Library", font=("TkDefaultFont", 14, "bold")).grid(
        row=0, column=0, columnspan=3, sticky="w", pady=(0, 4)
    )
    ttk.Label(
        frame,
        text="Turn a folder of files into one Markdown file for AI, storage, and search.",
    ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 12))

    def pick_source() -> None:
        chosen = filedialog.askdirectory(title="Choose the folder with your source files")
        if chosen:
            source_var.set(chosen)
            if not output_var.get():
                output_var.set(str(Path(chosen).parent / DEFAULT_LIBRARY_NAME))

    def pick_output() -> None:
        chosen = filedialog.asksaveasfilename(
            title="Save the Markdown library as",
            defaultextension=".md",
            initialfile=DEFAULT_LIBRARY_NAME,
            filetypes=[("Markdown", "*.md"), ("All files", "*.*")],
        )
        if chosen:
            output_var.set(chosen)

    ttk.Label(frame, text="Source folder").grid(row=2, column=0, sticky="w", **pad)
    ttk.Entry(frame, textvariable=source_var).grid(row=2, column=1, sticky="ew", **pad)
    ttk.Button(frame, text="Choose...", command=pick_source).grid(row=2, column=2, **pad)

    ttk.Label(frame, text="Save library as").grid(row=3, column=0, sticky="w", **pad)
    ttk.Entry(frame, textvariable=output_var).grid(row=3, column=1, sticky="ew", **pad)
    ttk.Button(frame, text="Choose...", command=pick_output).grid(row=3, column=2, **pad)

    ttk.Checkbutton(
        frame,
        text="Also make one Markdown file per source (good for storage and version control)",
        variable=split_var,
    ).grid(row=4, column=0, columnspan=3, sticky="w", **pad)

    log = scrolledtext.ScrolledText(frame, height=12, wrap="word", state="disabled")
    log.grid(row=6, column=0, columnspan=3, sticky="nsew", **pad)
    frame.rowconfigure(6, weight=1)

    make_btn = ttk.Button(frame, text="Make library")
    make_btn.grid(row=5, column=0, columnspan=3, sticky="ew", **pad)

    def write_log(text: str) -> None:
        log.configure(state="normal")
        log.insert("end", text + "\n")
        log.see("end")
        log.configure(state="disabled")

    def run_build() -> None:
        source = source_var.get().strip()
        output = output_var.get().strip() or None
        if not source:
            write_log("Choose a source folder first.")
            make_btn.configure(state="normal", text="Make library")
            return
        try:
            result = build_library(
                source,
                output,
                individual_files=split_var.get(),
            )
        except MarkItDownMissing as exc:
            write_log(str(exc))
            make_btn.configure(state="normal", text="Make library")
            return
        except (FileNotFoundError, NotADirectoryError) as exc:
            write_log(f"Problem: {exc}")
            make_btn.configure(state="normal", text="Make library")
            return

        write_log("Done.")
        write_log(f"  Library:  {result.library_path}")
        write_log(f"  Manifest: {result.manifest_path}")
        write_log(f"  Sources included: {result.converted_count}")
        write_log(f"  Sources skipped:  {result.skipped_count}")
        if result.individual_files:
            write_log(f"  Individual files: {len(result.individual_files)} in {result.individual_files[0].parent}")
        make_btn.configure(state="normal", text="Make library")

    def on_make() -> None:
        make_btn.configure(state="disabled", text="Working...")
        write_log("Working...")
        threading.Thread(target=run_build, daemon=True).start()

    make_btn.configure(command=on_make)

    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
