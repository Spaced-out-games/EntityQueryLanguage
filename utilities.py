

from lark import Tree, Token
from dataclasses import is_dataclass, fields


POSITION_FIELDS = {"line", "column"}


def children(node, show_positions=False):
    """Return (title, [(field_name | None, child), ...]) for container nodes, or None for leaves."""
    if isinstance(node, Tree):
        return str(node.data), [(None, c) for c in node.children]
    if isinstance(node, Token):
        return None
    if is_dataclass(node) and not isinstance(node, type):
        return type(node).__name__, [
            (f.name, getattr(node, f.name))
            for f in fields(node)
            if show_positions or f.name not in POSITION_FIELDS
        ]
    if isinstance(node, (list, tuple)):
        return type(node).__name__, [(f"[{i}]", c) for i, c in enumerate(node)]
    if isinstance(node, dict):
        return "dict", [(repr(k), v) for k, v in node.items()]
    if hasattr(node, "__dict__") and not isinstance(node, (str, bytes, int, float, bool)):
        return type(node).__name__, list(vars(node).items())  # plain custom classes
    return None


def leaf(node):
    if isinstance(node, Token):
        return f"{node.type}({node.value!r})"
    return repr(node)

def render(node, name, prefix, is_last, is_root, out, show_positions, hide_none):
    connector = "" if is_root else ("└─ " if is_last else "├─ ")
    label = f"{name}: "

    # Custom pretty-print protocol
    pretty = getattr(node, "pretty", None)
    if callable(pretty):
        out.append(f"{prefix}{connector}{label}{pretty()}")
        return

    kids = children(node, show_positions)

    if kids is None or not kids[1]:
        text = leaf(node) if kids is None else f"{kids[0]} (empty)"
        out.append(f"{prefix}{connector}{label}{text}")
        return

    title, items = kids
    if hide_none:
        items = [(n, c) for n, c in items if c is not None]
        if not items:
            out.append(f"{prefix}{connector}{label}{title} (empty)")
            return

    out.append(f"{prefix}{connector}{label}{title}")
    child_prefix = prefix + ("" if is_root else ("   " if is_last else "│  "))

    for i, (child_name, child) in enumerate(items):
        render(
            child, child_name, child_prefix, i == len(items) - 1, False,
            out, show_positions, hide_none
        )


def pretty_ast(node, show_positions: bool = False, hide_none: bool = False) -> str:
    out = []
    render(node, None, "", True, True, out, show_positions, hide_none)
    return "\n".join(out)


