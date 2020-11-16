import re


class Validator:
    def __init__(self):
        self.token_types = {
            "<NUMBER>": {"validate": Validator.is_number},
            # "<DIGIT>": {"validate": Validator.is_digit},
            "<OPEN_PARENTHESIS>": {},
            "<CLOSE_PARENTHESIS>": {},
            "<PLUS_SIGN>": {},
            "<MINUS_SIGN>": {},
            "<MULTIPLICATION_SIGN>": {},
            "<DIVISION_SIGN>": {},
            "<EQUALS_SIGN>": {},
            "<MULTI_LINE_COMMENT>": {},
            "<SINGLE_LINE_COMMENT>"
            "<CHARACTER>": {},
            "<IDENTIFIER>": {"validate": Validator.is_identifier},
            "<COMMAND_END>": {"validate": Validator.is_command_end},
            "<SIMPLE_TYPE>": {},
        }
        self.validators = [
            Validator.is_number,
            Validator.is_relation,
            # Validator.is_digit,
            Validator.is_identifier,
            Validator.is_plus_sign,
            Validator.is_minus_sign,
            Validator.is_multiplication_sign,
            Validator.is_division_sign,
            Validator.is_open_parenthesis,
            Validator.is_close_parenthesis,
            Validator.is_simple_type,
            Validator.is_keyword,
            Validator.is_bool_value,
            Validator.is_command_end,
            Validator.is_comma,
            Validator.is_colon,
            Validator.is_dot,
            Validator.is_equals_sign
        ]

    def validate_lexem(self, lexem: str) -> dict:
        try:
            return list(
                filter(
                    lambda x: x[lexem] != None,
                    [validator(lexem) for validator in self.validators],
                )
            ).pop()

        except Exception as inst:
            # print(inst)
            return {lexem: None}

    def validate_lexems(self, lexem_list: list) -> list:
        return [self.validate_lexem(lexem) for lexem in lexem_list]

    @classmethod
    def is_number(cls, value: str) -> dict:
        digit_pattern = re.compile("[0-9][0-9]*")
        check = (
            lambda x: {x: "<NUMBER>"} if digit_pattern.fullmatch(x) else {
                x: None}
        )
        return check(value)

    @classmethod
    def is_plus_sign(cls, value: str) -> dict:
        plus_sign_pattern = re.compile("[+]")
        check = (
            lambda x: {x: "<PLUS_SIGN>"} if plus_sign_pattern.fullmatch(x) else {
                x: None}
        )
        return check(value)

    @classmethod
    def is_minus_sign(cls, value: str) -> dict:
        plus_sign_pattern = re.compile("-")
        check = (
            lambda x: {x: "<MINUS_SIGN>"} if plus_sign_pattern.fullmatch(x) else {
                x: None}
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
        division_sign_pattern = re.compile("div")
        check = (
            lambda x: {x: "<DIVISION_SIGN>"}
            if division_sign_pattern.fullmatch(x)
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_equals_sign(cls, value: str) -> dict:
        equals_sign_pattern = re.compile("\:=")
        check = (
            lambda x: {x: "<EQUALS_SIGN>"}
            if equals_sign_pattern.fullmatch(x)
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_open_parenthesis(cls, value: str) -> dict:
        open_parenthesis_pattern = re.compile("[(]")
        check = (
            lambda x: {x: "<OPEN_PARENTHESIS>"}
            if open_parenthesis_pattern.fullmatch(x)
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_close_parenthesis(cls, value: str) -> dict:
        close_parenthesis_pattern = re.compile("[)]")
        check = (
            lambda x: {x: "<CLOSE_PARENTHESIS>"}
            if close_parenthesis_pattern.fullmatch(x)
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_command_end(cls, value: str) -> dict:
        close_parenthesis_pattern = re.compile("\;")
        check = (
            lambda x: {x: "<COMMAND_END>"}
            if close_parenthesis_pattern.fullmatch(x)
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_comma(cls, value: str) -> dict:
        close_parenthesis_pattern = re.compile("\,")
        check = (
            lambda x: {x: "<COMMA>"}
            if close_parenthesis_pattern.fullmatch(x)
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_colon(cls, value: str) -> dict:
        close_parenthesis_pattern = re.compile("\:")
        check = (
            lambda x: {x: "<COLON>"}
            if close_parenthesis_pattern.fullmatch(x)
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_dot(cls, value: str) -> dict:
        close_parenthesis_pattern = re.compile("\.")
        check = (
            lambda x: {x: "<DOT>"}
            if close_parenthesis_pattern.fullmatch(x)
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_identifier(cls, value: str) -> dict:
        identifier = re.compile("[_|a-z|A-Z]([_|a-z|A-Z]|[0-9])*")
        check = (
            lambda x: {x: "<IDENTIFIER>"}
            if identifier.fullmatch(x)
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_simple_type(cls, value: str) -> dict:
        simple_types = ["int", "real", "boolean"]
        check = (
            lambda x: {x: "<SIMPLE_TYPE>"}
            if value in simple_types
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_relation(cls, value: str) -> dict:
        relations = ["=", "<>", "<", "<=", ">=", ">"]
        check = (
            lambda x: {x: "<RELATION>"}
            if value in relations
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_bool_value(cls, value: str) -> dict:
        booleans = ["true", "false"]
        check = (
            lambda x: {x: "<BOOL_VALUE>"}
            if value in booleans
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_keyword(cls, value: str) -> dict:
        keyword = ["program", "procedure", "var", "read", "write",
                     "begin", "end", "if", "then", "else", "while", "do"]
        check = (
            lambda x: {x: "<KEYWORD_"+x.upper()+">"}
            if value in keyword
            else {x: None}
        )
        return check(value)


if __name__ == "__main__":
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
    print(validator.validate_lexems(lexems))
