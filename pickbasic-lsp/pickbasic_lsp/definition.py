"""Go-to-definition logic for Pick BASIC."""

from lsprotocol.types import Location, Position, Range

from tree_sitter import Node


def find_definition(root_node: Node, uri: str, line: int, column: int) -> Location | None:
    """Find the definition of the symbol at the given position."""
    target_node = _node_at_position(root_node, line, column)
    if target_node is None:
        return None

    name = target_node.text.decode()
    parent = target_node.parent

    # GOTO/GOSUB target → find label
    if parent and parent.type in ("goto_statement", "gosub_statement", "on_goto_statement"):
        return _find_label(root_node, name, uri)

    # CALL target → find subroutine
    if parent and parent.type == "call_statement":
        return _find_subroutine(root_node, name, uri)

    # Variable reference → find EQUATE, DIM, or COMMON declaration
    if target_node.type == "identifier":
        return _find_declaration(root_node, name, uri)

    # Label name (number) used in GOTO/GOSUB
    if target_node.type == "number":
        return _find_label(root_node, name, uri)

    return None


def _find_label(root_node: Node, name: str, uri: str) -> Location | None:
    for node in root_node.children:
        if node.type == "label":
            name_node = node.child_by_field_name("name")
            if name_node and name_node.text.decode() == name:
                return _make_location(uri, node)
    return None


def _find_subroutine(root_node: Node, name: str, uri: str) -> Location | None:
    name_upper = name.upper()
    for node in root_node.children:
        if node.type == "subroutine_statement":
            for child in node.children:
                if child.type == "identifier" and child.text.decode().upper() == name_upper:
                    return _make_location(uri, node)
    return None


def _find_declaration(root_node: Node, name: str, uri: str) -> Location | None:
    """Find EQUATE, DIM, or COMMON declaration for a variable name."""
    name_upper = name.upper()
    for node in root_node.children:
        if node.type in ("equate_statement", "dim_statement", "common_statement"):
            for child in node.children:
                if child.type == "identifier" and child.text.decode().upper() == name_upper:
                    return _make_location(uri, node)
    return None


def _node_at_position(root_node: Node, line: int, column: int) -> Node | None:
    """Find the most specific (deepest) named node at the given position."""
    cursor = root_node.walk()

    def _search() -> Node | None:
        node = cursor.node
        if not _contains_position(node, line, column):
            return None

        # Try children
        if cursor.goto_first_child():
            while True:
                result = _search()
                if result is not None:
                    return result
                if not cursor.goto_next_sibling():
                    break
            cursor.goto_parent()

        # Return this node if it's a leaf or named
        if node.type in ("identifier", "number", "label_name", "string"):
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


def _make_location(uri: str, node: Node) -> Location:
    return Location(
        uri=uri,
        range=Range(
            start=Position(line=node.start_point.row, character=node.start_point.column),
            end=Position(line=node.end_point.row, character=node.end_point.column),
        ),
    )
