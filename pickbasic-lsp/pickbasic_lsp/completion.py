"""Completion provider for Pick BASIC keywords and functions."""

from lsprotocol.types import CompletionItem, CompletionItemKind, CompletionList

KEYWORDS = [
    "ABORT", "AND", "BEGIN", "BREAK", "BY", "CALL", "CASE", "CHAIN",
    "CLEAR", "CLEARFILE", "CLOSE", "COM", "COMMON", "CONVERT", "CRT",
    "DATA", "DELETE", "DIM", "DIMENSION", "DO", "ECHO", "ELSE", "END",
    "ENTER", "EQU", "EQUATE", "ERROR", "EXECUTE", "EXIT", "FOR",
    "FOOTING", "FROM", "GO", "GOSUB", "GOTO", "HEADING", "IF", "IN",
    "INPUT", "INPUTERR", "INPUTNULL", "INPUTTRAP", "LOCKED",
    "LITERALLY", "LOCATE", "LOCK", "LOOP", "MAT", "MATREAD",
    "MATREADU", "MATWRITE", "MATWRITEU", "NEXT", "NOT", "NULL", "ON",
    "OPEN", "OR", "PAGE", "PRECISION", "PRINT", "PRINTER", "PROCREAD",
    "PROCWRITE", "PROMPT", "READ", "READNEXT", "READT", "READU",
    "READV", "READVU", "RELEASE", "REPEAT", "RETURN", "RETURNING",
    "REWIND", "RQM", "SELECT", "SETTING", "SLEEP", "STEP", "STOP",
    "SUB", "SUBROUTINE", "THEN", "TO", "UNLOCK", "UNTIL", "WEOF",
    "WHILE", "WRITE", "WRITEU", "WRITET", "WRITEV", "WRITEVU",
    "CAPTURING",
]

FUNCTIONS = [
    "ABS", "ALPHA", "ASCII", "CHAR", "COL1", "COL2", "CONVERT", "COS",
    "COUNT", "DATE", "DCOUNT", "DELETE", "DOWNCASE", "DQUOTE", "DTX",
    "EBCDIC", "EXCHANGE", "EXP", "EXTRACT", "FIELD", "FIELDSTORE",
    "FMT", "FOLD", "ICONV", "INDEX", "INMAT", "INSERT", "INT", "LEN",
    "LN", "MOD", "NOT", "NUM", "OCONV", "PWR", "REPLACE", "RND",
    "SEQ", "SIN", "SOUNDEX", "SPACE", "SQRT", "STATUS", "STR",
    "SYSTEM", "TAN", "TIME", "TIMEDATE", "TRIM", "TRIMB", "TRIMF",
    "UPCASE", "XTD",
]


def get_completions(root_node=None, source: bytes = b"") -> CompletionList:
    """Return completion items for keywords, functions, and document variables."""
    items: list[CompletionItem] = []

    for kw in KEYWORDS:
        items.append(
            CompletionItem(
                label=kw,
                kind=CompletionItemKind.Keyword,
            )
        )

    for fn in FUNCTIONS:
        items.append(
            CompletionItem(
                label=fn,
                kind=CompletionItemKind.Function,
                insert_text=f"{fn}(",
            )
        )

    # Add document-local variable names
    if root_node is not None:
        seen: set[str] = set()
        _collect_identifiers(root_node, seen)
        for name in sorted(seen):
            items.append(
                CompletionItem(
                    label=name,
                    kind=CompletionItemKind.Variable,
                )
            )

    return CompletionList(is_incomplete=False, items=items)


def _collect_identifiers(node, seen: set[str]):
    if node.type == "identifier":
        name = node.text.decode()
        if name.upper() not in {k.upper() for k in KEYWORDS} and name.upper() not in {f.upper() for f in FUNCTIONS}:
            seen.add(name)
    for child in node.children:
        _collect_identifiers(child, seen)
