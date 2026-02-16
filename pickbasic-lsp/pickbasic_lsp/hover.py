"""Hover information for Pick BASIC keywords and functions."""

from lsprotocol.types import Hover, MarkupContent, MarkupKind, Position, Range

from tree_sitter import Node

# Pick BASIC keyword documentation
KEYWORD_INFO: dict[str, str] = {
    "IF": "**IF** *expression* **THEN** *statements* [**ELSE** *statements*]\n\nConditional execution.",
    "FOR": "**FOR** *var* **=** *start* **TO** *end* [**STEP** *inc*] ... **NEXT** *var*\n\nCounted loop.",
    "LOOP": "**LOOP** ... **WHILE**/**UNTIL** *condition* **DO** ... **REPEAT**\n\nConditional loop.",
    "GOTO": "**GOTO** *label*\n\nUnconditional branch to a label.",
    "GOSUB": "**GOSUB** *label*\n\nBranch to a subroutine at *label*, returning with **RETURN**.",
    "RETURN": "**RETURN** [**TO** *label*]\n\nReturn from a **GOSUB** subroutine.",
    "CALL": "**CALL** *name* [**(** *args* **)**]\n\nCall an external cataloged subroutine.",
    "SUBROUTINE": "**SUBROUTINE** [*name*] [**(** *args* **)**]\n\nDeclare an external subroutine entry point.",
    "DIM": "**DIM** *array* **(** *rows* [**,** *cols*] **)**\n\nDimension a static array.",
    "EQUATE": "**EQUATE** *name* **TO** *value*\n\nDefine a compile-time constant.",
    "EQU": "**EQU** *name* **TO** *value*\n\nDefine a compile-time constant (alias for EQUATE).",
    "COMMON": "**COMMON** [**/** *block* **/**] *var1*, *var2*, ...\n\nDeclare variables shared between chained programs.",
    "PRINT": "**PRINT** [*expression*] [**:** | **,** | **;**]\n\nOutput to the terminal.",
    "CRT": "**CRT** *expression*\n\nOutput to the CRT (screen).",
    "INPUT": "**INPUT** *var* [**,** *length*] [**:**]\n\nRead keyboard input into a variable.",
    "OPEN": '**OPEN** *dict*, *filename* **TO** *filevar* [**ELSE** *statements*]\n\nOpen a file for I/O.',
    "READ": "**READ** *var* **FROM** *filevar*, *id* [**THEN** ...] [**ELSE** ...]\n\nRead a record from an open file.",
    "WRITE": "**WRITE** *var* **ON** *filevar*, *id* [**THEN** ...] [**ELSE** ...]\n\nWrite a record to an open file.",
    "DELETE": "**DELETE** *filevar*, *id*\n\nDelete a record from a file.",
    "SELECT": "**SELECT** *filevar* [**TO** *list*]\n\nCreate a select list of record IDs.",
    "READNEXT": "**READNEXT** *id* [**FROM** *list*] [**THEN** ...] [**ELSE** ...]\n\nRead next ID from a select list.",
    "LOCATE": "**LOCATE** *expr* **IN** *dynarray* [**,** *pos*] **SETTING** *var* [**THEN** ...] [**ELSE** ...]\n\nSearch a dynamic array.",
    "EXECUTE": "**EXECUTE** *command* [**CAPTURING** *var*] [**RETURNING** *var*]\n\nExecute a TCL command.",
    "STOP": "**STOP** [*message*]\n\nTerminate program execution.",
    "ABORT": "**ABORT** [*message*]\n\nAbort program execution (no RETURN).",
    "PRECISION": "**PRECISION** *n*\n\nSet decimal precision for arithmetic.",
    "SLEEP": "**SLEEP** *seconds*\n\nPause execution for a number of seconds.",
    "LOCK": "**LOCK** *filevar*, *id* [**THEN** ...] [**ELSE** ...]\n\nLock a record for exclusive access.",
    "UNLOCK": "**UNLOCK** *filevar*, *id*\n\nRelease a record lock.",
    "RELEASE": "**RELEASE** [*filevar* [**,** *id*]]\n\nRelease record locks.",
    "BEGIN": "**BEGIN CASE** ... **CASE** *expr* ... **END CASE**\n\nMulti-way conditional.",
    "MAT": "**MAT** *array* **=** *value*\n\nAssign a value to all elements of a dimensioned array.",
    "MATREAD": "**MATREAD** *array* **FROM** *filevar*, *id* [**THEN** ...] [**ELSE** ...]\n\nRead a record into a dimensioned array.",
    "MATWRITE": "**MATWRITE** *array* **ON** *filevar*, *id*\n\nWrite a dimensioned array as a record.",
    "CHAIN": "**CHAIN** *program*\n\nTransfer control to another program.",
    "ENTER": "**ENTER** *program*\n\nTransfer control (no RETURN possible).",
    "DATA": "**DATA** *expression* [**,** *expression* ...]\n\nStack data for subsequent INPUT.",
    "PROMPT": '**PROMPT** *char*\n\nSet the INPUT prompt character.',
    "ON": "**ON** *expression* **GOTO**/**GOSUB** *label1*, *label2*, ...\n\nComputed branch.",
    "NULL": "**NULL**\n\nNo operation (placeholder statement).",
    "CLEAR": "**CLEAR**\n\nClear all variables to zero/empty.",
    "CLEARFILE": "**CLEARFILE** *filevar*\n\nDelete all records from a file.",
    "PAGE": "**PAGE** [*printer*]\n\nAdvance to next page on printer.",
    "HEADING": "**HEADING** *string*\n\nSet page heading for printer output.",
    "FOOTING": "**FOOTING** *string*\n\nSet page footing for printer output.",
    "PRINTER": "**PRINTER ON** | **OFF** | **CLOSE**\n\nControl printer output routing.",
    "BREAK": "**BREAK ON** | **OFF**\n\nEnable or disable the break key.",
    "ECHO": "**ECHO ON** | **OFF**\n\nEnable or disable terminal echo.",
}

# Pick BASIC intrinsic functions
FUNCTION_INFO: dict[str, str] = {
    "ABS": "**ABS(** *expr* **)** → Absolute value",
    "ALPHA": "**ALPHA(** *expr* **)** → Returns 1 if string is all alphabetic",
    "ASCII": "**ASCII(** *expr* **)** → Convert EBCDIC to ASCII",
    "CHAR": "**CHAR(** *n* **)** → Character from numeric code",
    "COL1": "**COL1()** → Column position before last FIELD extraction",
    "COL2": "**COL2()** → Column position after last FIELD extraction",
    "CONVERT": "**CONVERT(** *from*, *to*, *string* **)** → Replace characters",
    "COS": "**COS(** *expr* **)** → Cosine",
    "COUNT": "**COUNT(** *string*, *substring* **)** → Count occurrences",
    "DATE": "**DATE()** → Internal date (days since Dec 31, 1967)",
    "DCOUNT": "**DCOUNT(** *string*, *delimiter* **)** → Count delimited fields",
    "DELETE": "**DELETE(** *dynarray*, *amc* [**,** *vmc* [**,** *svmc*]] **)** → Delete from dynamic array",
    "DOWNCASE": "**DOWNCASE(** *string* **)** → Convert to lowercase",
    "DQUOTE": "**DQUOTE(** *string* **)** → Wrap in double quotes",
    "DTX": "**DTX(** *decimal* **)** → Decimal to hexadecimal",
    "EBCDIC": "**EBCDIC(** *string* **)** → Convert ASCII to EBCDIC",
    "EXCHANGE": "**EXCHANGE(** *string*, *from*, *to* **)** → Character exchange",
    "EXP": "**EXP(** *expr* **)** → Natural exponential (e^x)",
    "EXTRACT": "**EXTRACT(** *dynarray*, *amc* [**,** *vmc* [**,** *svmc*]] **)** → Extract from dynamic array",
    "FIELD": "**FIELD(** *string*, *delim*, *occurrence* [**,** *count*] **)** → Extract delimited field",
    "FIELDSTORE": "**FIELDSTORE(** *string*, *delim*, *start*, *count*, *new* **)** → Replace delimited fields",
    "FMT": "**FMT(** *expr*, *format* **)** → Format expression for output",
    "FOLD": "**FOLD(** *string*, *length* **)** → Word-wrap string",
    "ICONV": "**ICONV(** *string*, *code* **)** → Input conversion",
    "INDEX": "**INDEX(** *string*, *substring*, *occurrence* **)** → Find position of substring",
    "INMAT": "**INMAT()** → Number of elements from last MATREAD",
    "INSERT": "**INSERT(** *dynarray*, *amc* [**,** *vmc* [**,** *svmc*]]**;** *value* **)** → Insert into dynamic array",
    "INT": "**INT(** *expr* **)** → Integer portion",
    "LEN": "**LEN(** *string* **)** → String length",
    "LN": "**LN(** *expr* **)** → Natural logarithm",
    "MOD": "**MOD(** *dividend*, *divisor* **)** → Modulo (remainder)",
    "NOT": "**NOT(** *expr* **)** → Logical negation",
    "NUM": "**NUM(** *string* **)** → Returns 1 if string is numeric",
    "OCONV": "**OCONV(** *expr*, *code* **)** → Output conversion",
    "PWR": "**PWR(** *base*, *exponent* **)** → Power",
    "REPLACE": "**REPLACE(** *dynarray*, *amc* [**,** *vmc* [**,** *svmc*]]**;** *value* **)** → Replace in dynamic array",
    "RND": "**RND(** *range* **)** → Random number 0 to range-1",
    "SEQ": "**SEQ(** *char* **)** → Numeric code of character",
    "SIN": "**SIN(** *expr* **)** → Sine",
    "SOUNDEX": "**SOUNDEX(** *string* **)** → Soundex code",
    "SPACE": "**SPACE(** *n* **)** → String of n spaces",
    "SQRT": "**SQRT(** *expr* **)** → Square root",
    "STATUS": "**STATUS()** → Status of last file operation",
    "STR": "**STR(** *string*, *count* **)** → Repeat string",
    "SYSTEM": "**SYSTEM(** *n* **)** → System information by code number",
    "TAN": "**TAN(** *expr* **)** → Tangent",
    "TIME": "**TIME()** → Internal time (seconds since midnight)",
    "TIMEDATE": "**TIMEDATE()** → Current time and date string",
    "TRIM": "**TRIM(** *string* **)** → Remove leading/trailing spaces",
    "TRIMB": "**TRIMB(** *string* **)** → Trim trailing spaces",
    "TRIMF": "**TRIMF(** *string* **)** → Trim leading spaces",
    "UPCASE": "**UPCASE(** *string* **)** → Convert to uppercase",
    "XTD": "**XTD(** *hex* **)** → Hexadecimal to decimal",
}


def get_hover(root_node: Node, line: int, column: int) -> Hover | None:
    """Get hover information for the node at the given position."""
    node = _node_at_position(root_node, line, column)
    if node is None:
        return None

    text = node.text.decode()
    text_upper = text.upper()

    # Check if it's a keyword
    if text_upper in KEYWORD_INFO:
        return _make_hover(KEYWORD_INFO[text_upper], node)

    # Check if it's a function call
    parent = node.parent
    if parent and parent.type == "function_call" and node == parent.child_by_field_name("name"):
        if text_upper in FUNCTION_INFO:
            return _make_hover(FUNCTION_INFO[text_upper], node)
        return _make_hover(f"**{text}()**\n\nFunction call", node)

    # Check standalone function name
    if text_upper in FUNCTION_INFO:
        return _make_hover(FUNCTION_INFO[text_upper], node)

    # Label
    if node.type == "label_name":
        return _make_hover(f"**Label** `{text}`", node)

    # Variable/identifier - show what it is
    if node.type == "identifier":
        decl = _find_declaration_type(root_node, text_upper)
        if decl:
            return _make_hover(decl, node)
        return _make_hover(f"**Variable** `{text}`", node)

    return None


def _find_declaration_type(root_node: Node, name_upper: str) -> str | None:
    for node in root_node.children:
        if node.type == "equate_statement":
            for child in node.children:
                if child.type == "identifier" and child.text.decode().upper() == name_upper:
                    return f"**EQUATE** constant\n\n`{node.text.decode()}`"
        elif node.type == "dim_statement":
            for child in node.children:
                if child.type == "identifier" and child.text.decode().upper() == name_upper:
                    return f"**DIM** array\n\n`{node.text.decode()}`"
        elif node.type == "common_statement":
            for child in node.children:
                if child.type == "identifier" and child.text.decode().upper() == name_upper:
                    return f"**COMMON** variable\n\n`{node.text.decode()}`"
    return None


def _node_at_position(root_node: Node, line: int, column: int) -> Node | None:
    cursor = root_node.walk()

    def _search() -> Node | None:
        node = cursor.node
        start = node.start_point
        end = node.end_point
        if line < start.row or line > end.row:
            return None
        if line == start.row and column < start.column:
            return None
        if line == end.row and column >= end.column:
            return None

        if cursor.goto_first_child():
            while True:
                result = _search()
                if result is not None:
                    return result
                if not cursor.goto_next_sibling():
                    break
            cursor.goto_parent()

        if node.child_count == 0 or node.type in ("identifier", "number", "label_name"):
            return node
        return None

    return _search()


def _make_hover(content: str, node: Node) -> Hover:
    return Hover(
        contents=MarkupContent(kind=MarkupKind.Markdown, value=content),
        range=Range(
            start=Position(line=node.start_point.row, character=node.start_point.column),
            end=Position(line=node.end_point.row, character=node.end_point.column),
        ),
    )
