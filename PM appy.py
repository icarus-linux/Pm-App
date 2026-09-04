import json
import os
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path

CONFIG_FILE = Path.home() / ".pm_workspace_config.json"
TEXT_EXTENSIONS = {".txt", ".md"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp"}

def load_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            return {}
    return {}

def save_config(data):
    try:
        CONFIG_FILE.write_text(json.dumps(data, indent=2))
    except Exception:
        pass  # non-fatal: worst case, state isn't remembered next launch

class WorkspaceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Product Workspace")
        self.geometry("1000x620")
        self.minsize(760, 480)

        self.config_data = load_config()
        self.workspace_path = None
        self.current_product = None
        self.current_file = None
        self.text_dirty = False

        self._build_ui()
        self._restore_state()

# ---------- UI construction ----------
    def _build_ui(self):
        top = ttk.Frame(self, padding=8)
        top.pack(side="top", fill="x")

        self.workspace_label = ttk.Label(top, text="No workspace selected", anchor="w")
        self.workspace_label.pack(side="left", fill="x", expand=True)

        ttk.Button(top, text="Choose Workspace...", command=self.choose_workspace).pack(side="right")

        main = ttk.Panedwindow(self, orient="horizontal")
        main.pack(fill="both", expand=True)

        # Products panel
        products_frame = ttk.Frame(main, padding=6)
        ttk.Label(products_frame, text="Products", font=("", 10, "bold")).pack(anchor="w")
        self.products_list = tk.Listbox(products_frame, exportselection=False)
        self.products_list.pack(fill="both", expand=True, pady=4)
        self.products_list.bind("<<ListboxSelect>>", self.on_select_product)
        pbtns = ttk.Frame(products_frame)
        pbtns.pack(fill="x")
        ttk.Button(pbtns, text="+ New Product", command=self.new_product).pack(side="left", expand=True, fill="x")
        ttk.Button(pbtns, text="Delete", command=self.delete_product).pack(side="left", expand=True, fill="x")
        main.add(products_frame, weight=1)

        # Files panel
        files_frame = ttk.Frame(main, padding=6)
        ttk.Label(files_frame, text="Files", font=("", 10, "bold")).pack(anchor="w")
        self.files_list = tk.Listbox(files_frame, exportselection=False)
        self.files_list.pack(fill="both", expand=True, pady=4)
        self.files_list.bind("<<ListboxSelect>>", self.on_select_file)
        fbtns = ttk.Frame(files_frame)
        fbtns.pack(fill="x")
        ttk.Button(fbtns, text="+ New .md/.txt", command=self.new_text_file).pack(side="left", expand=True, fill="x")
        ttk.Button(fbtns, text="Add File...", command=self.add_file).pack(side="left", expand=True, fill="x")
        ttk.Button(fbtns, text="Delete", command=self.delete_file).pack(side="left", expand=True, fill="x")
        main.add(files_frame, weight=1)

        # Preview / editor panel
        preview_frame = ttk.Frame(main, padding=6)
        self.preview_label = ttk.Label(preview_frame, text="Select a file to preview or edit", font=("", 10, "bold"))
        self.preview_label.pack(anchor="w")

        self.text_editor = tk.Text(preview_frame, wrap="word", undo=True)
        self.text_editor.pack(fill="both", expand=True, pady=4)
        self.text_editor.bind("<<Modified>>", self._on_text_modified)

        self.image_canvas_label = ttk.Label(preview_frame)  # used only for image preview

        save_bar = ttk.Frame(preview_frame)
        save_bar.pack(fill="x")
        self.save_btn = ttk.Button(save_bar, text="Save", command=self.save_current_file, state="disabled")
        self.save_btn.pack(side="left")
        ttk.Button(save_bar, text="Open in Default App", command=self.open_in_os).pack(side="left", padx=6)

        main.add(preview_frame, weight=2)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

# ---------- Workspace handling ----------
    def choose_workspace(self):
        path = filedialog.askdirectory(title="Choose a folder for your Product Workspace")
        if path:
            self.set_workspace(path)

    def set_workspace(self, path):
        self.workspace_path = Path(path)
        self.workspace_label.config(text=str(self.workspace_path))
        self.config_data["workspace_path"] = str(self.workspace_path)
        self.refresh_products()
        save_config(self.config_data)

    def _restore_state(self):
        ws = self.config_data.get("workspace_path")
        if ws and Path(ws).exists():
            self.set_workspace(ws)
            last_product = self.config_data.get("last_product")
            if last_product:
                items = list(self.products_list.get(0, "end"))
                if last_product in items:
                    idx = items.index(last_product)
                    self.products_list.selection_set(idx)
                    self.on_select_product()
                    last_file = self.config_data.get("last_file")
                    if last_file:
                        fitems = list(self.files_list.get(0, "end"))
                        if last_file in fitems:
                            fidx = fitems.index(last_file)
                            self.files_list.selection_set(fidx)
                            self.on_select_file()
        else:
            messagebox.showinfo("Welcome", "Choose a folder to use as your Product Workspace to get started.")

# ---------- Products ----------
    def refresh_products(self):
        self.products_list.delete(0, "end")
        if not self.workspace_path:
            return
        for entry in sorted(self.workspace_path.iterdir()):
            if entry.is_dir():
                self.products_list.insert("end", entry.name)

    def new_product(self):
        if not self.workspace_path:
            messagebox.showwarning("No workspace", "Choose a workspace folder first.")
            return
        name = simpledialog.askstring("New Product", "Product name:")
        if not name:
            return
        new_dir = self.workspace_path / name
        try:
            new_dir.mkdir(exist_ok=False)
        except FileExistsError:
            messagebox.showerror("Error", "A product with that name already exists.")
            return
        self.refresh_products()

    def delete_product(self):
        sel = self.products_list.curselection()
        if not sel:
            return
        name = self.products_list.get(sel[0])
        if messagebox.askyesno("Delete Product", f"Delete '{name}' and all its files? This cannot be undone."):
            shutil.rmtree(self.workspace_path / name)
            self.current_product = None
            self.refresh_products()
            self.files_list.delete(0, "end")
            self.clear_preview()

    def on_select_product(self, event=None):
        sel = self.products_list.curselection()
        if not sel:
            return
        self.current_product = self.products_list.get(sel[0])
        self.config_data["last_product"] = self.current_product
        self.config_data.pop("last_file", None)
        save_config(self.config_data)
        self.refresh_files()
        self.clear_preview()

# ---------- Files ----------
    def refresh_files(self):
        self.files_list.delete(0, "end")
        if not self.current_product:
            return
        product_dir = self.workspace_path / self.current_product
        for entry in sorted(product_dir.iterdir()):
            if entry.is_file():
                self.files_list.insert("end", entry.name)

    def new_text_file(self):
        if not self.current_product:
            messagebox.showwarning("No product", "Select a product first.")
            return
        name = simpledialog.askstring("New File", "File name (e.g. notes.md or notes.txt):")
        if not name:
            return
        if not (name.endswith(".txt") or name.endswith(".md")):
            name += ".md"
        path = self.workspace_path / self.current_product / name
        if path.exists():
            messagebox.showerror("Error", "A file with that name already exists.")
            return
        path.write_text("")
        self.refresh_files()

    def add_file(self):
        if not self.current_product:
            messagebox.showwarning("No product", "Select a product first.")
            return
        paths = filedialog.askopenfilenames(title="Add file(s) to product")
        if not paths:
            return
        dest_dir = self.workspace_path / self.current_product
        for p in paths:
            shutil.copy(p, dest_dir / Path(p).name)
        self.refresh_files()

    def delete_file(self):
        sel = self.files_list.curselection()
        if not sel:
            return
        name = self.files_list.get(sel[0])
        if messagebox.askyesno("Delete File", f"Delete '{name}'?"):
            (self.workspace_path / self.current_product / name).unlink()
            self.refresh_files()
            self.clear_preview()

    def on_select_file(self, event=None):
        sel = self.files_list.curselection()
        if not sel:
            return
        name = self.files_list.get(sel[0])
        self.current_file = name
        self.config_data["last_file"] = name
        save_config(self.config_data)
        self.load_preview(name)

# ---------- Preview / editing ----------
    def load_preview(self, name):
        path = self.workspace_path / self.current_product / name
        ext = path.suffix.lower()
        self.preview_label.config(text=name)

        if ext in TEXT_EXTENSIONS:
            self.image_canvas_label.pack_forget()
            self.text_editor.pack(fill="both", expand=True, pady=4)
            self.text_editor.delete("1.0", "end")
            try:
                content = path.read_text(encoding="utf-8")
            except Exception:
                content = "(Unable to read file as text)"
            self.text_editor.insert("1.0", content)
            self.text_editor.edit_modified(False)
            self.text_dirty = False
            self.save_btn.config(state="disabled")
        elif ext in IMAGE_EXTENSIONS:
            self.text_editor.pack_forget()
            self._show_image(path)
        else:
            self.image_canvas_label.pack_forget()
            self.text_editor.pack(fill="both", expand=True, pady=4)
            self.text_editor.delete("1.0", "end")
            self.text_editor.insert("1.0", f"(No inline preview for {ext} files. Use 'Open in Default App'.)")
            self.save_btn.config(state="disabled")

    def _show_image(self, path):
        try:
            from PIL import Image, ImageTk
        except ImportError:
            self.text_editor.pack(fill="both", expand=True, pady=4)
            self.text_editor.delete("1.0", "end")
            self.text_editor.insert("1.0", "(Install Pillow to preview images: pip install Pillow)")
            return
        img = Image.open(path)
        img.thumbnail((600, 500))
        photo = ImageTk.PhotoImage(img)
        self.image_canvas_label.image = photo  # keep a reference so it isn't garbage collected
        self.image_canvas_label.config(image=photo)
        self.image_canvas_label.pack(fill="both", expand=True, pady=4)

    def _on_text_modified(self, event=None):
        if self.text_editor.edit_modified():
            self.text_dirty = True
            self.save_btn.config(state="normal")
            self.text_editor.edit_modified(False)

    def save_current_file(self):
        if not self.current_file:
            return
        path = self.workspace_path / self.current_product / self.current_file
        content = self.text_editor.get("1.0", "end-1c")
        path.write_text(content, encoding="utf-8")
        self.text_dirty = False
        self.save_btn.config(state="disabled")

    def clear_preview(self):
        self.current_file = None
        self.preview_label.config(text="Select a file to preview or edit")
        self.text_editor.pack(fill="both", expand=True, pady=4)
        self.image_canvas_label.pack_forget()
        self.text_editor.delete("1.0", "end")
        self.save_btn.config(state="disabled")

    def open_in_os(self):
        if not self.current_file:
            return
        path = self.workspace_path / self.current_product / self.current_file
        if sys.platform.startswith("darwin"):
            subprocess.call(("open", str(path)))
        elif os.name == "nt":
            os.startfile(str(path))
        else:
            subprocess.call(("xdg-open", str(path)))

    def on_close(self):
        if self.text_dirty:
            if messagebox.askyesno("Unsaved changes", "Save changes before closing?"):
                self.save_current_file()
        save_config(self.config_data)
        self.destroy()
if __name__ == "__main__":
    app = WorkspaceApp()
    app.mainloop()