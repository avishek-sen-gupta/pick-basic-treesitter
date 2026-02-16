"""Pick BASIC Language Server using pygls."""

from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DEFINITION,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_CLOSE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DOCUMENT_SYMBOL,
    TEXT_DOCUMENT_HOVER,
    TEXT_DOCUMENT_REFERENCES,
    TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    CompletionList,
    CompletionOptions,
    CompletionParams,
    DefinitionParams,
    DidChangeTextDocumentParams,
    DidCloseTextDocumentParams,
    DidOpenTextDocumentParams,
    DocumentSymbolParams,
    Hover,
    HoverParams,
    Location,
    ReferenceParams,
    SemanticTokens,
    SemanticTokensLegend,
    SemanticTokensParams,
    TextDocumentSyncKind,
)

from pygls.server import LanguageServer

from . import completion as comp_mod
from . import definition as def_mod
from . import diagnostics as diag_mod
from . import hover as hover_mod
from . import parser as parser_mod
from . import references as ref_mod
from . import symbols as sym_mod

# Semantic token types matching highlights.scm categories
TOKEN_TYPES = [
    "keyword",
    "operator",
    "number",
    "string",
    "function",
    "variable",
    "label",
    "comment",
]
TOKEN_MODIFIERS = ["declaration", "readonly"]


server = LanguageServer("pickbasic-lsp", "v0.1.0")


def _publish_diagnostics(ls: LanguageServer, uri: str):
    tree = parser_mod.get_tree(uri)
    if tree is None:
        return
    diags = diag_mod.get_diagnostics(tree.root_node)
    ls.publish_diagnostics(uri, diags)


@server.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: LanguageServer, params: DidOpenTextDocumentParams):
    uri = params.text_document.uri
    source = params.text_document.text.encode("utf-8")
    parser_mod.parse(uri, source)
    _publish_diagnostics(ls, uri)


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: LanguageServer, params: DidChangeTextDocumentParams):
    uri = params.text_document.uri
    # Full sync: use the last content change
    if params.content_changes:
        source = params.content_changes[-1].text.encode("utf-8")
        parser_mod.parse(uri, source)
        _publish_diagnostics(ls, uri)


@server.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(ls: LanguageServer, params: DidCloseTextDocumentParams):
    uri = params.text_document.uri
    parser_mod.remove_tree(uri)


@server.feature(TEXT_DOCUMENT_DOCUMENT_SYMBOL)
def document_symbol(ls: LanguageServer, params: DocumentSymbolParams):
    tree = parser_mod.get_tree(params.text_document.uri)
    if tree is None:
        return []
    return sym_mod.get_document_symbols(tree.root_node)


@server.feature(TEXT_DOCUMENT_DEFINITION)
def definition(ls: LanguageServer, params: DefinitionParams) -> Location | None:
    tree = parser_mod.get_tree(params.text_document.uri)
    if tree is None:
        return None
    return def_mod.find_definition(
        tree.root_node,
        params.text_document.uri,
        params.position.line,
        params.position.character,
    )


@server.feature(TEXT_DOCUMENT_REFERENCES)
def references(ls: LanguageServer, params: ReferenceParams) -> list[Location]:
    tree = parser_mod.get_tree(params.text_document.uri)
    if tree is None:
        return []
    return ref_mod.find_references(
        tree.root_node,
        params.text_document.uri,
        params.position.line,
        params.position.character,
        include_declaration=params.context.include_declaration,
    )


@server.feature(TEXT_DOCUMENT_HOVER)
def hover(ls: LanguageServer, params: HoverParams) -> Hover | None:
    tree = parser_mod.get_tree(params.text_document.uri)
    if tree is None:
        return None
    return hover_mod.get_hover(
        tree.root_node,
        params.position.line,
        params.position.character,
    )


@server.feature(
    TEXT_DOCUMENT_COMPLETION,
    CompletionOptions(trigger_characters=["."]),
)
def completions(ls: LanguageServer, params: CompletionParams) -> CompletionList:
    tree = parser_mod.get_tree(params.text_document.uri)
    root = tree.root_node if tree else None
    return comp_mod.get_completions(root_node=root)


@server.feature(
    TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    SemanticTokensLegend(
        token_types=TOKEN_TYPES,
        token_modifiers=TOKEN_MODIFIERS,
    ),
)
def semantic_tokens_full(ls: LanguageServer, params: SemanticTokensParams) -> SemanticTokens:
    tree = parser_mod.get_tree(params.text_document.uri)
    if tree is None:
        return SemanticTokens(data=[])
    return SemanticTokens(data=_encode_semantic_tokens(tree.root_node))


def _encode_semantic_tokens(root_node) -> list[int]:
    """Encode all leaf nodes as semantic tokens in LSP format."""
    tokens: list[tuple[int, int, int, int, int]] = []
    _collect_tokens(root_node, tokens)

    # Sort by position
    tokens.sort(key=lambda t: (t[0], t[1]))

    # Encode as relative positions
    data: list[int] = []
    prev_line = 0
    prev_start = 0
    for line, start, length, token_type, modifiers in tokens:
        delta_line = line - prev_line
        delta_start = start - prev_start if delta_line == 0 else start
        data.extend([delta_line, delta_start, length, token_type, modifiers])
        prev_line = line
        prev_start = start

    return data


# Map node types to token type indices
_NODE_TYPE_MAP = {
    "comment": 7,
    "inline_comment": 7,
    "number": 2,
    "string": 3,
    "identifier": 5,
    "label_name": 6,
}

# Keywords from highlights.scm
_KEYWORDS = {
    "IF", "THEN", "ELSE", "END", "FOR", "TO", "STEP", "NEXT", "WHILE", "UNTIL",
    "DO", "LOOP", "REPEAT", "BEGIN", "CASE", "GOTO", "GO", "GOSUB", "SUB", "ON",
    "RETURN", "STOP", "ABORT", "DIM", "DIMENSION", "COMMON", "COM", "EQUATE", "EQU",
    "SUBROUTINE", "CALL", "NULL", "CLEAR", "PRECISION", "PRINT", "CRT", "INPUT",
    "INPUT@", "INPUTERR", "INPUTNULL", "INPUTTRAP", "DATA", "PROMPT", "PAGE",
    "HEADING", "FOOTING", "PRINTER", "BREAK", "ECHO", "OPEN", "READ", "READU",
    "READV", "READVU", "WRITE", "WRITEU", "WRITEV", "WRITEVU", "DELETE",
    "READNEXT", "READT", "WRITET", "SELECT", "LOCK", "UNLOCK", "RELEASE",
    "CLEARFILE", "MATREAD", "MATREADU", "MATWRITE", "MATWRITEU", "LOCATE", "FROM",
    "SETTING", "IN", "LOCKED", "LITERALLY", "ERROR", "EXECUTE", "CAPTURING",
    "RETURNING", "CHAIN", "ENTER", "SLEEP", "RQM", "MAT", "PROCREAD", "PROCWRITE",
    "REWIND", "WEOF",
}

_OPERATORS = {
    "AND", "OR", "NOT", "CAT", "MATCH", "MATCHES", "EQ", "NE", "LT", "GT", "LE", "GE",
    "+", "-", "*", "/", "^", "**", ":", "=", "<", ">", "<>", "#", "<=", ">=", "=<", "=>",
}


def _collect_tokens(node, tokens: list):
    # Leaf nodes
    if node.child_count == 0:
        text = node.text.decode() if node.text else ""
        text_upper = text.upper()
        row = node.start_point.row
        col = node.start_point.column
        length = node.end_point.column - node.start_point.column
        if node.start_point.row != node.end_point.row:
            # Multi-line token: use full byte length for first line
            length = len(text.split("\n")[0]) if "\n" in text else len(text)

        if length <= 0:
            return

        if node.type in _NODE_TYPE_MAP:
            # Check if identifier is actually a function name
            token_type = _NODE_TYPE_MAP[node.type]
            if node.type == "identifier" and node.parent and node.parent.type == "function_call":
                if node == node.parent.child_by_field_name("name"):
                    token_type = 4  # function
            tokens.append((row, col, length, token_type, 0))
        elif text_upper in _KEYWORDS:
            tokens.append((row, col, length, 0, 0))  # keyword
        elif text_upper in _OPERATORS or text in _OPERATORS:
            tokens.append((row, col, length, 1, 0))  # operator
        return

    # Comments are named nodes but not leaves in all cases
    if node.type in ("comment", "inline_comment"):
        row = node.start_point.row
        col = node.start_point.column
        if node.start_point.row == node.end_point.row:
            length = node.end_point.column - node.start_point.column
        else:
            length = len(node.text.decode().split("\n")[0])
        if length > 0:
            tokens.append((row, col, length, 7, 0))
        return

    for child in node.children:
        _collect_tokens(child, tokens)
