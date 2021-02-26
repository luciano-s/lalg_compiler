from src.validator import Validator


class Tokens:
    def __init__(self):
        self.validator = Validator()
        self.has_comment = False

    def verify_composite(self, in_, col, token_list):
        if in_ != "":
            col_i = col - len(in_)
            token_list.append((col_i, col, self.validator.validate_lexem(in_)))
            in_ = ""
        return in_

    def split_token(self, input: str) -> list:
        token_list = []
        number = ""
        error = ""
        col = 0
        previous_token = ""
        line_comment = input.find("//")
        for c in input:
            col += 1
            if c == "{" or col == line_comment+1:
                self.has_comment = True
                if previous_token not in ["", " ", "\t"]:
                    token_type = self.validator.validate_lexem(previous_token)
                    token_list.append((token_type, col, col + 1))
                    previous_token=""
                continue
            elif c == "}" and self.has_comment:
                self.has_comment = False
                continue
            elif self.has_comment:
                continue
            # current_token = self.validator.validate_lexem(c)
            current_token = self.validator.validate_lexem(previous_token + c)
            # print("P:", previous_token+c)
            # print(current_token[previous_token+c])

            if current_token[previous_token + c] is None and previous_token != "":
                # print("P:", previous_token)
                token_type = self.validator.validate_lexem(previous_token)
                # token_list.append(Token(previous_token, token_type[previous_token], col)
                token_list.append((token_type, col - len(previous_token), col))
                previous_token = ""

                if c not in ["", " ", "\t"]:
                    previous_token += c

                continue

            if c in ["", " ", "\t"]:
                continue
            previous_token += c

        # number=self.verify_composite(number, col, token_list)
        # error=self.verify_composite(error, col, token_list)
        # print("P:", previous_token)
        if previous_token not in ["", " ", "\t"]:
            token_type = self.validator.validate_lexem(previous_token)
            if len(previous_token) == 1:
                token_list.append((token_type, col, col+1))
            else:
                token_list.append((token_type, col - len(previous_token)+1, col+1))

        if line_comment != -1:
            self.has_comment = False

        return token_list

    def split_tokens(self, inputs: list) -> list:
        return [self.split_token(in_) for in_ in inputs]

    def generate_tokens(self, inputs: list) -> list:
        # [<TIPO_SIMPLES>, <IDENTIFIER>, <COMMA>, <IDENTIFIER>. <SINAL_IGUAL>]
        token_list = []
        for token in inputs:
            token_type = self.validator.validate_token([*token_list, token[1]])
            # print([*token_list, token])
            token_list.append(token)
        # token_type = self.validator.validate_token(inputs)
        return token_list
        # print(inputs, "->", token_type.token)

if __name__ == "__main__":
    # print(Tokens().split_token("program correto;"))
    # print(Tokens().split_token("program correto; "))
    # print(Tokens().split_token("int a, b, c;"))
    # print(Tokens().split_token("boolean d, e, f;"))
    # print(Tokens().split_token("procedure proc(var a1 : int);"))
    # print(Tokens().split_token("begin"))
    # print(Tokens().split_token(" 	a:=1;"))
    # print(Tokens().split_token("if (a<1)"))
    # print(Tokens().split_token("end;"))
    # print(Tokens().split_token("a:=b+c;"))
    # print(Tokens().split_token("d:=true;"))
    # print(Tokens().split_token("read(a);"))
    # print(Tokens().split_token("write(b);"))
    # print(Tokens().split_token("b:=10*c;"))
    # print(Tokens().split_token("c:=a div b"))
    # print(Tokens().split_token("a:=a-1"))
    # print(Tokens().split_token("end."))
    # print(Tokens().split_token("if (a<1)@"))
    # Tokens().generate_tokens(
    #     ['<IDENTIFIER>', '<COMMA>', '<IDENTIFIER>', '<COMMA>', '<IDENTIFIER>'])
    # Tokens().generate_tokens(
    #     ['<IDENTIFIER>', '<COMMA>', '<IDENTIFIER>', '<COMMA>'])
    # Tokens().generate_tokens(
    #     ['<IDENTIFIER>', '<IDENTIFIER>'])
    # Tokens().generate_tokens(['<IDENTIFIER>'])
    # Tokens().generate_tokens(['<SIMPLE_TYPE>', '<IDENTIFIER>', '<COMMA>',
    #                           '<IDENTIFIER>', '<COMMA>', '<IDENTIFIER>', '<COMMAND_END>'])

    # <FORMAL_PARAMETERS>
    # Tokens().generate_tokens(
    #     ['<VAR_DECLARATION>', '<COMMAND_END>', '<VAR_DECLARATION>'])
    # Tokens().generate_tokens(
    #     ['<VAR_DECLARATION>', '<COMMAND_END>'])
    # Tokens().generate_tokens(
    #     ['<KEYWORD_VAR>', '<IDENTIFIER>', '<COLON>', '<SIMPLE_TYPE>'])
    # Tokens().generate_tokens(
    #     ['<KEYWORD_VAR>', '<IDENTIFIER_LIST>', '<COLON>', '<SIMPLE_TYPE>'])
    # Tokens().generate_tokens(
    #     ['<IDENTIFIER_LIST>', '<COLON>', '<SIMPLE_TYPE>'])

    # Tokens().generate_tokens(
    #     ['<OPEN_PARENTHESIS>', '<FORMAL_PARAMETERS_SECTION>', '<COMMAND_END>', '<FORMAL_PARAMETERS_SECTION>', '<CLOSE_PARENTHESIS>'])
    # Tokens().generate_tokens(
    #     ['<OPEN_PARENTHESIS>', '<FORMAL_PARAMETERS_SECTION>', '<COMMAND_END>', '<FORMAL_PARAMETERS_SECTION>', '<COMMAND_END>', '<CLOSE_PARENTHESIS>'])
    # Tokens().generate_tokens(
    #     ['<OPEN_PARENTHESIS>', '<FORMAL_PARAMETERS_SECTION>', '<FORMAL_PARAMETERS_SECTION>', '<CLOSE_PARENTHESIS>'])
    # Tokens().generate_tokens(
    #     ['<FORMAL_PARAMETERS_SECTION>', '<COMMAND_END>', '<FORMAL_PARAMETERS_SECTION>', '<CLOSE_PARENTHESIS>'])
    # Tokens().generate_tokens(
    #     ['<OPEN_PARENTHESIS>', '<FORMAL_PARAMETERS_SECTION>', '<COMMAND_END>', '<FORMAL_PARAMETERS_SECTION>'])

    # PROCEDURE_DECLARATION
    # Tokens().generate_tokens(
    #     ['<KEYWORD_PROCEDURE>', '<IDENTIFIER>', '<FORMAL_PARAMETERS>', '<COMMAND_END>', '<BLOC>'])
    # Tokens().generate_tokens(
    #     ['<KEYWORD_PROCEDURE>', '<IDENTIFIER>', '<COMMAND_END>', '<BLOC>'])
    # Tokens().generate_tokens(
    #     ['<KEYWORD_PROCEDURE>', '<IDENTIFIER>', '<BATATA>', '<COMMAND_END>', '<BLOC>'])
    # Tokens().generate_tokens(
    #     ['<KEYWORD_PROCEDURE>', '<COMMAND_END>', '<BLOC>'])

    # SUBROUTINES DECLARATION PART
    # Tokens().generate_tokens(
    #     ['<PROCEDURE_DECLARATION>', '<COMMAND_END>'])
    # Tokens().generate_tokens(
    #     ['<PROCEDURE_DECLARATION>'])
    # Tokens().generate_tokens(
    #     ['<PROCEDURE_DECLARATION>', '<COMMAND_END>', '<COMMAND_END>'])
    # Tokens().generate_tokens(
    #     ['<PROCEDURE_DECLARATION>', '<COMMAND_END>', '<PROCEDURE_DECLARATION>', '<COMMAND_END>'])
    # Tokens().generate_tokens(
    #     ['<COMMAND_END>'])
    # Tokens().generate_tokens(
    #     ["<KEYWORD_PROGRAM>", "<IDENTIFIER>", "<COMMAND_END>", "<BLOC>", "<DOT>"]
    # )
    # Tokens().generate_tokens(["<VARIABLE>"])
    # Tokens().generate_tokens(["<NUMBER>"])
    # Tokens().generate_tokens(
    #     ["<OPEN_PARENTHESIS>", "<EXPRESSION>", "<CLOSE_PARENTHESIS>"]
    # )
    # Tokens().generate_tokens(["<KEYWORD_NOT>", "<FACTOR>"])
    # Tokens().generate_tokens(
    #     ["<FACTOR>", "<MULTIPLICATION_SIGN>", "<FACTOR>", "<DIVISION_SIGN>", "<FACTOR>"]
    # )
    # Tokens().generate_tokens(
    #     [
    #         "<FACTOR>",
    #         "<MULTIPLICATION_SIGN>",
    #         "<FACTOR>",
    #         "<MULTIPLICATION_SIGN>",
    #         "<FACTOR>",
    #     ]
    # )
    # Tokens().generate_tokens(["<FACTOR>", "<DIVISION_SIGN>", "<FACTOR>"])
    # Tokens().generate_tokens(["<FACTOR>", "<KEYWORD_AND>", "<FACTOR>"])
    # Tokens().generate_tokens(["<FACTOR>", "<KEYWORD_AND>"])

    # Tokens().generate_tokens(["<THERM>", "<KEYWORD_OR>", "<THERM>"])
    # Tokens().generate_tokens(["<PLUS_SIGN>", "<THERM>", "<KEYWORD_OR>", "<THERM>"])
    # Tokens().generate_tokens(
    #     ["<PLUS_SIGN>", "<THERM>", "<KEYWORD_OR>", "<THERM>", "<MINUS_SIGN>", "<THERM>"]
    # )
    # Tokens().generate_tokens(
    #     ["<PLUS_SIGN>", "<THERM>", "<KEYWORD_OR>", "<THERM>", "<KEYWORD_OR>", "<THERM>"]
    # )
    # Tokens().generate_tokens(["<THERM>", "<KEYWORD_OR>", "<THERM>"])
    # Tokens().generate_tokens(["<THERM>", "<KEYWORD_OR>"])
    # print(Tokens().split_token("or"))
    # print(Tokens().split_token("and"))

    # Tokens().generate_tokens(
    #     ["<SIMPLE_EXPRESSION>", "<RELATION>", "<SIMPLE_EXPRESSION>"]
    # )
    # Tokens().generate_tokens(["<SIMPLE_EXPRESSION>"])
    # Tokens().generate_tokens(["<SIMPLE_EXPRESSION>", "<RELATION>"])
    # Tokens().generate_tokens(["<EXPRESSION>"])
    # Tokens().generate_tokens(["<EXPRESSION>", "<EXPRESSION>"])
    # Tokens().generate_tokens(
    #     ["<EXPRESSION>", "<EXPRESSION>" "<EXPRESSION>", "<EXPRESSION>"]
    # )
    # Tokens().generate_tokens(["<IDENTIFIER>"])
    # Tokens().generate_tokens(["<EXPRESSION>"])
    # Tokens().generate_tokens(["<IDENTIFIER>", "<EXPRESSION>"])

    str_file = """program correto;
int a, b, c;
boolean d, e, f;

procedure proc(var a1 : int);
int a, b, c;
boolean d, e, f;
begin
	a:=1;
	if (a<1)
		a:=12
end;

begin
	a:=2;
	b:=10;
	c:=11;
	a:=b+c;
	d:=true;
	e:=false;
	f:=true;
	read(a);
	write(b);
	if (d)
	begin
		a:=20;
		b:=10*c;
		c:=a div b
	end;
	while (a>1)
	begin
		if (b>10)
			b:=2;
		a:=a-1
	end
end."""

    str_file2 = """program correto;
int &a, b, c;
boolean d, e, f;

procedure proc(var a1 : int);
int a, b, c;
boolean d, e, f;
begin
	a:=1;
	if (a<1)@
		a:=12
end;

begin
	a:=2;
	b:=10;
	c:=11;#
	a:=b+c;
	d:=true;
	e:=false;
	f:=true;
	if (d)
	begin
		a:=20;
		b:=10*c;
		c:=a div b
	end;
	while (a>1)
	begin
		if (b>10)
			b:=2;
		a:=a-1
	end
end."""
    # [print(i+1,Tokens().split_token(x)) for i, x in enumerate(str_file.split("\n"))]
    # print(Tokens().split_tokens())
