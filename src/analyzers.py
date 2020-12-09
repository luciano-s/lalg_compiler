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
                if tk_list[i][1] == "<COMMA>" and tk_list[i+1][1] == "<IDENTIFIER>":
                    i += 2
                else:
                    break
            return Token(tk_list[initial:i], "<IDENTIFIER_LIST>", (initial, i))

        return Token(tk_list[initial:i+1], "<ERROR>", (initial, i+1))

    @staticmethod
    def is_variable_declarator(validated_lexems, i):
        initial = i
        # print(validated_lexems[i][1])
        # input()
        if validated_lexems[i][1] == "<SIMPLE_TYPE>":
            is_ilist = Analyzers.is_identifier_list(validated_lexems, i+1)
            i = is_ilist.col[1]
            if is_ilist.token == "<IDENTIFIER_LIST>":
                return Token(validated_lexems[initial:i],  "<VARIABLE_DECLARATION>", (initial, i))
        return Token(validated_lexems[initial:i+1], "<ERROR>", (initial, i+1))

    @staticmethod
    def is_variable_declaration_part(tk_list: list, i: int):
        initial = i
        first = Analyzers.is_variable_declarator(tk_list, i)
        # print(f"first-lexem{first.lexem}")
        # input()
        if first.token == "<VARIABLE_DECLARATION>":
            i = first.col[1]
            while i < len(tk_list) and i + 1 < len(tk_list):
                next = Analyzers.is_variable_declarator(tk_list, i+1)
                # print(next.token)
                # input()
                if tk_list[i][1] == "<COMMAND_END>" and next.token == "<VARIABLE_DECLARATION>":
                    i = next.col[1]
                else:
                    break
            print(tk_list[i][1])
            if i < len(tk_list) and tk_list[i][1] == "<COMMAND_END>":
                return Token(tk_list[initial:i], "<VARIABLE_DECLARATION_PART>", (initial, i+1))

        return Token(tk_list[initial:i+1], "<ERROR>", (initial, i+1))

    @staticmethod
    def syntax_analyzer(validated_lexems):
        i = 0
        new_tokens = []
        while i < len(validated_lexems):

            # print(validated_lexems[i])
            res = Analyzers.is_variable_declaration_part(tk_list=validated_lexems, i=i)
            print(res)
            print(res.lexem)
            # input()
            if res.token != "<ERROR>":
                i = res.col[1]
            else:
                return [*new_tokens, res]
            new_tokens.append(res)
            print(*new_tokens)
            # input()
        return new_tokens

