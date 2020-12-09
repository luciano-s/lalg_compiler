import re
from src.token import Token


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
            "<SINGLE_LINE_COMMENT>" "<CHARACTER>": {},
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
            Validator.is_equals_sign,
            Validator.is_simple_type,
        ]
        self.token_validators = [
            Validator.is_identifier_list,
            Validator.is_var_declaration,
            Validator.is_simple_type,
            Validator.is_part_var_declaration,
            Validator.is_formal_parameter_section,
            Validator.is_formal_parameters,
            Validator.is_procedure_declaration,
            Validator.is_subroutines_declaration_part,
            Validator.is_program,
            Validator.is_factor,
            Validator.is_therm,
            Validator.is_simple_expression,
            Validator.is_expression,
            Validator.is_expression_list,
            # Validator.is_variable,
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

    def validate_token(self, tk_list: list) -> Token:
        # print(tk_list)
        try:
            return list(
                filter(
                    lambda x: x.token != None,
                    [validator(tk_list) for validator in self.token_validators],
                )
            ).pop()
        except Exception as inst:
            # print(inst)
            return Token("", None, None)

    def validate_lexems(self, lexem_list: list) -> list:
        return [self.validate_lexem(lexem) for lexem in lexem_list]

    @classmethod
    def is_number(cls, value: str) -> dict:
        digit_pattern = re.compile("[0-9][0-9]*")
        check = lambda x: {x: "<NUMBER>"} if digit_pattern.fullmatch(x) else {x: None}
        return check(value)

    @classmethod
    def is_plus_sign(cls, value: str) -> dict:
        plus_sign_pattern = re.compile("[+]")
        check = (
            lambda x: {x: "<PLUS_SIGN>"}
            if plus_sign_pattern.fullmatch(x)
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_minus_sign(cls, value: str) -> dict:
        plus_sign_pattern = re.compile("-")
        check = (
            lambda x: {x: "<MINUS_SIGN>"}
            if plus_sign_pattern.fullmatch(x)
            else {x: None}
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
        check = lambda x: {x: "<IDENTIFIER>"} if identifier.fullmatch(x) else {x: None}
        return check(value)

    @classmethod
    def is_simple_type(cls, value: str) -> dict:
        simple_types = ["int", "real", "boolean"]
        check = lambda x: {x: "<SIMPLE_TYPE>"} if value in simple_types else {x: None}
        return check(value)

    @classmethod
    def is_relation(cls, value: str) -> dict:
        relations = ["=", "<>", "<", "<=", ">=", ">"]
        check = lambda x: {x: "<RELATION>"} if value in relations else {x: None}
        return check(value)

    @classmethod
    def is_bool_value(cls, value: str) -> dict:
        booleans = ["true", "false"]
        check = lambda x: {x: "<BOOL_VALUE>"} if value in booleans else {x: None}
        return check(value)

    @classmethod
    def is_keyword(cls, value: str) -> dict:
        keyword = [
            "program",
            "procedure",
            "var",
            "read",
            "write",
            "begin",
            "end",
            "if",
            "then",
            "else",
            "while",
            "do",
            "and",
            "or",
        ]
        check = (
            lambda x: {x: "<KEYWORD_" + x.upper() + ">"}
            if value in keyword
            else {x: None}
        )
        return check(value)

    @classmethod
    def is_identifier_list(cls, tk_list: list) -> dict:
        checked = False
        i = 0
        while True:
            if i < len(tk_list):
                # print(i, i+1)
                if tk_list[i] == "<IDENTIFIER>":
                    checked = True
                else:
                    break
                if i + 1 < len(tk_list) and tk_list[i + 1] == "<COMMA>":
                    checked = False
                    i += 1
            else:
                break
            i += 1
        if checked:
            return Token(tk_list, "<IDENTIFIER_LIST>", None)
        else:
            return Token("", None, None)

    @classmethod
    def is_var_declaration(cls, tk_list: list) -> dict:
        if (
            tk_list[0] == "<SIMPLE_TYPE>"
            and tk_list[-1] == "<COMMAND_END>"
            and cls.is_identifier_list(tk_list[1:-1])
        ):
            return Token("", "<VAR_DECLARATION>", None)
        return Token("", None, None)

    @classmethod
    def is_part_var_declaration(cls, tk_list: list) -> dict:
        checked = False
        i = 0
        while True:
            if i < len(tk_list):
                if tk_list[i] == "<VAR_DECLARATION>":
                    checked = True
                else:
                    break
                if i + 1 < len(tk_list) and tk_list[i + 1] == "<COMMAND_END>":
                    checked = False
                    i += 1
            else:
                break
            i += 1
        if checked:
            return Token(tk_list, "<VAR_DECLARATION_PART>", None)
        else:
            return Token("", None, None)

    @classmethod
    def is_formal_parameter_section(cls, tk_list: list) -> dict:
        i = 1 if tk_list[0] == "<KEYWORD_VAR>" else 0
        if (
            len(tk_list) > 2
            and tk_list[i] == "<IDENTIFIER_LIST>"
            and tk_list[-2] == "<COLON>"
            and tk_list[-1] == "<SIMPLE_TYPE>"
        ):
            return Token("", "<FORMAL_PARAMETERS_SECTION>", None)
        return Token("", None, None)

    @classmethod
    def is_formal_parameters(cls, tk_list: list) -> dict:
        if (
            len(tk_list) > 2
            and tk_list[0] == "<OPEN_PARENTHESIS>"
            and tk_list[-1] == "<CLOSE_PARENTHESIS>"
        ):
            checked = False
            i = 1
            while True:
                if i < len(tk_list) - 1:
                    print(tk_list[i], tk_list[i + 1])
                    if tk_list[i] == "<FORMAL_PARAMETERS_SECTION>":
                        checked = True
                    else:
                        break
                    if i + 1 < len(tk_list) - 1:
                        checked = False
                        if tk_list[i + 1] != "<COMMAND_END>":
                            break
                else:
                    break
                i += 2
            if checked:
                return Token("", "<FORMAL_PARAMETERS>", None)

        return Token("", None, None)

    @classmethod
    def is_procedure_declaration(cls, tk_list: list) -> dict:
        if (
            3 < len(tk_list) <= 5
            and tk_list[0] == "<KEYWORD_PROCEDURE>"
            and tk_list[1] == "<IDENTIFIER>"
            and tk_list[-2] == "<COMMAND_END>"
            and tk_list[-1] == "<BLOC>"
        ):
            if len(tk_list) == 5 and tk_list[2] != "<FORMAL_PARAMETERS>":
                return Token("", None, None)
            return Token("", "<PROCEDURE_DECLARATION>", None)
        return Token("", None, None)

    @classmethod
    def is_subroutines_declaration_part(cls, tk_list: list) -> dict:
        i = 0
        checked = True
        while True:
            if i < len(tk_list):
                if (
                    tk_list[i] != "<PROCEDURE_DECLARATION>"
                    or tk_list[i + 1] != "<COMMAND_END>"
                ):
                    checked = False
            else:
                break
            i += 2
        if checked:
            return Token(tk_list, "<SUBROUTINES_DECLARATION_PART>", None)
        else:
            return Token("", None, None)

    @classmethod
    def is_program(cls, tk_list: list) -> Token:
        if (
            len(tk_list) == 5
            and tk_list[0] == "<KEYWORD_PROGRAM>"
            and tk_list[1] == "<IDENTIFIER>"
            and tk_list[2] == "<COMMAND_END>"
            and tk_list[3] == "<BLOC>"
            and tk_list[4] == "<DOT>"
        ):
            return Token("", "<PROGRAM>", None)
        return Token("", None, None)

    @classmethod
    def is_factor(cls, tk_list: list) -> Token:

        if (
            tk_list == ["<VARIABLE>"]
            or tk_list == ["<NUMBER>"]
            or tk_list == ["<OPEN_PARENTHESIS>", "<EXPRESSION>", "<CLOSE_PARENTHESIS>"]
            or tk_list == ["<KEYWORD_NOT>", "<FACTOR>"]
        ):
            return Token("", "<FACTOR>", None)
        return Token("", None, None)

    @classmethod
    def is_therm(cls, tk_list: list) -> Token:
        len_tk_list = len(tk_list)
        if len_tk_list >= 1 and tk_list[0] == "<FACTOR>":
            i = 1
            checked = True
            while True:
                if i < len_tk_list:

                    if not (
                        tk_list[i]
                        in ["<MULTIPLICATION_SIGN>", "<DIVISION_SIGN>", "<KEYWORD_AND>"]
                        and (i + 1 < len_tk_list and tk_list[i + 1] == "<FACTOR>")
                    ):
                        checked = False
                        break
                else:
                    break
                i += 2
            if checked:
                return Token(tk_list, "<THERM>", None)

        return Token("", None, None)

    @classmethod
    def is_simple_expression(cls, tk_list: list) -> Token:
        len_tk_list = len(tk_list)

        if len_tk_list >= 1 and tk_list[0] in [
            "<THERM>",
            "<PLUS_SIGN>",
            "<MINUS_SIGN>",
        ]:
            i = 1
            if tk_list[0] != "<THERM>":
                i += 1
                if tk_list[1] != "<THERM>":
                    return Token("", None, None)

            checked = True
            while True:
                if i < len_tk_list:

                    if not (
                        tk_list[i] in ["<PLUS_SIGN>", "<MINUS_SIGN>", "<KEYWORD_OR>"]
                        and (i + 1 < len_tk_list and tk_list[i + 1] == "<THERM>")
                    ):
                        checked = False
                        break
                else:
                    break
                i += 2

            if checked:
                return Token(tk_list, "<SIMPLE_EXPRESSION>", None)

        return Token("", None, None)

    @classmethod
    def is_expression(cls, tk_list: list) -> Token:
        len_tk_list = len(tk_list)

        if len_tk_list >= 1 and tk_list[0] == "<SIMPLE_EXPRESSION>":
            i = 1
            checked = True
            while i < len_tk_list:

                if not (
                    tk_list[i] == "<RELATION>"
                    and (
                        i + 1 < len_tk_list and tk_list[i + 1] == "<SIMPLE_EXPRESSION>"
                    )
                ):
                    checked = False
                    break

                i += 2

            if checked:
                return Token(tk_list, "<SIMPLE_EXPRESSION>", None)

        return Token("", None, None)

    @classmethod
    def is_expression_list(cls, tk_list: list):
        checked = False
        i = 0
        while True:
            if i < len(tk_list):
                # print(i, i+1)
                if tk_list[i] == "<EXPRESSION>":
                    checked = True
                else:
                    break
                if i + 1 < len(tk_list) and tk_list[i + 1] == "<COMMA>":
                    checked = False
                    i += 1
            else:
                break
            i += 1
        if checked:
            return Token(tk_list, "<EXPRESSION_LIST>", None)
        else:
            return Token("", None, None)

    @classmethod
    def is_variable(cls, tk_list: list) -> Token:
        if tk_list == ["<IDENTIFIER>"] or tk_list == ["<IDENTIFIER>", "<EXPRESSION>"]:
            return Token(tk_list, "<VARIABLE>", None)
        return Token(tk_list, None, None)






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
