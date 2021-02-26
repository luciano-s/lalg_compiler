from src.token_ import Token_
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

        expressions = expression.replace("\r", "").split("\n")
        tokens = Tokens()
        validated_lexems = []
        line = 0
        for exp in expressions:
            line += 1
            res = tokens.split_token(exp)
            if len(res) == 0:
                continue

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
                        *zip(*res)
                    )
                )
            )
        return validated_lexems

    @staticmethod
    def is_identifier_list(tk_list: list, i: int):
        follow_identifier_list = ["<COLON>", "<SIMPLE_TYPE>", "<COMMAND_END>"]
        initial = i
        errors = []
        l = len(tk_list)
        if i < l and tk_list[i][1] == "<IDENTIFIER>":
            i +=1
            while i < l:  # verifica se tem repeticoes da parte opcional da {, expressao}
                has_comma = False
                current_i = i
                optional_errors = []
                while True:
                    if current_i < l and tk_list[current_i][1] == "<COMMA>":
                        has_comma = True
                        current_i += 1
                        break
                    elif current_i < l:
                        saved_i = current_i
                        current_i = Analyzers.error(current_i, tk_list,
                                                    [*follow_identifier_list, "<IDENTIFIER>", "<COMMA>"], limit=2)
                        if current_i == saved_i:
                            break
                        str_error = ""
                        for err_index in range(saved_i, current_i):
                            str_error += tk_list[err_index][0]
                        optional_errors.append({"message": f"unexpected '{str_error}' before ','", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})
                    else:
                        pass

                if i < l and tk_list[current_i][1] == "<IDENTIFIER>":
                    if not has_comma:
                        errors.append({"message": f"',' expected", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})
                    else:
                        errors.extend(optional_errors)
                    i = current_i + 1
                elif has_comma:  # sincronização pois teve virgula, mas não identificador
                    errors.extend(optional_errors)
                    if i < l:
                        errors.append({"message": f"missing identifier after ','", "line": tk_list[current_i][3], "col": tk_list[current_i][4].split("-")[0]})
                    i = Analyzers.error(current_i, tk_list, follow_identifier_list)
                else:  # nao tenho virgula nem identificador, então não tem mais parte opcional
                    break

            return Token_(tk_list[initial:i], "<IDENTIFIER_LIST>", (initial, i)), errors

        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_variable_declarator(tk_list, i):
        initial = i
        errors = []
        l = len(tk_list)
        if i < l and tk_list[i][1] == "<SIMPLE_TYPE>":
            is_ilist, e = Analyzers.is_identifier_list(tk_list, i + 1)
            if is_ilist.token == "<IDENTIFIER_LIST>":
                i = is_ilist.col[1]
                errors.extend(e)
                return Token_(
                    tk_list[initial:i], "<VARIABLE_DECLARATION>", (initial, i)
                ), errors
        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_variable_declaration_part(tk_list: list, i: int):
        first_variable_declaration = ["<SIMPLE_TYPE>"]
        follow = ["<KEYWORD_PROCEDURE>", "<IDENTIFIER>", "<KEYWORD_BEGIN>"]
        initial = i
        errors = []
        l = len(tk_list)
        has_element = False
        current_i = i
        while True:
            res, e = Analyzers.is_variable_declarator(tk_list, current_i)
            if res.token == "<VARIABLE_DECLARATION>":
                has_element = True
                current_i = res.col[1]
                has_end = False
                optional_errors = []
                errors.extend(e)
                while True:
                    if current_i < l and tk_list[current_i][1] == "<COMMAND_END>":
                        current_i += 1
                        has_end = True
                        break
                    else:
                        if current_i < l:
                            saved_i = current_i
                            current_i = Analyzers.error(current_i, tk_list,
                                                        [*first_variable_declaration, *follow, "<COMMAND_END>"])
                            if current_i == saved_i:
                                break
                            str_error = ""
                            for err_index in range(saved_i, current_i):
                                str_error += tk_list[err_index][0]
                            optional_errors.append(
                                {"message": f"unexpected '{str_error}' before ';'", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})
                        else:
                            break

                if has_end:
                    errors.extend(optional_errors)
                else:
                    errors.append({"message": f"';' expected", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})

                i = current_i
            else:
                break

        if has_element:
            return Token_(tk_list[initial:i], "<VARIABLE_DECLARATION_PART>", (initial, i)), errors

        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

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
            errors.append({"message": "program expected	", "line": tk_list[i][3], "col": tk_list[i][4].split("-")[0]})
            i = Analyzers.error(i + 1, tk_list, ["<IDENTIFIER>"], limit=2)

        if i < l and tk_list[i][1] == "<IDENTIFIER>":
            i += 1
        else:
            errors.append({"message": "program identifier expected", "line": tk_list[i][3], "col": tk_list[i][4].split("-")[0]})
            i = Analyzers.error(i, tk_list, ["<COMMAND_END>"], limit=2)

        if i < l and tk_list[i][1] == "<COMMAND_END>":
            i += 1
        else:
            errors.append({"message": "';' expected", "line": tk_list[i-1][3], "col": tk_list[i-1][4].split("-")[-1]})
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
            errors.append({"message": "'.' expected on the end of program", "line": tk_list[i-1][3], "col": tk_list[i-1][4].split("-")[-1]})
            Analyzers.error(i + 1, tk_list, [])

        return Token_(tk_list[initial:i], "<PROGRAM>", (initial, i + 1)), errors


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
            return Token_(tk_list[initial:i], "<BLOC>", (initial, i)), errors

        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_composite_command(tk_list: list, i: int):
        initial = i
        errors = []
        l = len(tk_list)
        has_begin = False
        if i < l and tk_list[i][1] == "<KEYWORD_BEGIN>":
            i += 1
            has_begin = True
        else:
            errors.append({"message": "begin expected", "line": tk_list[i][3], "col": tk_list[i][4].split("-")[0]})
            i = Analyzers.error(
                i + 1, tk_list,
                ["<IDENTIFIER>", "<KEYWORD_BEGIN>", "<KEYWORD_IF>", "<KEYWORD_PROCEDURE>", "<KEYWORD_WHILE>"], limit=1)

        if i < l:
            res, e = Analyzers.is_command(tk_list, i)
            if res.token == "<COMMAND>":
                i = res.col[1]
                errors.extend(e)
                while i + 1 < l and tk_list[i][1] != "<KEYWORD_END>":
                    res, e = Analyzers.is_command(tk_list, i + 1)
                    if i < l and tk_list[i][1] == "<COMMAND_END>" and res.token == "<COMMAND>":
                        i = res.col[1]
                        errors.extend(e)
                    else:
                        break

                if i < l and tk_list[i][1] == "<KEYWORD_END>":
                    return Token_(tk_list[initial:i], "<COMPOSITE_COMMAND>", (initial, i)), errors
                else:
                    errors.append({"message": "end expected", "line": tk_list[i][3], "col": tk_list[i][4].split("-")[0]})

        if has_begin:
            i = Analyzers.error(i, tk_list, ["<KEYWORD_END>", "<KEYWORD_BEGIN>", "<KEYWORD_IF>", "<KEYWORD_PROCEDURE>", "<KEYWORD_WHILE>", "<IDENTIFIER>"])
            return Token_(tk_list[initial:i], "<COMPOSITE_COMMAND>", (initial, i)), errors

        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_command(tk_list: list, i: int):
        initial = i
        errors = []

        conditions = {
            "<ASSIGNMENT>": Analyzers.is_assignment,
            "<PROCEDURE_CALL>": Analyzers.is_procedure_call,
            "<CONDITIONAL_COMMAND_1>": Analyzers.is_conditional_command_1,
            "<REPETITIVE_COMMAND_1>": Analyzers.is_repetitive_command,
            "<COMPOSITE_COMMAND>": Analyzers.is_composite_command,
        }

        for token_type in conditions:
            res, e = conditions[token_type](tk_list, i)
            if res.token == token_type:
                i = res.col[1]
                errors.extend(e)
                if token_type == "<COMPOSITE_COMMAND>":
                    i += 1
                return Token_(tk_list[initial:i], "<COMMAND>", (initial, i)), errors

        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_assignment(tk_list: list, i: int):
        initial = i
        errors = []
        l = len(tk_list)
        has_equal = False
        res, e = Analyzers.is_variable(tk_list, i)
        if res.token == "<VARIABLE>":
            errors.extend(e)
            if res.col[1] < l and tk_list[res.col[1]][1] == "<EQUALS_SIGN>":
                i = res.col[1] + 1
                has_equal = True
            elif res.col[1] < l and tk_list[res.col[1]][0] == "=":
                errors.append({"message": "':=' expected", "line": tk_list[res.col[1]][3], "col": tk_list[res.col[1]][4].split("-")[0]})
                i = Analyzers.error(res.col[1] + 1, tk_list,
                                    ["<PLUS_SIGN>", "<MINUS_SIGN>", "<OPEN_PARENTHESIS>",
                                     "<KEYWORD_NOT>", "<IDENTIFIER>", "<NUMBER>"], limit=1)
            else:
                return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

            res, e = Analyzers.is_expression(tk_list, i)
            if res.token == "<EXPRESSION>":
                i = res.col[1]
                errors.extend(e)
            elif has_equal:
                errors.append({"message": "expression expected before ':='", "line": tk_list[i-1][3], "col": tk_list[i-1][4].split("-")[0]})
                i = Analyzers.error(i, tk_list,
                                    ["<COMMA>", "<CLOSE_PARENTHESIS>", "<KEYWORD_THEN>",
                                     "<KEYWORD_DO>", "<KEYWORD_END>", "<KEYWORD_ELSE>"], limit=1)
            else:
                return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

            return Token_(tk_list[initial:i], "<ASSIGNMENT>", (initial, i)), errors

        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_variable(tk_list: list, i: int):
        initial = i
        errors = []
        l = len(tk_list)
        if i < l and tk_list[i][1] == "<IDENTIFIER>":
            return Token_(tk_list[initial:i], "<VARIABLE>", (initial, i + 1)), errors

        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_expression(tk_list: list, i: int):
        first_therm = ["<OPEN_PARENTHESIS>", "<KEYWORD_NOT>", "<IDENTIFIER>", "<NUMBER>"]
        follow = ["<COMMA>", "<CLOSE_PARENTHESIS>", "<COMMAND_END>", "<KEYWORD_THEN>", "<KEYWORD_DO>", "<KEYWORD_END>", "<KEYWORD_ELSE>"]
        initial = i
        errors = []
        l = len(tk_list)
        res, e = Analyzers.is_simple_expression(tk_list, i)
        if i < l and res.token == "<SIMPLE_EXPRESSION>":
            i = res.col[1]
            errors.extend(e)
            current_i = i
            optional_errors = []
            has_relation = False
            while current_i < l:
                if current_i < l and tk_list[current_i][1] == "<RELATION>":
                    current_i += 1
                    has_relation = True
                    break
                else:
                    saved_i = current_i
                    current_i = Analyzers.error(current_i, tk_list,
                                                [*first_therm, *follow, "<RELATION>", "<PLUS_SIGN>", "<MINUS_SIGN>"], limit=2)
                    if current_i == saved_i:  # encontrou continuacao  ou não encontrou nada
                        break
                    str_error = ""
                    for err_index in range(saved_i, current_i):
                        str_error += tk_list[err_index][0]
                    optional_errors.append({"message": f"unexpected '{str_error}'", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})

            res, e = Analyzers.is_simple_expression(tk_list, current_i)
            if has_relation and res.token == "<SIMPLE_EXPRESSION>":
                i = res.col[1]
                errors.extend(optional_errors)
                errors.extend(e)
            elif has_relation:
                # provavelmente aqui fazemos o sincronismo
                errors.extend(optional_errors)
                errors.append({"message": f"simple expression expected after relation", "line": tk_list[current_i][3], "col": tk_list[current_i][4].split("-")[0]})
                i = Analyzers.error(current_i, tk_list, follow)
                # não tenho certeza se retornamos erro ou só pulamos mesmo
                # return Token(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

            return Token_(tk_list[initial:i], "<EXPRESSION>", (initial, i)), errors

        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_simple_expression(tk_list: list, i: int):
        first_therm = ["<OPEN_PARENTHESIS>", "<KEYWORD_NOT>", "<IDENTIFIER>", "<NUMBER>"]
        follow_simple_expression = ["<RELATION>", "<COMMA>", "<CLOSE_PARENTHESIS>", "<KEYWORD_THEN>", "<KEYWORD_DO>",
                                    "<KEYWORD_END>", "<COMMAND_END>", "<KEYWORD_ELSE>"]
        initial = i
        errors = []
        l = len(tk_list)
        while True:
            if (
                    i < l and
                    (tk_list[i][1] == "<PLUS_SIGN>"
                     or tk_list[i][1] == "<MINUS_SIGN>")
            ):
                i += 1
                break
            else:
                if i < l:
                    saved_i = i
                    i = Analyzers.error(i, tk_list, [*first_therm, *follow_simple_expression, "<PLUS_SIGN>", "<MINUS_SIGN>"], limit=4)
                    if i == saved_i:  # encontrou sinal/continuacao  ou não encontrou nada
                        break
                    str_error = ""
                    for err_index in range(saved_i, i):
                        str_error += tk_list[err_index][0]
                    errors.append({"message": f"unexpected '{str_error}'", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})
                else:
                    break

        res, e = Analyzers.is_therm(tk_list, i)
        if res.token == "<THERM>":
            i = res.col[1]
            errors.extend(e)
            while i < l:  # verifica se tem repeticoes da parte opcional da expressao simples
                current_i = i
                optional_errors = []
                has_operand = False
                while True:
                    if (
                            current_i < l and
                            (tk_list[current_i][1] == "<PLUS_SIGN>"
                             or tk_list[current_i][1] == "<MINUS_SIGN>"
                             or tk_list[current_i][1] == "<KEYWORD_OR>")
                    ):
                        has_operand = tk_list[current_i][0]
                        current_i += 1
                        break
                    else:
                        if current_i < l:
                            saved_i = current_i
                            current_i = Analyzers.error(current_i, tk_list,
                                                        [*first_therm, *follow_simple_expression, "<PLUS_SIGN>",
                                                         "<MINUS_SIGN>", "<KEYWORD_OR>"], limit=2)
                            if current_i == saved_i:
                                break
                            str_error = ""
                            for err_index in range(saved_i, current_i):
                                str_error += tk_list[err_index][0]
                            optional_errors.append({"message": f"unexpected '{str_error}'", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})

                res, e = Analyzers.is_therm(tk_list, current_i)
                if has_operand is not False and res.token == "<THERM>":
                    i = res.col[1]  # aqui achou uma parte opcional, então pode aumentar o i e salvar erros dessa parte
                    errors.extend(optional_errors)
                    errors.extend(e)
                elif has_operand is not False:  # sincronizacao
                    errors.append({"message": f"therm expected before ", "line": tk_list[current_i][3], "col": tk_list[current_i][4].split("-")[0]})
                    i = Analyzers.error(current_i, tk_list, follow_simple_expression)
                else:  # não encontrou
                    break

            return Token_(tk_list[initial:i], "<SIMPLE_EXPRESSION>", (initial, i)), errors

        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_therm(tk_list: list, i: int):
        initial = i
        errors = []
        l = len(tk_list)
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

            return Token_(tk_list[initial:i], "<THERM>", (initial, i)), errors

        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_factor(tk_list: list, i: int):
        follow_factor = ["<MULTIPLICATION_SIGN>", "<DIVISION_SIGN>", "<KEYWORD_AND>", "<PLUS_SIGN>", "<MINUS_SIGN>",
                         "<KEYWORD_OR>", "<RELATION>", "<CLOSE_PARENTHESIS>", "<COMMA>", "<CLOSE_PARENTHESIS>",
                         "<KEYWORD_THEN>", "<COMMAND_END>", "<KEYWORD_DO>", "<COMMAND_END>", "<KEYWORD_END>", "<KEYWORD_ELSE>"]
        wrong_therms = 4
        initial = i
        errors = []
        l = len(tk_list)
        has_factor = False
        while True:
            if i >= l:
                break

            if tk_list[i][1] == "<IDENTIFIER>" and tk_list[i][0] not in ["read", "write"]:
                i += 1
                has_factor = True
                break

            if tk_list[i][1] == "<NUMBER>":
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
                    errors.extend(e)
                    i = res.col[1]
                    if tk_list[res.col[1]][1] == "<CLOSE_PARENTHESIS>":
                        i+=1
                    else:
                        errors.append({"message": "')' expected", "line": tk_list[res.col[1]][3], "col": tk_list[res.col[1]][4].split("-")[0]})
                        i = Analyzers.error(i, tk_list, follow_factor)
                    has_factor = True
                break

            if tk_list[i][1] == "<KEYWORD_NOT>":
                res, e = Analyzers.is_factor(tk_list, i + 1)
                if res.token == "<FACTOR>":
                    i = res.col[1]
                    errors.extend(e)
                else:
                    errors.append({"message": "expected factor before not", "line": tk_list[i+1][3], "col": tk_list[i+1][4].split("-")[0]})
                    save_i = i
                    i = Analyzers.error(i, tk_list, follow_factor)

                has_factor = True
                break

            if tk_list[i][1] in follow_factor or tk_list[i][0] in ["read", "write"]:
                break

            errors.append({"message": f"unexpected factor '{tk_list[i][0]}'", "line": tk_list[i][3], "col": tk_list[i][4].split("-")[0]})
            i += 1

            wrong_therms -= 1
            if wrong_therms <= 0:
                break

        if has_factor:
            return Token_(tk_list[initial:i], "<FACTOR>", (initial, i)), errors

        return Token_(tk_list[initial: i], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_procedure_call(tk_list: list, i: int):
        follow_procedure_call_command = ["<KEYWORD_END>", "<KEYWORD_ELSE>", "<COMMAND_END>"]
        first_expression_list = ["<PLUS_SIGN>", "<MINUS_SIGN>", "<OPEN_PARENTHESIS>", "<KEYWORD_NOT>", "<IDENTIFIER>",
                                 "<NUMBER>"]
        initial = i
        errors = []
        l = len(tk_list)
        has_open = has_close = has_list = False
        index_missing = -1
        if i < l and tk_list[i][1] == "<IDENTIFIER>":
            i += 1
            current_i = i
            optional_errors = []
            while True:
                if current_i < l and tk_list[current_i][1] == "<OPEN_PARENTHESIS>":
                    has_open = True
                    current_i += 1
                    break
                else:
                    if current_i < l:
                        saved_i = current_i
                        index_missing = saved_i
                        current_i = Analyzers.error(current_i, tk_list, first_expression_list, limit=3)
                        if current_i == saved_i:
                            break
                        str_error = ""
                        for err_index in range(saved_i, current_i):
                            str_error += tk_list[err_index][0]
                        optional_errors.append({"message": f"unexpected '{str_error}'", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})
                    else:
                        break

            res, e = Analyzers.is_expression_list(tk_list, current_i)

            if res.token == "<EXPRESSION_LIST>":
                has_list = True
                current_i = res.col[1]
                if has_open:
                    errors.extend(optional_errors)
                errors.extend(e)

            optional_errors = []
            while True:
                if current_i < l and tk_list[current_i][1] == "<CLOSE_PARENTHESIS>":
                    has_close = True
                    current_i += 1
                    break
                else:
                    if current_i < l:
                        saved_i = current_i
                        current_i = Analyzers.error(current_i, tk_list, follow_procedure_call_command, limit=2)
                        if current_i == saved_i:
                            break
                        str_error = ""
                        for err_index in range(saved_i, current_i):
                            str_error += tk_list[err_index][0]
                        optional_errors.append({"message": f"unexpected '{str_error}'", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})
                    else:
                        break

            if not (has_open or has_close or has_list):  # nao achou parte opcional
                pass
            else:
                if not has_open:
                    errors.append({"message": f"missing '('", "line": tk_list[index_missing][3], "col": tk_list[index_missing][4].split("-")[0]})

                if has_close:
                    errors.extend(optional_errors)
                else:
                    errors.append({"message": f"missing ')'", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})
                i = current_i

            return Token_(tk_list[initial:i], "<PROCEDURE_CALL>", (initial, i)), errors
        return Token_(tk_list[initial: i], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_expression_list(tk_list: list, i: int):
        first_expression_simple_expression = ["<PLUS_SIGN>", "<MINUS_SIGN>", "<OPEN_PARENTHESIS>", "<KEYWORD_NOT>",
                                              "<IDENTIFIER>", "<NUMBER>"]
        initial = i
        errors = []
        l = len(tk_list)
        tk_atual = Convert(tk_list, i)
        res, e = Analyzers.is_expression(tk_list, i)
        if res.token == "<EXPRESSION>":
            i = res.col[1]
            while i < l:  # verifica se tem repeticoes da parte opcional da {, expressao}
                has_comma = False
                current_i = i
                optional_errors = []
                while True:
                    if current_i < l and tk_list[current_i][1] == "<COMMA>":
                        has_comma = True
                        current_i += 1
                        break
                    elif current_i < l:
                        saved_i = current_i
                        current_i = Analyzers.error(current_i, tk_list,
                                                    [*first_expression_simple_expression, "<CLOSE_PARENTHESIS>",
                                                     "<COMMA>"], limit=2)
                        if current_i == saved_i:
                            break
                        str_error = ""
                        for err_index in range(saved_i, current_i):
                            str_error += tk_list[err_index][0]
                        optional_errors.append({"message": f"unexpected '{str_error}'", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})
                    else:
                        pass

                res, e = Analyzers.is_expression(tk_list, current_i)
                if res.token == "<EXPRESSION>":
                    if not has_comma:
                        errors.append({"message": f"',' expected", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})
                    else:
                        errors.extend(optional_errors)
                    i = res.col[1]
                    errors.extend(e)
                elif has_comma:  # sincronização pois teve virgula, mas não expressao
                    errors.extend(optional_errors)
                    errors.append({"message": f"missing expression after ','", "line": tk_list[current_i][3], "col": tk_list[current_i][4].split("-")[0]})
                    i = Analyzers.error(current_i, tk_list, ["<CLOSE_PARENTHESIS>"])
                else:  # nao tenho virgula nem expression, então não tem mais parte opcional
                    break

            return Token_(tk_list[initial:i], "<EXPRESSION_LIST>", (initial, i)), errors

        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_conditional_command_1(tk_list: list, i: int):
        initial = i
        errors = []
        l = len(tk_list)
        tk_atual = Convert(tk_list, i)
        optional_errors = []
        has_if = False
        if i < l and tk_list[i][1] == "<KEYWORD_IF>":
            i += 1
            res, e = Analyzers.is_expression(tk_list, i)
            if res.token == "<EXPRESSION>":
                errors.extend(e)
                i = res.col[1]
                if i < l and tk_list[i][1] == "<KEYWORD_THEN>":
                    i += 1
                else:
                    errors.append({"message": "then expected", "line": tk_list[i][3], "col": tk_list[i][4].split("-")[0]})
                    if i + 1 < l and tk_list[i][1] == "<IDENTIFIER>" and tk_list[i + 1][1] == "<EQUALS_SIGN>":
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
                    return Token_(tk_list[initial: i], "<CONDITIONAL_COMMAND_1>", (initial, i)), errors

            else:
                if i < l:
                    errors.append({"message": "expression expected after if keyword", "line": tk_list[i][3], "col": tk_list[i][4].split("-")[0]})
                i = Analyzers.error(i, tk_list,
                                    ["<KEYWORD_END>", "<COMMAND_END>", "<KEYWORD_ELSE>",
                                     "<IDENTIFIER>", "<KEYWORD_BEGIN>", "<KEYWORD_IF>", "<KEYWORD_WHILE>"])
                return Token_(tk_list[initial: i], "<CONDITIONAL_COMMAND_1>", (initial, i)), errors

        # COLOCAR AQUI O FOLLOW
        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_repetitive_command(tk_list: list, i: int):
        # verificar se dá pra analisar erro com o while
        initial = i
        errors = []
        l = len(tk_list)
        tk_atual = Convert(tk_list, i)
        if i < l and tk_list[i][1] == "<KEYWORD_WHILE>":
            res, e = Analyzers.is_expression(tk_list, i + 1)
            has_do = has_command = has_exp = False
            optional_errors = []
            if res.token == "<EXPRESSION>":
                i = res.col[1]
                has_exp= True
                errors.extend(e)
                if tk_list[i][1] == "<KEYWORD_DO>":
                    i += 1
                    has_do=True
                else:
                    optional_errors.append({"message": "'do' expected", "line": tk_list[i][3], "col": tk_list[i][4].split("-")[0]})
                    i = Analyzers.error(i, tk_list,
                                        ["<IDENTIFIER>", "<KEYWORD_IF>", "<KEYWORD_PROCEDURE>", "<KEYWORD_WHILE>"],
                                        limit=1)

                res, e = Analyzers.is_command(tk_list, i)
                if res.token == "<COMMAND>":
                    i = res.col[1]
                    has_command = True
                else:
                    optional_errors.append({"message": "command expected", "line": tk_list[i][3], "col": tk_list[i][4].split("-")[0]})
            else:
                if i+1 < l:
                    optional_errors.append({"message": "expression expected after while keyword", "line": tk_list[i+1][3], "col": tk_list[i+1][4].split("-")[0]})

            if not has_exp or (not has_do and not has_command):
                if tk_list[i][1] == "<KEYWORD_WHILE>":
                    i+=1
                    errors.extend(optional_errors)
                i = Analyzers.error(i, tk_list,
                                ["<KEYWORD_END>", "<COMMAND_END>", "<KEYWORD_ELSE>",
                                 "<IDENTIFIER>", "<KEYWORD_BEGIN>", "<KEYWORD_IF>", "<KEYWORD_WHILE>"])
            else:
                errors.extend(optional_errors)

            return Token_(tk_list[initial: i], "<REPETITIVE_COMMAND_1>", (initial, i)), errors

            # ACHO QUE AQUI QUE FAREMOS A BUSCA DO FOLLOW
        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_formal_parameter_section(tk_list, i):
        follow = ["<COMMAND_END>", "<CLOSE_PARENTHESIS>"]
        initial = i
        errors = []
        tk_atual = Convert(tk_list, i)
        l = len(tk_list)
        current_i = i
        optional_errors = []
        while True:  # opcional
            if current_i < l and tk_list[current_i][1] == "<KEYWORD_VAR>":
                current_i += 1
                break
            else:
                if current_i < l:
                    saved_i = current_i
                    current_i = Analyzers.error(current_i, tk_list, ["<IDENTIFIER>", "<KEYWORD_VAR>"], limit=3)
                    if current_i == saved_i:
                        break
                    str_error = ""
                    for err_index in range(saved_i, current_i):
                        str_error += tk_list[err_index][0]
                    optional_errors.append({"message": f"unexpected '{str_error}'", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})
                else:
                    break

        res, e = Analyzers.is_identifier_list(tk_list, current_i)
        if res.token == "<IDENTIFIER_LIST>":
            current_i = i = res.col[1]
            errors.extend(optional_errors)
            errors.extend(e)
            optional_errors = []

            has_colon = False
            while True:
                if current_i < l and tk_list[current_i][1] == "<COLON>":
                    current_i += 1
                    has_colon = True
                    break
                else:
                    if current_i < l:
                        saved_i = current_i
                        current_i = Analyzers.error(current_i, tk_list, [*follow, "<SIMPLE_TYPE>", "<COLON>"], limit=3)
                        if current_i == saved_i:
                            break
                        str_error = ""
                        for err_index in range(saved_i, current_i):
                            str_error += tk_list[err_index][0]
                        optional_errors.append(
                            {"message": f"unexpected '{str_error}' before ':'", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})
                    else:
                        break

            if has_colon:
                i = current_i
                errors.extend(optional_errors)
            else:
                errors.append({"message": f"':' expected", "line": tk_list[i][3], "col": tk_list[i][4].split("-")[0]})

            has_type = False
            optional_errors = []
            index_missing = current_i
            while True:
                if current_i < l and tk_list[current_i][1] == "<SIMPLE_TYPE>":
                    current_i += 1
                    has_type = True
                    break
                else:
                    if current_i < l:
                        saved_i = current_i
                        current_i = Analyzers.error(current_i, tk_list, [*follow, "<SIMPLE_TYPE>"], limit=3)
                        if current_i == saved_i:
                            break
                        str_error = ""
                        for err_index in range(saved_i, current_i):
                            str_error += tk_list[err_index][0]
                        optional_errors.append(
                            {"message": f"unexpected '{str_error}' before type", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})
                    else:
                        break

            i = current_i
            if has_type:
                errors.extend(optional_errors)
            else:
                errors.append({"message": f"type expected", "line": tk_list[index_missing][3], "col": tk_list[index_missing][4].split("-")[0]})
            return Token_(tk_list[initial: i], "<FORMAL_PARAMETER_SECTION>", (initial, i)), errors
        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_formal_parameters(tk_list, i):
        first_formal_param_sec = ["<KEYWORD_VAR>", "<IDENTIFIER>"]
        follow = ["<COMMAND_END>", "<KEYWORD_BEGIN>", "<SIMPLE_TYPE>", "<KEYWORD_PROCEDURE>"]
        current_i = initial = i
        errors = []
        tk_atual = Convert(tk_list, i)
        l = len(tk_list)

        has_open = False
        optional_errors = []
        index_missing = current_i
        while True:
            if current_i < l and tk_list[current_i][1] == "<OPEN_PARENTHESIS>":
                current_i += 1
                has_open = True
                break
            else:
                if current_i < l:
                    saved_i = current_i
                    current_i = Analyzers.error(current_i, tk_list, [*first_formal_param_sec, "<OPEN_PARENTHESIS>"], limit=3)
                    if current_i == saved_i:
                        break
                    str_error = ""
                    for err_index in range(saved_i, current_i):
                        str_error += tk_list[err_index][0]
                    optional_errors.append(
                        {"message": f"unexpected '{str_error}' before '('", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})
                else:
                    break
        
        res, e = Analyzers.is_formal_parameter_section(tk_list, current_i)
        if res.token == "<FORMAL_PARAMETER_SECTION>":
            current_i = i = res.col[1]
            if not has_open:
                errors.append({"message": f"expected '('", "line": tk_list[index_missing][3], "col": tk_list[index_missing][4].split("-")[0]})

            errors.extend(optional_errors)
            errors.extend(e)

            while current_i < l: # parte opcional
                has_end = False
                optional_errors = []
                index_missing = current_i
                while True:
                    if current_i < l and tk_list[current_i][1] == "<COMMAND_END>":
                        current_i += 1
                        has_end = True
                        break
                    else:
                        if current_i < l:
                            saved_i = current_i
                            current_i = Analyzers.error(current_i, tk_list,
                                                        [*first_formal_param_sec, "<CLOSE_PARENTHESIS>", "<COMMAND_END>"], limit=3)
                            if current_i == saved_i:
                                break
                            str_error = ""
                            for err_index in range(saved_i, current_i):
                                str_error += tk_list[err_index][0]
                            optional_errors.append(
                                {"message": f"unexpected '{str_error}' before ';'", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})
                        else:
                            break

                res, e = Analyzers.is_formal_parameter_section(tk_list, current_i)
                if res.token == "<FORMAL_PARAMETER_SECTION>":
                    current_i = i = res.col[1]
                    if has_end:
                        errors.extend(optional_errors)
                    else:
                        errors.append({"message": f"';' expected", "line": tk_list[index_missing][3], "col": tk_list[index_missing][4].split("-")[0]})
                    errors.extend(e)
                else: # não tem parte opcional
                    current_i = index_missing
                    break

            has_close = False
            optional_errors = []
            index_missing_close = current_i
            while True:
                if current_i < l and tk_list[current_i][1] == "<CLOSE_PARENTHESIS>":
                    current_i += 1
                    has_close = True
                    break
                else:
                    if current_i < l:
                        saved_i = current_i
                        current_i = Analyzers.error(current_i, tk_list,
                                                    [*follow, "<CLOSE_PARENTHESIS>"], limit=3)
                        if current_i == saved_i:
                            break
                        str_error = ""
                        for err_index in range(saved_i, current_i):
                            str_error += tk_list[err_index][0]
                        optional_errors.append(
                            {"message": f"unexpected '{str_error}' before ')'", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})
                    else:
                        break
            if not has_open and not has_close: # errado de mais
                pass
            elif (has_close or has_open):
                i = current_i
                if not has_close:
                    errors.append({"message": f"expected ')'", "line": tk_list[index_missing_close][3], "col": tk_list[index_missing_close][4].split("-")[0]})
                errors.extend(optional_errors)
                return Token_(tk_list[initial:i], "<FORMAL_PARAMETERS>", (initial, i)), errors

        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_procedure_declaration(tk_list, i):
        if i==0:
            a=1
        first_bloc = ["<KEYWORD_BEGIN>", "<SIMPLE_TYPE>", "<KEYWORD_PROCEDURE>"]
        initial = i
        errors = []
        l = len(tk_list)
        if i < l and tk_list[i][1] == "<KEYWORD_PROCEDURE>":
            i += 1
        else: # se tiver errado o procedure
            if (
                    i < l and tk_list[i][1] == "<IDENTIFIER>" and
                    i + 1 < l and tk_list[i + 1][1] == "<IDENTIFIER>"
            ):
                errors.append({"message": f"keyword 'procedure' expected", "line": tk_list[i][3], "col": tk_list[i][4].split("-")[0]})
                i += 1
            else:
                return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

        if i < l and tk_list[i][1] == "<IDENTIFIER>":
            i += 1
            res, e = Analyzers.is_formal_parameters(tk_list, i)
            current_i = i
            if res.token == "<FORMAL_PARAMETERS>":
                errors.extend(e)
                current_i = res.col[1]
                index_missing = current_i-1
            else:
                index_missing = current_i

            has_end = False
            optional_errors = []
            while True:
                if current_i < l and tk_list[current_i][1] == "<COMMAND_END>":
                    current_i += 1
                    has_end = True
                    break
                else:
                    if current_i < l:
                        saved_i = current_i
                        current_i = Analyzers.error(current_i, tk_list, [*first_bloc, "<COMMAND_END>"],
                                                    limit=3)
                        if current_i == saved_i:
                            break
                        str_error = ""
                        for err_index in range(saved_i, current_i):
                            str_error += tk_list[err_index][0]
                        optional_errors.append(
                            {"message": f"unexpected '{str_error}' before ';'", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})
                    else:
                        break

            i = current_i
            if has_end:
                errors.extend(optional_errors)
            else:
                errors.append({"message": f"expected ';'", "line": tk_list[index_missing][3], "col": tk_list[index_missing][4].split("-")[0]})

            res, e = Analyzers.is_bloc(tk_list, i)
            if res.token == "<BLOC>":
                errors.extend(e)
                i = res.col[1]
                return Token_(tk_list[initial:i], "<PROCEDURE_DECLARATION>", (initial, i)), errors

        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

    @staticmethod
    def is_subroutine_declaration_part(tk_list: list, i: int):
        first_procedure_declaration = ["<KEYWORD_PROCEDURE>"]
        follow = ["<KEYWORD_BEGIN>"]
        initial = i
        errors = []
        l = len(tk_list)
        tk_atual = Convert(tk_list, i)
        has_element = False
        current_i = i
        while True:
            res, e = Analyzers.is_procedure_declaration(tk_list, current_i)
            if res.token == "<PROCEDURE_DECLARATION>":
                has_element = True
                current_i = res.col[1] + 1
                errors.extend(e)
                has_end = False
                optional_errors = []
                index_missing = current_i
                while True:
                    if current_i < l and tk_list[current_i][1] == "<COMMAND_END>":
                        current_i += 1
                        has_end = True
                        break
                    else:
                        if current_i < l:
                            saved_i = current_i
                            current_i = Analyzers.error(current_i, tk_list, [*first_procedure_declaration, *follow, "<COMMAND_END>"])
                            if current_i == saved_i:
                                break
                            str_error = ""
                            for err_index in range(saved_i, current_i):
                                str_error += tk_list[err_index][0]
                            optional_errors.append(
                                {"message": f"unexpected '{str_error}' before ';'", "line": tk_list[saved_i][3], "col": tk_list[saved_i][4].split("-")[0]})
                        else:
                            break

                if has_end:
                    errors.extend(optional_errors)
                else:
                    errors.append({"message": f"';' expected", "line": tk_list[index_missing][3], "col": tk_list[index_missing][4].split("-")[0]})

                i = current_i
            else:
                break

        if has_element:
            return Token_(tk_list[initial:i], "<SUBROUTINE_DECLARATION_PART>", (initial, i)), errors

        return Token_(tk_list[initial: i + 1], "<ERROR>", (initial, i + 1)), errors

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
        res, errors = Analyzers.is_program(tk_list=validated_lexems, i=i)
        # res, errors = Analyzers.is_assignment(tk_list=validated_lexems, i=i)
        # res, errors = Analyzers.is_assignment(tk_list=validated_lexems, i=i)
        # res, errors = Analyzers.is_factor(tk_list=validated_lexems, i=i)
        # res, errors = Analyzers.is_expression_list(tk_list=validated_lexems, i=i)
        # res, errors = Analyzers.is_procedure_call(tk_list=validated_lexems, i=i)
        # res, errors = Analyzers.is_formal_parameter_section(tk_list=validated_lexems, i=i)
        # res, errors = Analyzers.is_formal_parameters(tk_list=validated_lexems, i=i)
        # res, errors = Analyzers.is_procedure_declaration(tk_list=validated_lexems, i=i)
        # res, errors = Analyzers.is_subroutine_declaration_part(tk_list=validated_lexems, i=i)
        # res, errors = Analyzers.is_identifier_list(tk_list=validated_lexems, i=i)
        # res, errors = Analyzers.is_variable_declaration_part(tk_list=validated_lexems, i=i)
        # print(res)
        # print(res.lexem)
        # if res.token != "<ERROR>":, errors
        #     i = res.col[1]
        # else:
        #     return [*new_tokens, res]
        new_tokens.append(res)
        # print(*new_tokens)

        return new_tokens, errors
