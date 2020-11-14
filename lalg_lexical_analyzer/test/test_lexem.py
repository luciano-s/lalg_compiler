import re
import pytest

from src.validator import Validator

def test_number_lexem():
    """
    Test if it can validate a number
    """

    lexems = [
        "1.97",
        "1",
        "1.0",
        "37",
        "0.58",
        ".5",
        ".",
        "1.",
    ]

    validator = Validator()
    assert validator.validate_lexems(lexems) == [
        {"1.97": "<NUMBER>"},
        {"1": "<NUMBER>"},
        {"1.0": "<NUMBER>"},
        {"37": "<NUMBER>"},
        {"0.58": "<NUMBER>"},
        {".5": None},
        {".": None},
        {"1.": None},
    ]


def test_sign_lexem():
    """
    Test if it can validate a sign lexem, +, -, * and /
    """
    lexems = ["+", "-", "*", "/", "=", "batata", "#", "@", "!", "_", "$", "%", "(", ")"]
    validator = Validator()
    assert validator.validate_lexems(lexems) == [
        {"+": "<PLUS_SIGN>"},
        {"-": "<MINUS_SIGN>"},
        {"*": "<MULTIPLICATION_SIGN>"},
        {"/": "<DIVISION_SIGN>"},
        {"=": "<EQUALS_SIGN>"},
        {"batata": None},
        {"#": None},
        {"@": None},
        {"!": None},
        {"_": None},
        {"$": None},
        {"%": None},
        {"(": "<OPEN_PARENTHESIS>"},
        {")": "<CLOSE_PARENTHESIS>"},
    ]