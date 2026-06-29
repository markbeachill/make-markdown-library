"""A small click-to-use window for Make Markdown Library."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from pathlib import Path

from .core import (
    DEFAULT_CONVERTER_MODE,
    DEFAULT_INDEX_FORMAT,
    DEFAULT_LIBRARY_NAME,
    DEFAULT_MARKDOWN_POLICY,
    ConversionDependencyMissing,
    OptionalDependencyMissing,
    build_library,
    install_optional_tool,
)


def main() -> int:
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, scrolledtext, ttk
    except ImportError:
        print(
            "This needs Tkinter, which usually ships with Python.\n"
            "On Linux you may need to install it, e.g.  sudo apt install python3-tk"
        )
        return 1

    root = tk.Tk()
    root.title("Make Markdown Library")
    root.minsize(700, 560)

    source_var = tk.StringVar()
    output_var = tk.StringVar()
    description_var = tk.StringVar()
    category_var = tk.StringVar()
    split_var = tk.BooleanVar(value=False)
    converter_var = tk.StringVar(value=DEFAULT_CONVERTER_MODE)
    md_policy_var = tk.StringVar(value=DEFAULT_MARKDOWN_POLICY)
    index_format_var = tk.StringVar(value=DEFAULT_INDEX_FORMAT)
    liteparse_image_mode_var = tk.StringVar(value="placeholder")
    liteparse_ocr_language_var = tk.StringVar(value="eng")
    liteparse_dpi_var = tk.StringVar(value="150")
    liteparse_complexity_var = tk.BooleanVar(value=False)
    last_output_dir = {"path": None}

    pad = {"padx": 10, "pady": 6}

    frame = ttk.Frame(root, padding=14)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(1, weight=1)

    ttk.Label(frame, text="Make Markdown Library", font=("TkDefaultFont", 14, "bold")).grid(
        row=0, column=0, columnspan=3, sticky="w", pady=(0, 4)
    )
    ttk.Label(
        frame,
        text="Turn a folder of files into one indexed Markdown file for AI, storage, and search.",
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

    ttk.Label(frame, text="Library description").grid(row=4, column=0, sticky="w", **pad)
    ttk.Entry(frame, textvariable=description_var).grid(row=4, column=1, columnspan=2, sticky="ew", **pad)

    ttk.Label(frame, text="Library category").grid(row=5, column=0, sticky="w", **pad)
    ttk.Entry(frame, textvariable=category_var).grid(row=5, column=1, columnspan=2, sticky="ew", **pad)

    ttk.Label(frame, text="Converter").grid(row=6, column=0, sticky="w", **pad)
    ttk.Combobox(
        frame,
        textvariable=converter_var,
        values=["markitdown", "liteparse", "auto", "hybrid"],
        state="readonly",
    ).grid(row=6, column=1, sticky="ew", **pad)
    ttk.Button(frame, text="Install LiteParse", command=lambda: on_install_liteparse()).grid(row=6, column=2, **pad)

    ttk.Label(frame, text="Markdown files").grid(row=7, column=0, sticky="w", **pad)
    ttk.Combobox(
        frame,
        textvariable=md_policy_var,
        values=["include", "import-libs", "skip"],
        state="readonly",
    ).grid(row=7, column=1, sticky="ew", **pad)

    ttk.Label(frame, text="Index file").grid(row=8, column=0, sticky="w", **pad)
    ttk.Combobox(
        frame,
        textvariable=index_format_var,
        values=["json", "yaml", "both", "none"],
        state="readonly",
    ).grid(row=8, column=1, sticky="ew", **pad)

    lite_frame = ttk.LabelFrame(frame, text="Advanced LiteParse options")
    lite_frame.grid(row=9, column=0, columnspan=3, sticky="ew", padx=10, pady=6)
    lite_frame.columnconfigure(1, weight=1)
    ttk.Label(lite_frame, text="Image mode").grid(row=0, column=0, sticky="w", padx=8, pady=4)
    ttk.Combobox(lite_frame, textvariable=liteparse_image_mode_var, values=["off", "placeholder", "markdown", "base64"], state="readonly").grid(row=0, column=1, sticky="ew", padx=8, pady=4)
    ttk.Label(lite_frame, text="OCR language").grid(row=1, column=0, sticky="w", padx=8, pady=4)
    ttk.Entry(lite_frame, textvariable=liteparse_ocr_language_var, width=12).grid(row=1, column=1, sticky="w", padx=8, pady=4)
    ttk.Label(lite_frame, text="DPI").grid(row=1, column=2, sticky="w", padx=8, pady=4)
    ttk.Entry(lite_frame, textvariable=liteparse_dpi_var, width=8).grid(row=1, column=3, sticky="w", padx=8, pady=4)
    ttk.Checkbutton(lite_frame, text="Use PDF complexity check", variable=liteparse_complexity_var).grid(row=2, column=0, columnspan=4, sticky="w", padx=8, pady=4)

    ttk.Checkbutton(
        frame,
        text="Also make one Markdown file per source (good for storage and version control)",
        variable=split_var,
    ).grid(row=10, column=0, columnspan=3, sticky="w", **pad)

    make_btn = ttk.Button(frame, text="Make library")
    make_btn.grid(row=11, column=0, columnspan=2, sticky="ew", **pad)
    open_btn = ttk.Button(frame, text="Open output folder")
    open_btn.grid(row=11, column=2, sticky="ew", **pad)

    log = scrolledtext.ScrolledText(frame, height=14, wrap="word", state="disabled")
    log.grid(row=12, column=0, columnspan=3, sticky="nsew", **pad)
    frame.rowconfigure(12, weight=1)

    def write_log(text: str) -> None:
        def do_write() -> None:
            log.configure(state="normal")
            log.insert("end", text + "\n")
            log.see("end")
            log.configure(state="disabled")
        root.after(0, do_write)

    def set_make_button(enabled: bool, text: str = "Make library") -> None:
        root.after(0, lambda: make_btn.configure(state="normal" if enabled else "disabled", text=text))

    def open_output_folder() -> None:
        path = last_output_dir.get("path")
        if not path:
            write_log("No output folder yet. Build a library first.")
            return
        folder = str(path)
        try:
            if sys.platform.startswith("darwin"):
                subprocess.Popen(["open", folder])
            elif os.name == "nt":
                os.startfile(folder)  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as exc:  # noqa: BLE001
            write_log(f"Could not open output folder: {exc}")


    def on_install_liteparse() -> None:
        def install() -> None:
            write_log("Installing LiteParse using this Python environment...")
            code = install_optional_tool("liteparse", yes=True)
            if code == 0:
                write_log("LiteParse install command finished. You may now choose converter: liteparse or auto.")
            else:
                write_log("LiteParse install command did not complete successfully. Try: pip install liteparse")
        threading.Thread(target=install, daemon=True).start()

    def run_build() -> None:
        source = source_var.get().strip()
        output = output_var.get().strip() or None
        if not source:
            write_log("Choose a source folder first.")
            set_make_button(True)
            return
        try:
            result = build_library(
                source,
                output,
                description=description_var.get().strip(),
                category=category_var.get().strip(),
                individual_files=split_var.get(),
                converter_mode=converter_var.get(),  # type: ignore[arg-type]
                markdown_policy=md_policy_var.get(),  # type: ignore[arg-type]
                index_format=index_format_var.get(),  # type: ignore[arg-type]
                liteparse_options={
                    "image_mode": liteparse_image_mode_var.get(),
                    "ocr_language": liteparse_ocr_language_var.get() or "eng",
                    "dpi": int(liteparse_dpi_var.get() or "150"),
                    "complexity_check": liteparse_complexity_var.get(),
                },
                backup_existing=True,
            )
        except (ConversionDependencyMissing, OptionalDependencyMissing) as exc:
            write_log(str(exc))
            if "LiteParse" in str(exc):
                write_log("Use the Install LiteParse button, or change Converter to markitdown.")
            set_make_button(True)
            return
        except (FileNotFoundError, NotADirectoryError) as exc:
            write_log(f"Problem: {exc}")
            set_make_button(True)
            return
        except Exception as exc:  # noqa: BLE001 - GUI should report failures instead of crashing
            messagebox.showerror("Make Markdown Library", str(exc))
            set_make_button(True)
            return

        last_output_dir["path"] = result.library_path.parent
        write_log("Done.")
        write_log(f"  Library:  {result.library_path}")
        write_log(f"  Manifest: {result.manifest_path}")
        if result.index_path:
            write_log(f"  JSON index: {result.index_path}")
        if result.yaml_index_path:
            write_log(f"  YAML index: {result.yaml_index_path}")
        write_log(f"  Sources included: {result.converted_count}")
        write_log(f"  Sources skipped:  {result.skipped_count}")
        if result.individual_files:
            write_log(f"  Individual files: {len(result.individual_files)} in {result.individual_files[0].parent}")
        set_make_button(True)

    def on_make() -> None:
        set_make_button(False, "Working...")
        write_log("Working...")
        threading.Thread(target=run_build, daemon=True).start()

    make_btn.configure(command=on_make)
    open_btn.configure(command=open_output_folder)

    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
