from .parser import Parser
from .utils import coerce
from .visitor.compiler import Compiler
from .visitor.evaluator import Evaluator
from .visitor.normalizer import Normalizer


class Renderer:
    def __init__(self, s: str, options: dict):
        self.s = s
        self.options = options
        self.options["globals"] = options.get("globals", {})
        self.options["functions"] = options.get("functions", {})
        self.options["use"] = options.get("use", [])
        if not isinstance(self.options["use"], list):
            self.options["use"] = list(self.options["use"])
        # todo: fix me and use pathlib
        from os.path import realpath, dirname, join

        self.options["imports"] = [
            join(dirname(realpath(__file__)), "functions")
        ]
        self.options["paths"] = options.get("paths", [])
        self.options["filename"] = options.get("filename", "stilus")
        self.options["Evaluator"] = options.get("Evaluator", Evaluator)

    def render(self):

        # todo: use plugin

        self.parser = Parser(self.s, self.options)
        ast = self.parser.parse()

        self.evaluator = Evaluator(ast, self.parser, self.options)
        ast = self.evaluator.evaluate()

        self.normalizer = Normalizer(ast, self.parser, self.options)
        ast = self.normalizer.normalize()

        self.compiler = Compiler(ast, self.options)
        ast = self.compiler.compile()

        # todo: expose sourcemap

        # todo: handle end event

        return ast

    def include(self, path):
        self.options["paths"].append(path)
        return self

    def define(self, name, fn, raw=True, options=None):
        fn = coerce(fn, raw)
        if hasattr(fn, "node_name"):
            self.options["globals"][name] = fn
            return self

        self.options["functions"][name] = fn
        if raw:
            fn.raw = raw
            # todo: add it to the raw_bifs here?
        if options:
            fn.options = options
        return self

    def do_import(self, file):
        self.options["imports"].append(file)
        return self


def render(s, options) -> str:
    return Renderer(s, options).render()
