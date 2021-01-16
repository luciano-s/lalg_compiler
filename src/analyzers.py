from src.token import Token
from src.tokens import Tokens
from src.validator import Validator


class Analyzers:
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
    def is_identifier_list(tk_list, i):
        initial = i
        if tk_list[i][1] == "<IDENTIFIER>":
            i += 1
            while i < len(tk_list) and i + 1 < len(tk_list):
                if tk_list[i][1] == "<COMMA>" and tk_list[i + 1][1] == "<IDENTIFIER>":
                    i += 2
                else:
                    break
            return Token(tk_list[initial:i], "<IDENTIFIER_LIST>", (initial, i))

        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))

    @staticmethod
    def is_variable_declarator(validated_lexems, i):
        initial = i
        # print(validated_lexems[i][1])
        # input()
        if validated_lexems[i][1] == "<SIMPLE_TYPE>":
            is_ilist = Analyzers.is_identifier_list(validated_lexems, i + 1)
            i = is_ilist.col[1]
            if is_ilist.token == "<IDENTIFIER_LIST>":
                return Token(
                    validated_lexems[initial:i], "<VARIABLE_DECLARATION>", (initial, i)
                )
        return Token(validated_lexems[initial : i + 1], "<ERROR>", (initial, i + 1))

    @staticmethod
    def is_variable_declaration_part(tk_list: list, i: int):
        initial = i
        first = Analyzers.is_variable_declarator(tk_list, i)
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
                )

        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))

    @staticmethod
    def is_program(tk_list: list, i: int):
        initial = i
        if (
            tk_list[i][1] == "<KEYWORD_PROGRAM>"
            and tk_list[i + 1][1] == "<IDENTIFIER>"
            and tk_list[i + 2][1] == "<COMMAND_END>"
        ):
            res = Analyzers.is_bloc(tk_list, i + 3)
            i = res.col[1]  # get the end of the block
            if res.token == "<BLOC>" and tk_list[i + 1][1] == "<DOT>":
                return Token(tk_list[initial:i], "<PROGRAM>", (initial, i + 1))

        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))
    
    @staticmethod
    def is_bloc(tk_list: list, i: int):
        initial = i
        res = Analyzers.is_variable_declaration_part(tk_list, i)
        if res.token == "<VARIABLE_DECLARATION_PART>":
            i = res.col[1]

        res = Analyzers.is_subroutines_declaration_part(tk_list, i)
        if res.token == "<SUBROUTINE_DECLARATION_PART>":
            i = res.col[1]

        res = Analyzers.is_composite_command(tk_list, i)
        if res.token == "<COMPOSITE_COMMAND>":
            return Token(tk_list[initial:i], "<BLOC>", (initial, i + 1))

        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))

    @staticmethod
    def is_composite_command(tk_list: list, i: int):
        initial = i
        if tk_list[i][1] == "<KEYWORD_BEGIN>":
            res = Analyzers.is_command(tk_list, i+1)
            if res.token == "<COMMAND>":
                i = res.col[1] + 1
                while i < len(tk_list) and i + 1 < len(tk_list):
                    res = Analyzers.is_command(tk_list, i+1)
                    if tk_list[i][1] == "<COMMAND_END>" and res.token == "<COMMAND>":
                        i = res.col[1] + 1
                    else:
                        break
                if tk_list[i][1] == "<KEYWORD_END>":
                    return Token(tk_list[initial:i], "<COMPOSITE_COMMAND>", (initial, i + 1))

        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))

    @staticmethod
    def is_command(tk_list: list, i: int):
        initial = i

        conditions = {
            "<ASSIGNMENT>" : Analyzers.is_assignment, 
            "<PROCEDURE_CALL>": Analyzers.is_procedure_call, 
            "<COMPOSITE_COMMAND>": Analyzers.is_composite_command,
            "<CONDITIONAL_COMMAND_1>": Analyzers.is_conditional_command_1,
            "<WHILE_COMMAND_1>": Analyzers.is_while_command_1
        }
        
        for token_type in conditions:
            res = conditions[token_type](tk_list, i)
            if res.token == token_type:
                return Token(tk_list[initial:i], "<COMMAND>", (initial, i + 1))

        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))
            
    @staticmethod
    def is_assignment(tk_list: list, i: int):
        initial = i
        res = Analyzers.is_variable(tk_list, i)
        if res.token == "<VARIABLE>" and tk_list[res.col[1]+1] == "<EQUALS_SIGN>":
            i = res.col[1] + 2
            res = Analyzers.is_expression(tk_list, i)
            if res.token == "<EXPRESSION>":
                i = res.col[1]
                return Token(tk_list[initial:i], "<ASSIGMENT>", (initial, i + 1))

        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))

    @staticmethod
    def is_variable(tk_list: list, i: int):
        initial = i
        if tk_list[i][1] == "<IDENTIFIER>":
            res = Analyzers.is_expression(tk_list, i+1)
            if res.token == "<EXPRESSION>":
                i = res.col[1]
            return Token(tk_list[initial:i], "<VARIABLE>", (initial, i + 1))

        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))
    @staticmethod
    def is_expression(tk_list: list, i: int):
        initial = i
        res = Analyzers.is_simple_expression(tk_list, i+1)
        if res.token == "<SIMPLE_EXPRESSION>":
            i = res.col[1]
            if tk_list[i+1][1] == "<RELATION>":
                i+=1 # arrumar aqui
                res = Analyzers.is_simple_expression(tk_list, i+1)
                if res.token == "<SIMPLE_EXPRESSION>":
                    i = res.col[1]
                else:
                    return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))

            return Token(tk_list[initial:i], "<VARIABLE>", (initial, i + 1))

        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))
    
    @staticmethod
    def is_simple_expression(tk_list: list, i: int):
        initial = i
        has_sign = False
        if (
            tk_list[i][1] == "<PLUS_SIGN>"
            or tk_list[i][1] == "<MINUS_SIGN>"
        ):
            has_sign = True

        res = Analyzers.is_THERM(tk_list, i+1 if has_sign  else i)
        if res.token == "<THERM>":
            i = res.col[1] + 1
            while i < len(tk_list) and i + 1 < len(tk_list):
                res = Analyzers.is_THERM(tk_list, i+1)
                if (
                    tk_list[i][1] == "<PLUS_SIGN>"
                    or tk_list[i][1] == "<MINUS_SIGN>"
                    or tk_list[i][1] == "<KEYWORD_OR>"
                ) and res.token == "<THERM>":
                    i = res.col[1] + 1
                else:
                    break
            return Token(tk_list[initial:i], "<SIMPLE_EXPRESSION>", (initial, i))

        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))

    @staticmethod
    def is_therm(tk_list: list, i: int):
        initial = i
        res = Analyzers.is_factor(tk_list, i)
        if res.token == "<FACTOR>":
            i = res.col[1] + 1
            while i < len(tk_list) and i + 1 < len(tk_list):
                res = Analyzers.is_factor(tk_list, i+1)
                if tk_list[i][1] in [
                    "<MULTIPLICATION_SIGN>", 
                    "<DIVISION_SIGN>", 
                    "<KEYWORD_AND>"
                ] and res.token == "<FACTOR>":
                    i = res.col[1] + 1
                else:
                    break
            return Token(tk_list[initial:i], "<THERM>", (initial, i))

        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))

    @staticmethod
    def is_factor(tk_list: list, i: int):
        initial = i
        while True:
            res = Analyzers.is_variable(tk_list, i)
            if res.token == "<VARIABLE>":
                i = res.col[1]
                break

            if tk_list[i][1] == "<NUMBER>": # TODO: arrumar, pois até lexemas tem col[ini, end]
                i+=1
                break
            
            if tk_list[i][1] == "<OPEN_PARENTHESIS>":
                res = Analyzers.is_expression(tk_list, i+1)
                if res.token == "<EXPRESSION>":
                    i = res.col[1]+1
                    if tk_list[i][1] == "<CLOSE_PARENTHESIS>":
                        break

            if tk_list[i][1] == "<KEYWORD_NOT>":
                res = Analyzers.is_factor(tk_list, i+1)
                if res.token == "<FACTOR>":
                    i = res.col[1]
                    break
            
            break

        if initial != i:
            return Token(tk_list[initial:i], "<FACTOR>", (initial, i + 1))

        return Token(tk_list[initial : i], "<ERROR>", (initial, i + 1))

    @staticmethod
    def is_procedure_call(tk_list: list, i: int):
        initial = i
        if tk_list[i][1] == "<IDENTIFIER>":
            i+=1
            res = Analyzers.is_expression_list(tk_list, i+1)
            if (
                tk_list[i][1] == "<OPEN_PARENTHESIS>" 
                and res.token == "<EXPRESSION_LIST>" 
                and tk_list[res.col[1]+1][1] == "<CLOSE_PARENTHESIS>"
            ):
                i+=res.col[1]+1

                return Token(tk_list[initial:i], "<PROCEDURE_CALL>", (initial, i + 1))
        return Token(tk_list[initial : i], "<ERROR>", (initial, i + 1))
    
    @staticmethod
    def is_expression_list(tk_list: list, i: int):
        initial = i
        res = Analyzers.is_expression(tk_list, i)
        if res.token == "<EXPRESSION>":
            i += res.col[1]+1 # TODO: verificar finalização de indice
            while i < len(tk_list) and i + 1 < len(tk_list):
                res = Analyzers.is_expression(tk_list, i+1)
                if tk_list[i][1] == "<COMMA>" and res.token == "<EXPRESSION>":
                    i+=res.col[1]+2
                else:
                    break
            
            return Token(tk_list[initial:i], "<IDENTIFIER_LIST>", (initial, i))

        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))

    @staticmethod
    def is_conditional_command_1(tk_list: list, i: int):
        initial = i
        if tk_list[i][1] == "<KEYWORD_IF>":
            res = Analyzers.is_expression(tk_list, i+1)
            if res.token == "<EXPRESSION>":
                i = res.col[1] + i
                if tk_list[i+1][1] == "<KEYWORD_THEN>":
                    res = Analyzers.is_command(tk_list, i+1)
                    if res.token == "<COMMAND>":
                        i = res.col[1] + i
                        if tk_list[i+1][1] ==  "<KEYWORD_ELSE>":
                            res = Analyzers.is_command(tk_list, i+1)
                            if res.token == "<COMMAND>":
                                i = res.col[1] + i
                        return Token(tk_list[initial: i], "<CONDITIONAL_COMMAND_1>", (initial, i))
        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))

    @staticmethod
    def is_repetitive_command(tk_list, i):
        initial = i
        if tk_list[i][1] == "<KEYWORD_WHILE>":
            res = Analyzers.is_expression(tk_list, i+1)
            if res.token == "<EXPRESSION>":
                i = res.col[1] + i
                if tk_list[i+1][1] == "<KEYWORD_DO>":
                    res = Analyzers.is_command(tk_list, i+1)
                    if res.token == "<COMMAND>":
                            i = res.col[1] + i
                            return Token(tk_list[initial: i], "<REPETITIVE_COMMAND_1>", (initial, i))
        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))
        
    @staticmethod
    def is_formal_parameter_section(tk_list, i):
        initial = i
        if tk_list[i][1] == "<KEYWORD_VAR>":
            res = Analyzers.is_identifier_list(tk_list, i+1)
            if res.token == "<IDENTIFIER_LIST>":
                i = res.col[1] + i
                if tk_list[i+1][1] == "<COLON>":
                    i +=1
                    res = Analyzers.is_identifier(tk_list, i+1)
                    if res.token == "<IDENTIFIER>":
                        i = res.col[1] + i
                        return Token(tk_list[initial: i], "<FORMAL_PARAMETER_SECTION>", (initial, i))
        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))

    @staticmethod
    def is_formal_parameters(tk_list, i):
        initial = i
        if tk_list[i][1] == "<OPEN_PARENTHESIS>":
            res = Analyzers.is_formal_parameter_section(tk_list, i+1)
            if res.token == "<FORMAL_PARAMETER_SECTION>":
                while res.token == "<FORMAL_PARAMETER_SECTION>":
                    i = res.col[1] + i
                    if tk_list[i+1][1] == "<SEMICOLON>":
                        res = Analyzers.is_formal_parameter_section(tk_list, i+1)
                        i = res.col[1] + i 
                        if tk_list[i+1][1] == "<CLOSE_PARENTHESIS>":
                            return Token(tk_list[initial:i], "<FORMAL_PARAMETERS>", (initial, i))

        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))

    @staticmethod
    def is_procedure_declaration(tk_list, i):
        initial = i
        if tk_list[i][1] == "<KEYWORD_PROCEDURE>":
            if tk_list[i+1][1] == "<IDENTIFIER>":
                res = Analyzers.is_formal_parameters(tk_list, i+2)
                if res.token == "<FORMAL_PARAMETERS>" and tk_list[i+res.col[1]+1] == "<SEMICOLON>":
                    i = res.col[1] + i + 1
                    res = Analyzers.is_bloc(tk_list, i+1)
                    if res.token == "<BLOC>":
                        return Token(tk_list[initial:i], "<PROCEDURE_DECLARATION>", (initial, i))
                elif tk_list[i+2][1] == "<SEMICOLON>":
                    i += 2
                    res = Analyzers.is_bloc(tk_list, i+1)
                    if res.token == "<BLOC>":
                        return Token(tk_list[initial:i], "<PROCEDURE_DECLARATION>", (initial, i))
        
        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))

    @staticmethod
    def is_part_subroutine_declaration(tk_list, i):
        initial = i
        res = Analyzers.is_procedure_declaration(tk_list, i+1)
        if res.token == "<PROCEDURE_DECLARATION>":
            if tk_list[i][1] == "<OPEN_BRACKET>":
                i = res.col[1] + i
                if tk_list[i+1][1] == "<COLON>":
                    i +=1
                    if tk_list[i+1][1] == "<CLOSE_BRACKET>":
                        return Token(tk_list[initial:i], "<PART_SUBROUTINE_DECLARATION>", (initial, i))
        return Token(tk_list[initial : i + 1], "<ERROR>", (initial, i + 1))

    @staticmethod
    def syntax_analyzer_for_variable(validated_lexems):
        i = 0
        new_tokens = []
        while i < len(validated_lexems):

            res = Analyzers.is_variable_declaration_part(tk_list=validated_lexems, i=i)
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
        while i < len(validated_lexems):

            res = Analyzers.is_program(tk_list=validated_lexems, i=i)
            print(res)
            print(res.lexem)
            if res.token != "<ERROR>":
                i = res.col[1]
            else:
                return [*new_tokens, res]
            new_tokens.append(res)
            print(*new_tokens)

        return new_tokens
