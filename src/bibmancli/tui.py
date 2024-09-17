from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TextArea, DirectoryTree
from textual.containers import Horizontal, Vertical
from pathlib import Path
from typing import Iterable
from os import system


class FilenameTree(DirectoryTree):
    def on_mount(self):
        self.styles.max_width = "25%"
        self.styles.min_width = 20

        self.guide_depth = 3

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [
            path
            for path in paths
            if path.suffix == ".bib"
            or (path.is_dir() and (path.name[0] != "_" and path.name[0] != "."))
        ]


class MainPane(Horizontal):
    CSS = """
    TextArea {
        width: 100%;
        height: 50%;
        min-height: 50%;
        max-height: 50%;
        border: solid $secondary;
    }
    """

    BINDINGS = {
        ("r", "reload_tree", "[R]eload Tree"),
    }

    def __init__(self, location: Path):
        self.path = location
        self.save_path = location
        self.text_area = TextArea(read_only=True, id="text_area")
        self.text_area.border_title = "File contents"
        self.note = TextArea(read_only=True)
        self.note.border_title = "Note contents"
        super().__init__()

    def compose(self) -> ComposeResult:
        yield FilenameTree(self.path)
        with Vertical():
            yield self.text_area
            yield self.note

    def action_reload_tree(self) -> None:
        tree = self.query_one(FilenameTree)
        tree.reload()

    def update_text(self, path: Path) -> None:
        filename = path.name
        notename = "." + filename.replace(".bib", ".txt")

        self.text_area.text = path.read_text()
        self.note.text = (path.parent / notename).read_text()
        self.save_path = path

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user click a file in the directory tree."""
        path = event.path
        self.update_text(path)


class BibApp(App[None]):
    BINDINGS = {
        ("q", "quit", "[Q]uit"),
        ("e", "edit_file", "[E]dit Open File"),
        ("n", "edit_note", "Edit Open [N]ote"),
    }

    def __init__(self, *, location: Path):
        self.location = location
        super().__init__()

    def on_mount(self) -> None:
        self.title = "BIBMAN"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        yield MainPane(self.location)

    def action_edit_file(self) -> None:
        main_pane = self.query_one(MainPane)
        if main_pane.save_path.is_dir():
            self.notify("Selected path is a directory", severity="error")
            return

        # get environment variable EDITOR
        # editor = environ.get("EDITOR", None)
        # if editor:
        #     self.notify("EDITOR environment variable not set", severity="warning")
        #     return

        with self.suspend():
            # system(f"{editor} {main_pane.save_path}")
            system(f"vim {main_pane.save_path}")

        main_pane.update_text(main_pane.save_path)

    def action_edit_note(self) -> None:
        main_pane = self.query_one(MainPane)
        if main_pane.save_path.is_dir():
            self.notify("Selected path is a directory", severity="error")
            return

        # get environment variable EDITOR
        # editor = environ.get("EDITOR", None)
        # if editor:
        #     self.notify("EDITOR environment variable not set", severity="warning")
        #     return

        filename = main_pane.save_path.name
        notename = "." + filename.replace(".bib", ".txt")
        notepath = main_pane.save_path.parent / notename

        with self.suspend():
            # system(f"{editor} {main_pane.save_path}")
            system(f"vim {notepath}")

        main_pane.update_text(main_pane.save_path)

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user click a file in the directory tree."""
        self.sub_title = event.path.relative_to(self.location).as_posix()
