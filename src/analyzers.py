from src.token import Token
from src.tokens import Tokens
from src.validator import Validator


def Convert(a, ini):
    d = {}
    if ini - 1 <= 0:
        ini += 1

    for i in range(ini - 1, len(a)):
        d[i] = a[i]

    return d


class Analyzers:
    symbol_table = dict()
    @staticmethod
    def lexical_analyzer(expression):
        expressions = list(filter(None, expression.replace("\r", "").split("\n")))
        tokens = Tokens()
        validated_lexems = []
        line = 1
        for exp in expressions:
            validated_lexems.extend(
                list(
                    map(
                        lambda d, ci, ce: (
                            list(d.keys()).pop(),
                            list(d.values()).pop(),
                            "Yes" if list(d.values()).pop() is not None else "No",
                            line,
                            str(ci) + "-" + str(ce),
                        ),
                        *zip(*tokens.split_token(exp))
                    )
                )
            )
            line += 1
        return validated_lexems

    @staticmethod
    def is_identifier_list(tk_list: list, i: int):
        initial = i
        errors = []
        tk_atual = Convert(tk_list, i)
        if tk_list[i][1] == "<IDENTIFIER>":
            i += 1
            while i + 1 < len(tk_list):
                if tk_list[i][1] == "<COMMA>" and tk_list[i + 1][1] == "<IDENTIFIER>":
                    i += 2
                else:
                    break
            return Token(tk_list[initial:i], "<IDENTIFIER_LIST>", (initial, i))

        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_variable_declarator(tk_list, i):
        initial = i
        errors = []
        tk_atual = Convert(tk_list, i)
        # print(tk_list[i][1])
        # input()
        if tk_list[i][1] == "<SIMPLE_TYPE>":
            is_ilist = Analyzers.is_identifier_list(tk_list, i + 1)
            i = is_ilist.col[1]
            if is_ilist.token == "<IDENTIFIER_LIST>":
                return Token(
                    tk_list[initial:i], "<VARIABLE_DECLARATION>", (initial, i)
                ), errors
        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_variable_declaration_part(tk_list: list, i: int):
        initial = i
        errors = []
        tk_atual = Convert(tk_list, i)
        errors = []
        first, e = Analyzers.is_variable_declarator(tk_list, i)
        # print(f"first-lexem{first.lexem}")
        # input()
        if first.token == "<VARIABLE_DECLARATION>":
            i = first.col[1]
            while i < len(tk_list) and i + 1 < len(tk_list):
                next = Analyzers.is_variable_declarator(tk_list, i + 1)
                # print(next.token)
                # input()
                if (
                        tk_list[i][1] == "<COMMAND_END>"
                        and next.token == "<VARIABLE_DECLARATION>"
                ):
                    i = next.col[1]
                else:
                    break
            print(tk_list[i][1])
            if i < len(tk_list) and tk_list[i][1] == "<COMMAND_END>":
                return Token(
                    tk_list[initial:i], "<VARIABLE_DECLARATION_PART>", (initial, i + 1)
                ), errors

        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_program(tk_list: list, i: int):
        Analyzers.symbol_table["global"] = []
        initial = i
        errors = []
        l = len(tk_list)
        errors = []
        tk_atual = Convert(tk_list, i)
        if i < l and tk_list[i][1] == "<KEYWORD_PROGRAM>":
            i += 1
        else:
            errors.append({"message": "program expected	", "line": "0", "col": "0"})
            i = Analyzers.error(i + 1, tk_list, ["<IDENTIFIER>"])

        if i < l and tk_list[i][1] == "<IDENTIFIER>":
            i += 1
        else:
            errors.append({"message": "program identifier expected", "line": "0", "col": "0"})
            i = Analyzers.error(i, tk_list, ["<COMMAND_END>"], limit=2)

        if i < l and tk_list[i][1] == "<COMMAND_END>":
            i += 1
        else:
            errors.append({"message": "';' expected", "line": "0", "col": "0"})
            i = Analyzers.error(
                i, tk_list, ["<SIMPLE_TYPE>", "<KEYWORD_VAR>", "<KEYWORD_PROCEDURE>", "<KEYWORD_BEGIN>"], limit=2)

        if i < l:
            res, e = Analyzers.is_bloc(tk_list, i)
            errors.extend(e)
            i = res.col[1] + 1  # get the end of the block plus 1
            if res.token == "<BLOC>":
                pass

        if i < l and tk_list[i][1] == "<DOT>":
            i += 1
        else:
            errors.append({"message": "'.' expected on the end of program", "line": "0", "col": "0"})
            Analyzers.error(i + 1, tk_list, [])

        return Token(tk_list[initial:i], "<PROGRAM>", (initial, i + 1)), errors

        # return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_bloc(tk_list: list, i: int):
        initial = i
        errors = []
        tk_atual = Convert(tk_list, i)
        res, e = Analyzers.is_variable_declaration_part(tk_list, i)
        if res.token == "<VARIABLE_DECLARATION_PART>":
            i = res.col[1]
            errors.extend(e)

        res, e = Analyzers.is_subroutine_declaration_part(tk_list, i)
        if res.token == "<SUBROUTINE_DECLARATION_PART>":
            i = res.col[1]
            errors.extend(e)

        res, e = Analyzers.is_composite_command(tk_list, i)
        if res.token == "<COMPOSITE_COMMAND>":
            i = res.col[1]
            errors.extend(e)
            return Token(tk_list[initial:i], "<BLOC>", (initial, i)), errors

        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_composite_command(tk_list: list, i: int):
        initial = i
        errors = []
        l = len(tk_list)
        tk_atual = Convert(tk_list, i)

        if i < l and tk_list[i][1] == "<KEYWORD_BEGIN>":
            i += 1
        else:
            errors.append({"message": "begin expected", "line": "0", "col": "0"})
            i = Analyzers.error(
                i + 1, tk_list,
                ["<IDENTIFIER>", "<KEYWORD_BEGIN>", "<KEYWORD_IF>", "<KEYWORD_PROCEDURE>", "<KEYWORD_WHILE>"], limit=1)

        if i < l:
            res, e = Analyzers.is_command(tk_list, i)
            if res.token == "<COMMAND>":
                i = res.col[1]
                errors.extend(e)
                while i + 1 < l:
                    res, e = Analyzers.is_command(tk_list, i + 1)
                    if i < l and tk_list[i][1] == "<COMMAND_END>" and res.token == "<COMMAND>":
                        i = res.col[1]
                        errors.extend(e)
                    else:
                        break

                if i < l and tk_list[i][1] == "<KEYWORD_END>":
                    return Token(tk_list[initial:i], "<COMPOSITE_COMMAND>", (initial, i)), errors
                else:
                    errors.append({"message": "end expected", "line": "0", "col": "0"})
                    i = Analyzers.error(
                        i + 1, tk_list, ["<KEYWORD_END>"], )

        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_command(tk_list: list, i: int):
        initial = i
        errors = []
        tk_atual = Convert(tk_list, i)

        conditions = {
            "<ASSIGNMENT>": Analyzers.is_assignment,
            "<PROCEDURE_CALL>": Analyzers.is_procedure_call,
            "<COMPOSITE_COMMAND>": Analyzers.is_composite_command,
            "<CONDITIONAL_COMMAND_1>": Analyzers.is_conditional_command_1,
            "<REPETITIVE_COMMAND_1>": Analyzers.is_repetitive_command
        }

        for token_type in conditions:
            res, e = conditions[token_type](tk_list, i)
            if res.token == token_type:
                i = res.col[1]
                errors.extend(e)
                if token_type == "<COMPOSITE_COMMAND>":
                    i += 1
                return Token(tk_list[initial:i], "<COMMAND>", (initial, i)), errors

        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_assignment(tk_list: list, i: int):
        initial = i
        errors = []
        l = len(tk_list)
        has_equal = False
        tk_atual = Convert(tk_list, i)
        res, e = Analyzers.is_variable(tk_list, i)
        if res.token == "<VARIABLE>":
            errors.extend(e)
            if res.col[1] < l and tk_list[res.col[1]][1] == "<EQUALS_SIGN>":
                i = res.col[1] + 1
                has_equal = True
            elif res.col[1] < l and tk_list[res.col[1]][0] == "=":
                errors.append({"message": "':=' expected", "line": "0", "col": "0"})
                i = Analyzers.error(res.col[1] + 1, tk_list,
                                    ["<PLUS_SIGN>", "<MINUS_SIGN>", "<OPEN_PARENTHESIS>",
                                     "<KEYWORD_NOT>", "<IDENTIFIER>", "<NUMBER>"], limit=1)
            else:
                return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

            res, e = Analyzers.is_expression(tk_list, i)
            # AQUI NUMBER 125
            if res.token == "<EXPRESSION>":
                i = res.col[1]
                errors.extend(e)
            elif has_equal:
                errors.append({"message": "expression expected before ':='", "line": "0", "col": "0"})
                i = Analyzers.error(i, tk_list,
                                    ["<COMMA>", "<CLOSE_PARENTHESIS>", "<KEYWORD_THEN>",
                                     "<KEYWORD_DO>", "<KEYWORD_END>", "<KEYWORD_ELSE>"], limit=1)
            else:
                return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

            return Token(tk_list[initial:i], "<ASSIGNMENT>", (initial, i)), errors

        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_variable(tk_list: list, i: int):
        initial = i
        errors = []
        l = len(tk_list)
        tk_atual = Convert(tk_list, i)
        if i < l and tk_list[i][1] == "<IDENTIFIER>":
            # res, e = Analyzers.is_expression(tk_list, i + 1)
            # if res.token == "<EXPRESSION>":
            #     i = res.col[1]
            return Token(tk_list[initial:i], "<VARIABLE>", (initial, i + 1)), errors

        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_expression(tk_list: list, i: int):
        initial = i
        errors = []
        l = len(tk_list)
        tk_atual = Convert(tk_list, i)
        res, e = Analyzers.is_simple_expression(tk_list, i)
        if i < l and res.token == "<SIMPLE_EXPRESSION>":
            i = res.col[1]
            if i < l and tk_list[i][1] == "<RELATION>":
                res, e = Analyzers.is_simple_expression(tk_list, i + 1)
                if res.token == "<SIMPLE_EXPRESSION>":
                    i = res.col[1]
                else:
                    return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

            return Token(tk_list[initial:i], "<EXPRESSION>", (initial, i)), errors

        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_simple_expression(tk_list: list, i: int):
        initial = i
        errors = []
        l = len(tk_list)
        tk_atual = Convert(tk_list, i)
        has_sign = False
        if (
                i < l and
                (tk_list[i][1] == "<PLUS_SIGN>"
                 or tk_list[i][1] == "<MINUS_SIGN>")
        ):
            has_sign = True

        res, e = Analyzers.is_therm(tk_list, i + 1 if has_sign else i)
        if res.token == "<THERM>":
            i = res.col[1]
            errors.extend(e)
            while i + 1 < len(tk_list):
                res, e = Analyzers.is_therm(tk_list, i + 1)
                if (
                        tk_list[i][1] == "<PLUS_SIGN>"
                        or tk_list[i][1] == "<MINUS_SIGN>"
                        or tk_list[i][1] == "<KEYWORD_OR>"
                ) and res.token == "<THERM>":
                    i = res.col[1]
                    errors.extend(e)
                else:
                    break
            return Token(tk_list[initial:i], "<SIMPLE_EXPRESSION>", (initial, i)), errors

        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_therm(tk_list: list, i: int):
        initial = i
        errors = []
        l = len(tk_list)
        tk_atual = Convert(tk_list, i)
        res, e = Analyzers.is_factor(tk_list, i)
        if res.token == "<FACTOR>":
            i = res.col[1]
            errors.extend(e)
            while i + 1 < len(tk_list):
                res, e = Analyzers.is_factor(tk_list, i + 1)
                if i < l and tk_list[i][1] in [
                    "<MULTIPLICATION_SIGN>",
                    "<DIVISION_SIGN>",
                    "<KEYWORD_AND>"
                ] and res.token == "<FACTOR>":
                    i = res.col[1]
                    errors.extend(e)
                else:
                    break

            return Token(tk_list[initial:i], "<THERM>", (initial, i)), errors

        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_factor(tk_list: list, i: int):
        follow_factor = ["<MULTIPLICATION_SIGN>", "<KEYWORD_DIV>", "<KEYWORD_AND>", "<PLUS_SIGN>", "<MINUS_SIGN>",
                         "<KEYWORD_OR>", "<RELATION>", "<CLOSE_PARENTHESIS>", "<COMMA>", "<CLOSE_PARENTHESIS>",
                         "<KEYWORD_THEN>", "<KEYWORD_DO>", "<KEYWORD_END>", "<KEYWORD_ELSE>"]
        wrong_therms = 4
        initial = i
        errors = []
        l = len(tk_list)
        tk_atual = Convert(tk_list, i)
        has_factor = False
        while True:
            if i >= l:
                break

            if tk_list[i][1] == "<IDENTIFIER>":
                i += 1
                has_factor = True
                break

            if tk_list[i][1] == "<NUMBER>":  # TODO: arrumar, pois até lexemas tem col[ini, end]
                i += 1
                has_factor = True
                break

            if tk_list[i][1] == "<BOOL_VALUE>":
                i += 1
                has_factor = True
                break

            if tk_list[i][1] == "<OPEN_PARENTHESIS>":
                res, e = Analyzers.is_expression(tk_list, i + 1)
                if res.token == "<EXPRESSION>":
                    if tk_list[res.col[1]][1] == "<CLOSE_PARENTHESIS>":
                        i = res.col[1] + 1
                        has_factor = True
                        break
                    else:
                        errors.append({"message": "')' expected", "line": "0", "col": "0"})
                        i = Analyzers.error(i, tk_list, follow_factor)

            if tk_list[i][1] == "<KEYWORD_NOT>":
                res, e = Analyzers.is_factor(tk_list, i + 1)
                if res.token == "<FACTOR>":
                    i = res.col[1]
                    has_factor = True
                    errors.extend(e)
                else:
                    errors.append({"message": "expected factor before not", "line": "0", "col": "0"})
                    i = Analyzers.error(i, tk_list, follow_factor)
                break

            errors.append({"message": f"unexpected factor '{tk_list[i][0]}'", "line": "0", "col": "0"})
            i += 1

            wrong_therms -= 1
            if wrong_therms <= 0:
                break

        if has_factor:
            return Token(tk_list[initial:i], "<FACTOR>", (initial, i)), errors

        return Token(tk_list[initial: i], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_procedure_call(tk_list: list, i: int):
        initial = i
        errors = []
        l = len(tk_list)
        tk_atual = Convert(tk_list, i)
        if i < l and tk_list[i][1] == "<IDENTIFIER>":
            i += 1
            res, e = Analyzers.is_expression_list(tk_list, i + 1)
            if (
                    tk_list[i][1] == "<OPEN_PARENTHESIS>"
                    and res.token == "<EXPRESSION_LIST>"
                    and tk_list[res.col[1] + 1][1] == "<CLOSE_PARENTHESIS>"
            ):
                i += res.col[1] + 1

                return Token(tk_list[initial:i], "<PROCEDURE_CALL>", (initial, i + 1)), errors
        return Token(tk_list[initial: i], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_expression_list(tk_list: list, i: int):
        initial = i
        errors = []
        tk_atual = Convert(tk_list, i)
        res, e = Analyzers.is_expression(tk_list, i)
        if res.token == "<EXPRESSION>":
            i += res.col[1] + 1  # TODO: verificar finalização de indice
            while i < len(tk_list) and i + 1 < len(tk_list):
                res, e = Analyzers.is_expression(tk_list, i + 1)
                if tk_list[i][1] == "<COMMA>" and res.token == "<EXPRESSION>":
                    i += res.col[1] + 2
                else:
                    break

            return Token(tk_list[initial:i], "<IDENTIFIER_LIST>", (initial, i)), errors

        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_conditional_command_1(tk_list: list, i: int):
        initial = i
        errors = []
        l = len(tk_list)
        tk_atual = Convert(tk_list, i)
        if i < l and tk_list[i][1] == "<KEYWORD_IF>":
            i += 1
        else:
            errors.append({"message": "if expected", "line": "0", "col": "0"})
            i = Analyzers.error(
                i + 1, tk_list,
                ["<PLUS_SIGN>", "<MINUS_SIGN>", "<OPEN_PARENTHESIS>", "<KEYWORD_NOT>", "<IDENTIFIER>", "<NUMBER>"],
                limit=1)

        res, e = Analyzers.is_expression(tk_list, i)
        if res.token == "<EXPRESSION>":
            i = res.col[1]
            # a=b
            if i < l and tk_list[i][1] == "<KEYWORD_THEN>":
                i += 1
            else:
                errors.append({"message": "then expected", "line": "0", "col": "0"})
                if i + 1 < l and tk_list[i][1] == "<IDENTIFIER>" and tk_list[i + 1][1] == "<EQUAL_SIGN>":
                    i -= 1
                i = Analyzers.error(
                    i + 1, tk_list,
                    ["<PLUS_SIGN>", "<MINUS_SIGN>", "<OPEN_PARENTHESIS>", "<KEYWORD_NOT>", "<IDENTIFIER>", "<NUMBER>"],
                    limit=1)

                # in case of missing then follow by assigment

            res, e = Analyzers.is_command(tk_list, i)
            if res.token == "<COMMAND>":
                i = res.col[1]
                if i < l and tk_list[i][1] == "<KEYWORD_ELSE>":
                    res, e = Analyzers.is_command(tk_list, i + 1)
                    if res.token == "<COMMAND>":
                        i = res.col[1]
                return Token(tk_list[initial: i], "<CONDITIONAL_COMMAND_1>", (initial, i)), errors

        # COLOCAR AQUI O FOLLOW
        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_repetitive_command(tk_list: list, i: int):
        # verificar se dá pra analisar erro com o while
        initial = i
        errors = []
        l = len(tk_list)
        tk_atual = Convert(tk_list, i)
        if i < l and tk_list[i][1] == "<KEYWORD_WHILE>":
            res, e = Analyzers.is_expression(tk_list, i + 1)
            if res.token == "<EXPRESSION>":
                i = res.col[1]
                errors.extend(e)
                if tk_list[i][1] == "<KEYWORD_DO>":
                    i += 1
                else:
                    errors.append({"message": "'do' expected", "line": "0", "col": "0"})
                    i = Analyzers.error(i + 1, tk_list,
                                        ["<IDENTIFIER>", "<KEYWORD_IF>", "<KEYWORD_PROCEDURE>", "<KEYWORD_WHILE>"],
                                        limit=1)
                res, e = Analyzers.is_command(tk_list, i)
                if res.token == "<COMMAND>":
                    i = res.col[1]
                    return Token(tk_list[initial: i], "<REPETITIVE_COMMAND_1>", (initial, i)), errors

            # ACHO QUE AQUI QUE FAREMOS A BUSCA DO FOLLOW
            i = Analyzers.error(i, tk_list,
                                ["<KEYWORD_END>", "<COMMAND_END>", "<KEYWORD_ELSE>"])
        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_formal_parameter_section(tk_list, i):
        initial = i
        errors = []
        tk_atual = Convert(tk_list, i)
        if tk_list[i][1] == "<KEYWORD_VAR>":
            res, e = Analyzers.is_identifier_list(tk_list, i + 1)
            if res.token == "<IDENTIFIER_LIST>":
                i = res.col[1]
                if tk_list[i][1] == "<COLON>":
                    i += 1
                    if tk_list[i][1] == "<SIMPLE_TYPE>":
                        i += 1
                        return Token(tk_list[initial: i], "<FORMAL_PARAMETER_SECTION>", (initial, i))
        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_formal_parameters(tk_list, i):
        initial = i
        errors = []
        tk_atual = Convert(tk_list, i)
        if tk_list[i][1] == "<OPEN_PARENTHESIS>":
            res, e = Analyzers.is_formal_parameter_section(tk_list, i + 1)
            if res.token == "<FORMAL_PARAMETER_SECTION>":
                i = res.col[1]
                while i < len(tk_list) and i + 1 < len(tk_list):
                    res, e = Analyzers.is_formal_parameter_section(tk_list, i + 1)
                    if tk_list[i][1] == "<COMMAND_END>" and res.token == "<FORMAL_PARAMETERS>":
                        i += res.col[1] + 2
                    else:
                        break

                if tk_list[i][1] == "<CLOSE_PARENTHESIS>":
                    return Token(tk_list[initial:i], "<FORMAL_PARAMETERS>", (initial, i)), errors

        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_procedure_declaration(tk_list, i):
        initial = i
        errors = []
        tk_atual = Convert(tk_list, i)
        if tk_list[i][1] == "<KEYWORD_PROCEDURE>":
            if tk_list[i + 1][1] == "<IDENTIFIER>":
                res, e = Analyzers.is_formal_parameters(tk_list, i + 2)
                if res.token == "<FORMAL_PARAMETERS>" and tk_list[res.col[1] + 1][1] == "<COMMAND_END>":
                    i = res.col[1] + 1
                    res, e = Analyzers.is_bloc(tk_list, i + 1)
                    if res.token == "<BLOC>":
                        i = res.col[1]
                        return Token(tk_list[initial:i], "<PROCEDURE_DECLARATION>", (initial, i)), errors
                elif tk_list[i + 1][1] == "<COMMAND_END>":
                    i += 1
                    res, e = Analyzers.is_bloc(tk_list, i + 1)
                    if res.token == "<BLOC>":
                        i = res.col[1] + 1
                        return Token(tk_list[initial:i], "<PROCEDURE_DECLARATION>", (initial, i)), errors

        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_subroutine_declaration_part(tk_list: list, i: int):
        initial = i
        errors = []
        tk_atual = Convert(tk_list, i)
        res, e = Analyzers.is_procedure_declaration(tk_list, i)
        if (
                res.col[1] + 1 < len(tk_list)
                and tk_list[res.col[1] + 1][1] == "<COMMAND_END>"
                and res.token == "<PROCEDURE_DECLARATION>"
        ):
            i = res.col[1] + 2
            while i + 1 < len(tk_list):
                res, e = Analyzers.is_procedure_declaration(tk_list, i)
                if tk_list[i + 1][1] == "<COMMAND_END>" and res.token == "<PROCEDURE_DECLARATION>":
                    i += res.col[1] + 2
                else:
                    break
            return Token(tk_list[initial:i], "<SUBROUTINE_DECLARATION_PART>", (initial, i)), errors

        return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def error(i: int, tk_list: list, sync_simbols: list, limit=7):
        cont = 0
        initial = i
        while cont < limit and i < len(tk_list) and tk_list[i][1] not in sync_simbols:
            i += 1
            cont += 1

        if cont >= limit:
            i = initial

        return i

    @staticmethod
    def syntax_analyzer_for_variable(validated_lexems):
        i = 0
        new_tokens = []
        while i < len(validated_lexems):

            res, e = Analyzers.is_variable_declaration_part(tk_list=validated_lexems, i=i)
            print(res)
            print(res.lexem)
            if res.token != "<ERROR>":
                i = res.col[1]
            else:
                return [*new_tokens, res]
            new_tokens.append(res)
            print(*new_tokens)
        return new_tokens

    @staticmethod
    def syntax_analyzer(validated_lexems):
        i = 0
        new_tokens = []
        # res, e = Analyzers.is_bloc(tk_list=validated_lexems, i=i, errors=errors)
        # res, errors = Analyzers.is_assignment(tk_list=validated_lexems, i=i)
        # res, errors = Analyzers.is_assignment(tk_list=validated_lexems, i=i)
        # res, errors = Analyzers.is_factor(tk_list=validated_lexems, i=i)
        res, errors = Analyzers.is_simple_expression(tk_list=validated_lexems, i=i)
        # print(res)
        # print(res.lexem)
        # if res.token != "<ERROR>":, errors
        #     i = res.col[1]
        # else:
        #     return [*new_tokens, res]
        new_tokens.append(res)
        # print(*new_tokens)

        return new_tokens, errors
