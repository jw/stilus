from stilus.parser import Parser
from stilus.visitor.evaluator import Evaluator


def test_evaluator_create():
    parser = Parser('abc\n  color: red\n', {})
    root = parser.parse()
    evaluator = Evaluator(root, {})
    result = evaluator.evaluate()
    assert result is None


if __name__ == '__main__':
    parser = Parser('abc\n  color: red\n', {})
    root = parser.parse()
    evaluator = Evaluator(root, {})
    result = evaluator.evaluate()
    assert result is None
