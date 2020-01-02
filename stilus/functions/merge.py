from stilus import utils
from stilus.utils import assert_present, assert_type, unwrap


def merge(dest, *args, evaluator=None):
    assert_present(dest, "dest")
    dest = unwrap(dest).first()
    assert_type(dest, "objectnode", "dest")

    last = unwrap(args[len(args) - 1]).first()
    deep = True is last.value

    for arg in args:
        values = unwrap(arg).first()
        if hasattr(values, "values"):
            utils.merge(dest.values, unwrap(arg).first().values, deep)

    return dest
