
class ParseError(Exception):

    def __init__(self, message, filename=None, lineno=None,
                 column=None, input=None):
        super().__init__(message)
        self.message = message
        self.filename = filename
        self.lineno = lineno
        self.column = column
        self.input = input


class StilusError(Exception):

    def __init__(self, message, filename=None, lineno=None,
                 column=None, input=None):
        super().__init__(message)
        self.message = message
        self.filename = filename
        self.lineno = lineno
        self.column = column
        self.input = input
        self.from_stilus = None

    def __str__(self):
        if self.message:
            return f'Could not compile: {self.message}'
        else:
            return f'Could not compile.'
