class Token:
    def __init__(self, lexem, token, col):

        self.token = token
        self.lexem = lexem
        self.is_valid = False if token == "<ERROR>" else True
        self.col = col
        self.line = None

    def __str__(self):
        return f"token: {self.token}, column: {self.col}"

    def get_line(self):
        if len(self.lexem) > 0:
            return str(self.lexem[0][3]) + "-" + str(self.lexem[-1][3])
        return ""

    def get_column(self):
        if len(self.lexem) > 0:
            return self.lexem[0][4].split("-")[0] + "-" + self.lexem[-1][4].split("-")[1]
        else:
            return ""
