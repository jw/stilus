from os.path import realpath, dirname, join

from stilus.parser import Parser
from stilus.visitor.compiler import Compiler
from stilus.visitor.evaluator import Evaluator
from stilus.visitor.normalizer import Normalizer


class Renderer:

    def __init__(self, s: str, options: dict):
        self.s = s
        self.options = options
        self.options['globals'] = options.get('globals', {})
        self.options['functions'] = options.get('functions', {})
        self.options['use'] = options.get('use', [])
        if not isinstance(self.options['use'], list):
            self.options['use'] = list(self.options['use'])
        self.options['imports'] = [join(dirname(realpath(__file__)),
                                        'functions')]
        self.options['paths'] = options.get('paths', [])
        self.options['filename'] = options.get('filename', 'stilus')
        self.options['Evaluator'] = options.get('Evaluator', Evaluator)

    def render(self):

        # todo: use plugin

        self.parser = Parser(self.s, self.options)
        ast = self.parser.parse()

        self.evaluator = Evaluator(ast, self.options)
        ast = self.evaluator.evaluate()

        self.normalizer = Normalizer(ast, self.options)
        ast = self.normalizer.normalize()

        self.compiler = Compiler(ast, self.options)
        ast = self.compiler.compile()

        # todo: expose sourcemap

        # todo: handle end event

        return ast

    def do_import(self, file):
        self.options['imports'].append(file)
        return self


def render(s, options) -> str:
    return Renderer(s, options).render()
