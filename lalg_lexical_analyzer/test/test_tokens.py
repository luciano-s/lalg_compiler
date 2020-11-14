from src.tokens import Tokens
import re
import sys
import pytest


def test_split_tokens():
    """
    Test if it can validate a entire string
    """
    inputs = ["3+(2*12.01)", "2/3", "()", ".", "1aaa", "b##+1"]
    tokens = Tokens()
    tks = tokens.split_tokens(inputs)
    new_tks = []
    for t in tks:
        new_tks.append(list(map(lambda x: x[2], t)))

    assert new_tks == [
        [
            {'3': '<NUMBER>'},
            {'+': '<PLUS_SIGN>'},
            {'(': '<OPEN_PARENTHESIS>'},
            {'2': '<NUMBER>'},
            {'*': '<MULTIPLICATION_SIGN>'},
            {'12.01': '<NUMBER>'},
            {')': '<CLOSE_PARENTHESIS>'}
        ], [
            {'2': '<NUMBER>'},
            {'/': '<DIVISION_SIGN>'},
            {'3': '<NUMBER>'}
        ], [
            {'(': '<OPEN_PARENTHESIS>'},
            {')': '<CLOSE_PARENTHESIS>'}
        ], [
            {'.': None}
        ], [
            {'1': '<NUMBER>'},
            {'aaa': None}
        ], [
            {'b##': None},
            {'+': '<PLUS_SIGN>'},
            {'1': '<NUMBER>'},
        ]
    ]
