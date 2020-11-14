import re


class Validator:
    def __init__(self):
        self.token_types = {
            "<NUMBER>":{"validate":Validator.is_number},
            "<DIGIT>":{"validate":Validator.is_digit},
            "<OPEN_PARENTHESIS>":{},
            "<CLOSE_PARENTHESIS>":{},
            "<PLUS_SIGN>":{},
            "<MINUS_SIGN>":{},
            "<MULTIPLICATION_SIGN>":{},
            "<DIVISION_SIGN>":{},
            "<EQUALS_SIGN>":{},
            "<MULTI_LINE_COMMENT>":{},
            "<SINGLE_LINE_COMMENT>"
            "<CHARACTER>":{},
            "<IDENTIFIER>":{},
            "<SIMPLE_TYPE>":{},
        }
        self.validators = [
            Validator.is_number,
            Validator.is_digit,
            Validator.is_plus_sign,
            Validator.is_minus_sign,
            Validator.is_multiplication_sign,
            Validator.is_division_sign,
            Validator.is_equals_sign,
            Validator.is_open_parenthesis,
            Validator.is_close_parenthesis
        ]

    def validate_lexem(self, lexem: str) -> dict:
        try:
            return list(
                filter(
                    lambda x: x[lexem] != None,
                    [validator(lexem) for validator in self.validators],
                )
            ).pop()

        except:
            return {lexem: None}

    def validate_lexems(self, lexem_list: list) -> list:
        return [self.validate_lexem(lexem) for lexem in lexem_list]

    @classmethod
    def is_digit(cls, value:str)->dict:
        digit_pattern = re.compile("[0-9]")
        check = (
            lambda x: {x: "<DIGIT>"} if digit_pattern.fullmatch(x) else {x: None}
        )
        return check(value)

    @classmethod
    def is_number(cls, value: str) -> dict:

        [cls.is_digit(char) for char in value]
        check = (
            lambda x: {x: "<NUMBER>"} if number_pattern.fullmatch(x) else {x: None}
        )

        return check(value)

    @classmethod
    def is_plus_sign(cls, value: str) -> dict:
        plus_sign_pattern = re.compile("[+]")
        check = (
            lambda x: {x: "<PLUS_SIGN>"} if plus_sign_pattern.fullmatch(x) else {x: None}
        )
        return check(value)

    @classmethod
    def is_minus_sign(cls, value: str) -> dict:
        plus_sign_pattern = re.compile("-")
        check = (
            lambda x: {x: "<MINUS_SIGN>"} if plus_sign_pattern.fullmatch(x) else {x: None}
        )
        return check(value)

    @classmethod
    def is_multiplication_sign(cls, value: str) -> dict:
        multiplication_sign_pattern = re.compile("[*]")
        check = (
            lambda x: {x: "<MULTIPLICATION_SIGN>"}
            if multiplication_sign_pattern.fullmatch(x)
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_division_sign(cls, value: str) -> dict:
        division_sign_pattern = re.compile("/")
        check = (
            lambda x: {x: "<DIVISION_SIGN>"}
            if division_sign_pattern.fullmatch(x)
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_equals_sign(cls, value: str) -> dict:
        equals_sign_pattern = re.compile("=")
        check = (
            lambda x: {x: "<EQUALS_SIGN>"}
            if equals_sign_pattern.fullmatch(x)
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_open_parenthesis(cls, value: str) -> dict:
        open_parenthesis_pattern = re.compile("\(")
        check = (
            lambda x: {x: "<OPEN_PARENTHESIS>"}
            if open_parenthesis_pattern.match(x)
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_close_parenthesis(cls, value: str) -> dict:
        close_parenthesis_pattern = re.compile("\)")
        check = (
            lambda x: {x: "<CLOSE_PARENTHESIS>"}
            if close_parenthesis_pattern.match(x)
            else {x: None}
        )
        return check(value)
