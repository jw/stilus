from stilus.nodes.expression import Expression
from stilus.nodes.string import String
from stilus.selector_parser import SelectorParser


def selectors(evaluator=None):
    stack = evaluator.selector_stack()
    expr = Expression(is_list=True)
    if stack:
        for i, group in enumerate(stack):
            if len(group) > 1:
                selector_values = []
                for selector in group:
                    nested = SelectorParser(selector.value).parse()["nested"]
                    if nested and i != 0:
                        selector_values.append(f"& {selector.value}")
                    else:
                        selector_values.append(f"{selector.value}")
                expr.append(String(",".join(selector_values)))
            else:
                selector = group[0].value
                nested = SelectorParser(selector).parse()["nested"]
                if nested and i != 0:
                    expr.append(String(f"& {selector}"))
                else:
                    expr.append(String(f"{selector}"))
    else:
        expr.append(String("&"))
    return expr
