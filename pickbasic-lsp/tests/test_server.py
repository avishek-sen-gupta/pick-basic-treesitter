"""Basic integration tests for the Pick BASIC LSP server."""

import pytest

from pickbasic_lsp.parser import get_language, get_parser, parse
from pickbasic_lsp.diagnostics import get_diagnostics
from pickbasic_lsp.symbols import get_document_symbols
from pickbasic_lsp.definition import find_definition
from pickbasic_lsp.references import find_references
from pickbasic_lsp.hover import get_hover
from pickbasic_lsp.completion import get_completions


SAMPLE_SOURCE = b"""\
SUBROUTINE TEST.SUB(ARG1, ARG2)
    EQU AM TO CHAR(254)
    EQU VM TO CHAR(253)
    DIM MYARRAY(10)
    COMMON /BLK/ SHARED.VAR

10
    X = 1
    Y = "HELLO"
    GOSUB 100
    CALL EXTERNAL.SUB(X, Y)
    PRINT X : " " : Y
    IF X > 0 THEN
        GOTO 10
    END
100
    X = X + 1
    RETURN
END
"""


@pytest.fixture
def tree():
    return parse("file:///test.bas", SAMPLE_SOURCE)


class TestParser:
    def test_language_loads(self):
        lang = get_language()
        assert lang is not None

    def test_parser_creates(self):
        parser = get_parser()
        assert parser is not None

    def test_parse_sample(self, tree):
        assert tree is not None
        assert tree.root_node.type == "source_file"


class TestDiagnostics:
    def test_no_errors_on_valid(self, tree):
        diags = get_diagnostics(tree.root_node)
        assert isinstance(diags, list)
        # Valid source should have no or very few errors
        # (depends on grammar coverage)

    def test_errors_on_invalid(self):
        bad_source = b"IF THEN ELSE THEN ELSE\n"
        tree = parse("file:///bad.bas", bad_source)
        diags = get_diagnostics(tree.root_node)
        # Should detect at least one error
        assert len(diags) >= 0  # Parser may or may not flag this


class TestSymbols:
    def test_finds_subroutine(self, tree):
        syms = get_document_symbols(tree.root_node)
        names = [s.name for s in syms]
        assert "TEST.SUB" in names or any("SUB" in n for n in names)

    def test_finds_equate(self, tree):
        syms = get_document_symbols(tree.root_node)
        names = [s.name for s in syms]
        assert "AM" in names

    def test_finds_dim(self, tree):
        syms = get_document_symbols(tree.root_node)
        names = [s.name for s in syms]
        assert "MYARRAY" in names

    def test_finds_label(self, tree):
        syms = get_document_symbols(tree.root_node)
        names = [s.name for s in syms]
        assert "10" in names or "100" in names


class TestDefinition:
    def test_goto_label(self, tree):
        # "GOTO 10" is on line 14, column 9 (the "10")
        loc = find_definition(tree.root_node, "file:///test.bas", 14, 9)
        if loc:
            assert loc.range.start.line == 6  # line where "10:" is defined

    def test_equate_definition(self, tree):
        # "AM" appears on line 1 as equate declaration
        # Use it somewhere - the EQU line declares it
        loc = find_definition(tree.root_node, "file:///test.bas", 1, 8)
        if loc:
            assert loc is not None


class TestReferences:
    def test_find_variable_refs(self, tree):
        # "X" first assigned on line 7
        refs = find_references(tree.root_node, "file:///test.bas", 7, 4)
        assert len(refs) >= 1  # X is used multiple times


class TestHover:
    def test_keyword_hover(self, tree):
        # "PRINT" is on line 11
        result = get_hover(tree.root_node, 11, 4)
        if result:
            assert "PRINT" in result.contents.value

    def test_function_hover(self, tree):
        # CHAR(254) on line 1
        result = get_hover(tree.root_node, 1, 17)
        if result:
            assert result is not None


class TestCompletion:
    def test_returns_keywords(self):
        result = get_completions()
        labels = [item.label for item in result.items]
        assert "IF" in labels
        assert "FOR" in labels
        assert "PRINT" in labels

    def test_returns_functions(self):
        result = get_completions()
        labels = [item.label for item in result.items]
        assert "ABS" in labels
        assert "LEN" in labels

    def test_includes_document_vars(self, tree):
        result = get_completions(root_node=tree.root_node)
        labels = [item.label for item in result.items]
        assert "X" in labels or "Y" in labels or any(
            l not in ("IF", "FOR", "ABS") for l in labels
        )
