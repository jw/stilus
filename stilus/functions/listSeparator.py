from nodes.string import String
from utils import unwrap


def list_separator(list, evaluator=None):
    list = unwrap(list)
    return String(',' if list.is_list else ' ')
