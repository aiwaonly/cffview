import re, json
from typing import Any

from textual.content import Content
from textual.widgets.tree import TreeNode
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Tree, Static
from textual.containers import Horizontal, VerticalScroll


def node_path(node: TreeNode) -> str:
    """ Labels from the top-level node down to `node`, ignoring the tree root. """
    labels: list[str] = []
    while node is not None and node.parent is not None:
        labels.append(str(node.label))
        node = node.parent
    return " › ".join(reversed(labels))


def format_colored_dict(data: dict) -> Content:
    """ Render a dict as indented JSON Content with one colour per nesting level.

    Keys take the level hue, string values are bright white, other values are
    white-grey and structural brackets are dimmed.
    """

    LEVEL_COLORS = [
        "ansi_bright_cyan",
        "ansi_bright_green",
        "ansi_bright_yellow",
        "ansi_bright_magenta",
        "ansi_bright_blue",
        "ansi_bright_red",
    ]
    STR_COLOR = "$text"
    PRIM_COLOR = "$text-muted"
    BRACKET_COLOR = "$text-disabled"

    KV_RE = re.compile(r'^("(?:[^"\\]|\\.)*")(:\s*)(.+)$')

    text = json.dumps(data, indent=4, ensure_ascii=False, default=str)
    chunks: list[str] = []
    spans: list[tuple[str, int, int]] = []
    pos = 0
    STRUCTURE = set("{}[],")

    def write(chunk: str, style: str | None = None) -> None:
        """ Append `chunk` verbatim, spanning it with `style` when it is given. """
        nonlocal pos
        if style is not None:
            spans.append((style, pos, pos + len(chunk)))
        chunks.append(chunk)
        pos += len(chunk)

    for index, line in enumerate(text.split("\n")):
        if index:
            write("\n")

        content = line.lstrip(" ")
        level = (len(line) - len(content)) // 4
        lc = LEVEL_COLORS[level % len(LEVEL_COLORS)]
        write(" " * (len(line) - len(content)))

        m = KV_RE.match(content)
        if m:
            key, colon, rest = m.group(1), m.group(2), m.group(3)
            bare = rest.rstrip(",").strip()
            write(key, lc)
            write(colon, lc)
            if bare.startswith('"'):
                write(rest, STR_COLOR)
            elif bare and set(bare) <= STRUCTURE:
                write(rest, BRACKET_COLOR)
            else:
                write(rest, PRIM_COLOR)
        else:
            bare = content.rstrip(",").strip()
            if bare.startswith('"'):
                write(content, STR_COLOR)
            elif bare and set(bare) <= STRUCTURE:
                write(content, BRACKET_COLOR)
            else:
                write(content, PRIM_COLOR)

    content = Content("".join(chunks))
    for style, start, end in spans:
        content = content.stylize(style, start, end)
    return content


class CFFViewTUI(App):
    """ A textual app for viewing cas.h5 files. """

    TITLE = "cffview"
    CSS = """
    Horizontal { height: 100%; }
    #tree-panel, #detail-panel {
        scrollbar-size-vertical: 1;
        scrollbar-background: $panel-darken-1;
        scrollbar-background-hover: $panel-darken-1;
        scrollbar-background-active: $panel-darken-1;
    }
    #tree-panel {
        width: 40%;
        padding: 0 1;
        border: solid $primary;
        scrollbar-color: $primary;
        scrollbar-color-hover: $primary-lighten-1;
        scrollbar-color-active: $primary-lighten-2;
    }
    #detail-panel {
        width: 60%;
        height: 100%;
        padding: 1 2;
        border: solid $accent;
        border-title-align: left;
        scrollbar-color: $accent;
        scrollbar-color-hover: $accent-lighten-1;
        scrollbar-color-active: $accent-lighten-2;
    }
    """
    BINDINGS = [
        ("d", "toggle_theme", "Toggle theme mode"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, data: dict[str, Any], file_name: str) -> None:
        self.data = data
        self.data_tree = Tree(file_name, id="tree-panel")
        self.data_tree.root.expand()
        for key, value in self.data.items():
            match key:
                case "materials" | "boundary":
                    node = self.data_tree.root.add(key)
                    for type_, values in value.items():
                        type_node = node.add(type_)
                        for name, value in values.items():
                            type_node.add_leaf(name, value)
                case "solution" | "report-definitions" | "plotsets" | "monitorsets" | "surfaces" | "mesh" | "contours" | "vectors" | "pathlines" | "xy-plot" | "scene" | "parameters":
                    node = self.data_tree.root.add(key)
                    for name, value in value.items():
                        node.add_leaf(name, value)
                case _:
                    self.data_tree.root.add_leaf(key, value)
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Horizontal():
            yield self.data_tree
            with VerticalScroll(id="detail-panel"):
                yield Static("Select a leaf node to view details.", id="detail-content")

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        node = event.node
        if node.allow_expand:
            return
        data = node.data or {}
        panel = self.query_one("#detail-panel", VerticalScroll)
        panel.border_title = node_path(node)
        panel.border_subtitle = f"{len(data)} keys" if isinstance(data, dict) else ""
        self.query_one("#detail-content", Static).update(format_colored_dict(data))

    def action_toggle_theme(self) -> None:
        """An action to toggle theme mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
