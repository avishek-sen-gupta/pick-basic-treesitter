"""Extract parse errors as LSP diagnostics."""

from lsprotocol.types import Diagnostic, DiagnosticSeverity, Position, Range

from tree_sitter import Node


def get_diagnostics(root_node: Node) -> list[Diagnostic]:
    """Walk the tree and collect ERROR/MISSING nodes as diagnostics."""
    diagnostics: list[Diagnostic] = []
    _collect_errors(root_node, diagnostics)
    return diagnostics


def _collect_errors(node: Node, diagnostics: list[Diagnostic]):
    if node.is_missing:
        diagnostics.append(
            Diagnostic(
                range=_node_range(node),
                message=f"Missing {node.type}",
                severity=DiagnosticSeverity.Error,
                source="pickbasic",
            )
        )
    elif node.type == "ERROR":
        diagnostics.append(
            Diagnostic(
                range=_node_range(node),
                message="Syntax error",
                severity=DiagnosticSeverity.Error,
                source="pickbasic",
            )
        )
    else:
        for child in node.children:
            _collect_errors(child, diagnostics)


def _node_range(node: Node) -> Range:
    return Range(
        start=Position(line=node.start_point.row, character=node.start_point.column),
        end=Position(line=node.end_point.row, character=node.end_point.column),
    )
