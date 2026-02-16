"""Extract document symbols from the parse tree."""

from lsprotocol.types import DocumentSymbol, Position, Range, SymbolKind

from tree_sitter import Node


def get_document_symbols(root_node: Node) -> list[DocumentSymbol]:
    """Walk the tree and extract labels, subroutines, DIM, EQUATE, COMMON."""
    symbols: list[DocumentSymbol] = []
    for node in root_node.children:
        sym = _extract_symbol(node)
        if sym is not None:
            symbols.append(sym)
    return symbols


def _extract_symbol(node: Node) -> DocumentSymbol | None:
    if node.type == "label":
        name_node = node.child_by_field_name("name")
        if name_node:
            return _make_symbol(
                name=name_node.text.decode(),
                kind=SymbolKind.Key,
                node=node,
            )

    elif node.type == "subroutine_statement":
        # SUBROUTINE name(args)
        name = _get_first_child_text(node, "identifier")
        if name:
            return _make_symbol(name=name, kind=SymbolKind.Function, node=node)

    elif node.type == "dim_statement":
        # DIM var(size) — identifier is inside dim_spec child
        name = _get_first_child_text(node, "identifier")
        if not name:
            dim_spec = _get_first_child(node, "dim_spec")
            if dim_spec:
                name = _get_first_child_text(dim_spec, "identifier")
        if name:
            return _make_symbol(name=name, kind=SymbolKind.Array, node=node)

    elif node.type == "equate_statement":
        # EQUATE name TO value / EQU name TO value
        name = _get_first_child_text(node, "identifier")
        if name:
            return _make_symbol(name=name, kind=SymbolKind.Constant, node=node)

    elif node.type == "common_statement":
        # COMMON /block/ var1, var2
        # Try to get the block name or first variable
        name = _get_first_child_text(node, "identifier")
        if name:
            return _make_symbol(name=name, kind=SymbolKind.Namespace, node=node)

    return None


def _get_first_child(node: Node, child_type: str) -> Node | None:
    for child in node.children:
        if child.type == child_type:
            return child
    return None


def _get_first_child_text(node: Node, child_type: str) -> str | None:
    child = _get_first_child(node, child_type)
    return child.text.decode() if child else None


def _node_range(node: Node) -> Range:
    return Range(
        start=Position(line=node.start_point.row, character=node.start_point.column),
        end=Position(line=node.end_point.row, character=node.end_point.column),
    )


def _make_symbol(name: str, kind: SymbolKind, node: Node) -> DocumentSymbol:
    r = _node_range(node)
    return DocumentSymbol(
        name=name,
        kind=kind,
        range=r,
        selection_range=r,
    )
