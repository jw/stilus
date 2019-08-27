from stilus.nodes.string import String
from stilus.utils import unwrap


def list_separator(list, evaluator=None):
    list = unwrap(list)
    return String(',' if list.is_list else ' ')
