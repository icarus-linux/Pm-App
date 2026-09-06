# Product Workspace

A lightweight desktop app (Python + Tkinter) for organizing product/project
folders — notes, images, and other files — grouped into products and
nested sub-products, with a built-in text editor, search, and backups.

Think: a simple file manager purpose-built for "one folder per product,"
with a few conveniences a plain file explorer doesn't give you.

> Built with the constant help of random people on Discord, Claude Code,
> YouTube, old forum posts, and nonstop Googling — basically an entire
> weekend gone into making it work. Full transparency: I couldn't have
> built this on my own, and I'm not at a skill level where I could
> reliably reproduce it without all that help. This exists because of the
> people and resources that got me through it, not solo ability.

## Features

- **Multiple workspaces** — a landing page lists your recent workspaces
  (any folder on disk) so you can switch between separate projects without
  mixing them together.
- **Nested products** — top-level items are products or groups (e.g.
  `SPAR`), which can contain sub-products (`Eggs`, `Bacon`, ...) to any
  depth, shown as a tree.
- **Files panel** — shows the files inside whichever product/sub-product
  is selected. Add existing files, create new `.md`/`.txt` notes, rename,
  or delete.
- **Rich text editor** — Bold, Italic, and Underline (including proper
  combinations like bold+italic), with URLs auto-highlighted in blue.
  Formatting is stored in a small sidecar `<filename>.fmt.json` next to
  each text file, so the `.md`/`.txt` file itself stays plain text.
- **Image preview** — `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp` files preview
  inline (requires Pillow — see below).
- **Search** — one search box scans product/group names, file names, and
  the text inside `.md`/`.txt` files. Double-click (or Enter) a result to
  jump straight to it, expanding the tree as needed.
- **Backup / export** — one button zips the entire workspace (every
  product, sub-product, file, and its formatting) to a `.zip` you choose.
- **Drag-and-drop** — drop files from your OS file browser onto a product
  or the files panel to copy them in (requires `tkinterdnd2` — see below).
- **Right-click menus** — New / Rename / Delete on both the product tree
  and the files list, instead of only bottom-row buttons.
- **Hide/show panels** — toggle the Products and Files panes off if you
  want a narrower, more focused editor view.
- **Unsaved-changes protection** — switching files, switching products, or
  switching workspaces while you have unsaved edits prompts you to save,
  discard, or cancel — it will never silently throw away your work.
- **Help buttons** — a small `?` next to each panel explains what it does.

## Requirements

- Python 3.8+
- Tkinter (usually bundled with Python; on Debian/Ubuntu install it with
  `sudo apt install python3-tk` if `import tkinter` fails)

Optional, for full functionality:

```bash
pip install -r requirements.txt
```

This installs:
- **`tkinterdnd2`** — enables OS drag-and-drop. Without it, the app runs
  fine but shows a banner explaining that drag-and-drop is off.
- **`Pillow`** — enables inline image preview. Without it, image files
  show a message suggesting you install Pillow, and you can still open
  them with "Open in Default App."

## Getting started

```bash
git clone <this-repo-url>
cd <this-repo>
pip install -r requirements.txt   # optional, see above
python3 product_workspace.py
```

On first launch you'll land on the workspace picker. Click
**"Open Other Folder..."** and choose (or create) any folder on your
computer to use as a workspace — that folder is where all your products,
files, and settings will live. Nothing is written outside the folder you
choose, aside from a small config file at `~/.pm_workspace_config.json`
that remembers your recent workspaces and last-open file.

## Usage notes

- **Products vs. sub-products** are just folders and subfolders — you can
  see and edit them directly on disk if you want. The app doesn't require
  going through the UI.
- **Formatting sidecars** (`notes.md.fmt.json`) are created automatically
  when you apply Bold/Italic/Underline and are kept in sync with renames.
  Deleting a text file also deletes its sidecar.
- **Backups** are full-workspace `.zip` snapshots, not incremental —
  there's currently no built-in "restore" button, so restoring means
  unzipping the archive back into a folder yourself.
- **Deletes are permanent.** There's a confirmation dialog, but no trash
  or undo — double-check before confirming.

## Known limitations

- No restore-from-backup button (see above).
- No keyboard shortcuts yet (Ctrl+S / Ctrl+B / Ctrl+I / Ctrl+U).
- No trash/undo for deleted products or files.
- Product/file names aren't validated against filesystem-illegal
  characters before creation.
- Search reads the whole workspace on the main thread; on a very large
  workspace (thousands of files) it may pause briefly while searching.

## License

Add your preferred license here (e.g. MIT) before publishing.
