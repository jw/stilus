import json

from stilus.nodes.node import Node


class Comment(Node):

    def __init__(self, value: str, suppress: bool, inline: bool,
                 lineno=1, column=1):
        super().__init__(value, lineno=lineno, column=column)
        self.suppress = suppress
        self.inline = inline

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.__str__()

    def to_json(self):
        return json.dumps({'__type': 'Comment',
                           'str': self.value,
                           'suppress': self.suppress,
                           'inline': self.inline,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
