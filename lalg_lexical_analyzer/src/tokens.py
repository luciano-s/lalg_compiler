
from src.validator import Validator


class Tokens:
    def __init__(self):
        self.validator = Validator()

    def verify_composite(self, in_, col, token_list):
        if in_ != "":
            col_i = col-len(in_)
            token_list.append(
                (col_i, col, self.validator.validate_lexem(in_)))
            in_ = ""
        return in_

    def split_token(self, input: str) -> list:
        token_list = []
        number = ""
        error = ""
        col = 1
        for c in input:
            token_type = self.validator.validate_lexem(c)
            if token_type[c] == "<NUMBER>" or c == ".":
                number += c
                error = self.verify_composite(error, col, token_list)
            elif token_type[c] is None and c != " ":
                error += c
                number = self.verify_composite(number, col, token_list)
            else:
                number = self.verify_composite(number, col, token_list)
                error = self.verify_composite(error, col, token_list)
                if c != " ":
                    token_list.append((col, col+1, token_type))
            col += 1

        number = self.verify_composite(number, col, token_list)
        error = self.verify_composite(error, col, token_list)

        return token_list

    def split_tokens(self, inputs: list) -> list:
        return [self.split_token(in_) for in_ in inputs]
