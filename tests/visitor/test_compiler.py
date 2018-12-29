from stilus.parser import Parser
from stilus.visitor.compiler import Compiler
from stilus.visitor.evaluator import Evaluator
from stilus.visitor.normalizer import Normalizer


def test_compiler_create():
    parser = Parser('abc\n  color: red\n', {})
    root = parser.parse()
    evaluator = Evaluator(root, {})
    result = evaluator.evaluate()
    normalizer = Normalizer(result, {})
    result = normalizer.normalize()
    compiler = Compiler(result, {})
    result = compiler.compile()
    assert f'{result}' == 'abc {\n  color: #f00;\n}\n'
