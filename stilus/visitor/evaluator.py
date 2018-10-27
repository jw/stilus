from stilus.visitor.visitor import Visitor


class Evaluator(Visitor):

    def __init__(self, ast, options):
        super().__init__(ast)
        self.options = options

    def evaluate(self):
        pass
