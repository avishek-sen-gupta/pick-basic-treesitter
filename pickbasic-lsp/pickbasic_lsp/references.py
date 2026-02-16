"""Find all references to a symbol in a document."""

from lsprotocol.types import Location, Position, Range

from tree_sitter import Node


def find_references(
    root_node: Node, uri: str, line: int, column: int, include_declaration: bool = True
) -> list[Location]:
    """Find all references to the symbol at the given position."""
    target_node = _node_at_position(root_node, line, column)
    if target_node is None:
        return []

    name = target_node.text.decode()
    locations: list[Location] = []
    _collect_references(root_node, name, uri, locations)
    return locations


def _collect_references(node: Node, name: str, uri: str, locations: list[Location]):
    """Recursively collect all nodes matching the given name."""
    if node.type in ("identifier", "label_name") and node.text.decode().upper() == name.upper():
        locations.append(
            Location(
                uri=uri,
                range=Range(
                    start=Position(line=node.start_point.row, character=node.start_point.column),
                    end=Position(line=node.end_point.row, character=node.end_point.column),
                ),
            )
        )
    elif node.type == "number" and node.text.decode() == name:
        # Numeric labels
        parent = node.parent
        if parent and parent.type in ("label", "goto_statement", "gosub_statement", "on_goto_statement"):
            locations.append(
                Location(
                    uri=uri,
                    range=Range(
                        start=Position(line=node.start_point.row, character=node.start_point.column),
                        end=Position(line=node.end_point.row, character=node.end_point.column),
                    ),
                )
            )

    for child in node.children:
        _collect_references(child, name, uri, locations)


def _node_at_position(root_node: Node, line: int, column: int) -> Node | None:
    """Find the most specific named node at the given position."""
    cursor = root_node.walk()

    def _search() -> Node | None:
        node = cursor.node
        if not _contains_position(node, line, column):
            return None
        if cursor.goto_first_child():
            while True:
                result = _search()
                if result is not None:
                    return result
                if not cursor.goto_next_sibling():
                    break
            cursor.goto_parent()
        if node.type in ("identifier", "number", "label_name"):
            return node
        return None

    return _search()


def _contains_position(node: Node, line: int, column: int) -> bool:
    start = node.start_point
    end = node.end_point
    if line < start.row or line > end.row:
        return False
    if line == start.row and column < start.column:
        return False
    if line == end.row and column >= end.column:
        return False
    return True
