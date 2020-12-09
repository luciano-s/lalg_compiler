import re
import pytest

from src.validator import Validator


def test_number_lexem():
    """
    Test if it can validate a number
    """

    lexems = [
        "197",
        "1",
        "10",
        "37",
        "58",
        "5",
        "1a2",
        ".",
        "1.",
    ]

    validator = Validator()
    assert validator.validate_lexems(lexems) == [
        {"197": "<NUMBER>"},
        {"1": "<NUMBER>"},
        {"10": "<NUMBER>"},
        {"37": "<NUMBER>"},
        {"58": "<NUMBER>"},
        {"5": "<NUMBER>"},
        {"1a2":  None},
        {".": None},
        {"1.": None},
    ]


# def test_sign_lexem():
#     """
#     Test if it can validate a sign lexem, +, -, * and /
#     """
#     lexems = ["+", "-", "*", "/", "=", "batata",
#               "#", "@", "!", "_", "$", "%", "(", ")"]
#     validator = Validator()
#     assert validator.validate_lexems(lexems) == [
#         {"+": "<PLUS_SIGN>"},
#         {"-": "<MINUS_SIGN>"},
#         {"*": "<MULTIPLICATION_SIGN>"},
#         {"/": "<DIVISION_SIGN>"},
#         {"=": "<EQUALS_SIGN>"},
#         {"batata": None},
#         {"#": None},
#         {"@": None},
#         {"!": None},
#         {"_": None},
#         {"$": None},
#         {"%": None},
#         {"(": "<OPEN_PARENTHESIS>"},
#         {")": "<CLOSE_PARENTHESIS>"},
#     ]


def test_identifier():
    """
    Test if it can validate a identifier
    """

    lexems = [
        "_",
        "_a",
        "a1",
        "1",
        "a111*",
        " ",
        "a_1",
        "#$&",
    ]

    validator = Validator()
    assert validator.validate_lexems(lexems) == [
        {"_": "<IDENTIFIER>"},
        {"_a": "<IDENTIFIER>"},
        {"a1": "<IDENTIFIER>"},
        {"1": "<NUMBER>"},
        {"a111*": None},
        {" ": None},
        {"a_1": "<IDENTIFIER>"},
        {"#$&": None},
    ]


def test_simple_type():
    """
    Test if it can validate a simple type
    """

    lexems = [
        "_",
        "_a",
        "a1",
        "int_",
        "int",
        "int ",
        "real",
        "boolean",
        "bolean"
    ]

    validator = Validator()
    assert validator.validate_lexems(lexems) == [
        {"_": "<IDENTIFIER>"},
        {"_a": "<IDENTIFIER>"},
        {"a1": "<IDENTIFIER>"},
        {"int_": "<IDENTIFIER>"},
        {"int": "<SIMPLE_TYPE>"},
        {"int ": None},
        {"real": "<SIMPLE_TYPE>"},
        {"boolean": "<SIMPLE_TYPE>"},
        {"bolean": "<IDENTIFIER>"},
    ]


def test_relation():
    """
    Test if it can validate a relation
    """

    lexems = [
        "=",
        "<>",
        "<",
        "<=",
        ">=",
        ">",
        "#",
        "a",
        "&%4$",
        "1"
    ]

    validator = Validator()
    assert validator.validate_lexems(lexems) == [
        {"=": "<RELATION>"},
        {"<>": "<RELATION>"},
        {"<": "<RELATION>"},
        {"<=": "<RELATION>"},
        {">=": "<RELATION>"},
        {">": "<RELATION>"},
        {"#": None},
        {"a": "<IDENTIFIER>"},
        {"&%4$": None},
        {"1": "<NUMBER>"},
    ]


def test_keyword():
    """
    Test if it can validate a keyword
    """

    lexems = [
        "program",
        "progra",
        "procedure",
        "procedur",
        "var",
        "va",
        "read",
        "rea",
        "write",
        "writ",
        "begin",
        "begi",
        "end",
        "en",
        "if",
        "i",
        "then",
        "the",
        "else",
        "els",
        "while",
        "whil",
        "do",
        "d"
    ]

    validator = Validator()
    assert validator.validate_lexems(lexems) == [
        {"program": "<KEYWORD_PROGRAM>"},
        {"progra": "<IDENTIFIER>"},
        {"procedure": "<KEYWORD_PROCEDURE>"},
        {"procedur": "<IDENTIFIER>"},
        {"var": "<KEYWORD_VAR>"},
        {"va": "<IDENTIFIER>"},
        {"read": "<KEYWORD_READ>"},
        {"rea": "<IDENTIFIER>"},
        {"write": "<KEYWORD_WRITE>"},
        {"writ": "<IDENTIFIER>"},
        {"begin": "<KEYWORD_BEGIN>"},
        {"begi": "<IDENTIFIER>"},
        {"end": "<KEYWORD_END>"},
        {"en": "<IDENTIFIER>"},
        {"if": "<KEYWORD_IF>"},
        {"i": "<IDENTIFIER>"},
        {"then": "<KEYWORD_THEN>"},
        {"the": "<IDENTIFIER>"},
        {"else": "<KEYWORD_ELSE>"},
        {"els": "<IDENTIFIER>"},
        {"while": "<KEYWORD_WHILE>"},
        {"whil": "<IDENTIFIER>"},
        {"do": "<KEYWORD_DO>"},
        {"d": "<IDENTIFIER>"},
    ]
