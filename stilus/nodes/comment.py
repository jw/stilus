import json

from stilus.nodes.node import Node


class Comment(Node):

    def __init__(self, value: str, suppress: bool, inline: bool):
        super().__init__(value)
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
