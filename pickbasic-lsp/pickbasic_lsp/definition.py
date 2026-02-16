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

    # Clicking on a GOTO/GOSUB/ON keyword → extract the target from the statement
    if parent and parent.type in ("goto_statement", "gosub_statement", "on_goto_statement"):
        if target_node.type in ("identifier", "number", "label_name"):
            return _find_label(root_node, name, uri)
        # Clicked on the keyword itself — find the target number/identifier child
        target = _get_goto_target(parent)
        if target:
            return _find_label(root_node, target, uri)
        return None

    # CALL target → find subroutine
    if parent and parent.type == "call_statement":
        if target_node.type == "identifier":
            return _find_subroutine(root_node, name, uri)
        # Clicked on CALL keyword — find the identifier child
        for child in parent.children:
            if child.type == "identifier":
                return _find_subroutine(root_node, child.text.decode(), uri)
        return None

    # Variable reference → find declaration or first assignment
    if target_node.type == "identifier":
        return _find_declaration(root_node, name, uri)

    # Bare number — could be a label reference
    if target_node.type == "number":
        return _find_label(root_node, name, uri)

    return None


def _get_goto_target(statement_node: Node) -> str | None:
    """Extract the target label name/number from a GOTO/GOSUB statement."""
    for child in statement_node.children:
        if child.type in ("number", "identifier", "label_name"):
            return child.text.decode()
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
    """Find where a variable is declared or first assigned.

    Search order (first match wins):
    1. EQUATE/EQU statement
    2. DIM statement (including inside dim_spec)
    3. COMMON statement
    4. SUBROUTINE parameter list
    5. FOR loop variable
    6. First assignment (X = ...)
    """
    name_upper = name.upper()

    # Pass 1: explicit declarations (EQU, DIM, COMMON, SUBROUTINE params)
    for node in root_node.children:
        if node.type in ("equate_statement", "common_statement"):
            for child in node.children:
                if child.type == "identifier" and child.text.decode().upper() == name_upper:
                    return _make_location(uri, node)

        if node.type == "dim_statement":
            if _has_identifier(node, name_upper):
                return _make_location(uri, node)

        if node.type == "subroutine_statement":
            for child in node.children:
                if child.type == "identifier" and child.text.decode().upper() == name_upper:
                    return _make_location(uri, node)

    # Pass 2: FOR loop variable (FOR I = ...)
    result = _find_for_variable(root_node, name_upper, uri)
    if result:
        return result

    # Pass 3: first assignment (X = ...)
    result = _find_first_assignment(root_node, name_upper, uri)
    if result:
        return result

    return None


def _has_identifier(node: Node, name_upper: str) -> bool:
    """Recursively check if a node tree contains an identifier with the given name."""
    if node.type == "identifier" and node.text.decode().upper() == name_upper:
        return True
    for child in node.children:
        if _has_identifier(child, name_upper):
            return True
    return False


def _find_for_variable(node: Node, name_upper: str, uri: str) -> Location | None:
    """Find a FOR statement that declares this loop variable."""
    if node.type == "for_statement":
        var_node = node.child_by_field_name("variable")
        if var_node and var_node.text.decode().upper() == name_upper:
            return _make_location(uri, node)
        # Fallback: check first identifier child after FOR keyword
        for child in node.children:
            if child.type in ("identifier", "lvalue"):
                text = child.text.decode().upper()
                if text == name_upper:
                    return _make_location(uri, node)
                break  # only check the first one

    for child in node.children:
        result = _find_for_variable(child, name_upper, uri)
        if result:
            return result
    return None


def _find_first_assignment(node: Node, name_upper: str, uri: str) -> Location | None:
    """Find the first assignment_statement where the lvalue matches."""
    if node.type == "assignment_statement":
        for child in node.children:
            if child.type == "lvalue":
                if child.text.decode().upper() == name_upper:
                    return _make_location(uri, node)
                break  # only check the lvalue (first child)

    for child in node.children:
        result = _find_first_assignment(child, name_upper, uri)
        if result:
            return result
    return None


def _node_at_position(root_node: Node, line: int, column: int) -> Node | None:
    """Find the most specific (deepest) node at the given position."""
    cursor = root_node.walk()

    def _search() -> Node | None:
        node = cursor.node
        if not _contains_position(node, line, column):
            return None

        # Try children first (deepest match wins)
        if cursor.goto_first_child():
            while True:
                result = _search()
                if result is not None:
                    return result
                if not cursor.goto_next_sibling():
                    break
            cursor.goto_parent()

        # Return any leaf node (identifiers, numbers, keywords, operators)
        if node.child_count == 0:
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
