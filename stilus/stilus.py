from stilus.evaluator import Evaluator
from stilus.parser import Parser
from stilus.visitor.compiler import Compiler
from stilus.visitor.normalizer import Normalizer


class Renderer:

    def __init__(self, s, options):
        self.s = s
        self.options = options

    def render(self):

        self.parser = Parser(self.s, self.options)
        ast = self.parser.parse()

        self.evaluator = Evaluator(ast, self.options)
        ast = self.evaluator.evaluate()

        self.normalizer = Normalizer(ast, self.options)
        ast = self.normalizer.normalize()

        self.compiler = Compiler(ast, self.options)
        css = self.compiler.compile()

        return css


def render(s, options):
    return Renderer(s, options).render()
