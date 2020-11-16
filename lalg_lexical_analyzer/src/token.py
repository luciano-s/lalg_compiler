class Token:
    def __init__(self, lexem, token, col):
        self.token = token
        self.lexem = lexem
        self.is_valid = None
        self.col = col
        self.line = None
