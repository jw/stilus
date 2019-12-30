import re

from stilus import utils
from stilus.utils import assert_type


def get_flags(flags=None):
    f = 0
    if flags:
        for c in flags.string:
            if "i" == c:
                f |= re.I
            if "m" == c:
                f |= re.M
    return f


def stilus_findall(pattern, string, flags=None):
    p = re.compile(pattern, get_flags(flags))
    if flags and "g" in flags.string:
        return p.findall(string)
    else:
        m = p.search(string)
        if m:
            return [m.group(0)] + list(m.groups())
    from stilus.nodes.null import null

    return null


def match(pattern, val, flags=None, evaluator=None):
    assert_type(pattern, "string", "pattern")
    utils.assert_string(val, "val")
    return stilus_findall(pattern.value, val.string, flags)
