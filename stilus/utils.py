
def unwarp(expression):
    """
    Unwrap `expression`.
    Takes an expressions with length of 1
    such as `((1 2 3))` and unwraps it to `(1 2 3)`.

    :param expression:
    :return:
    """
    if expression.preserve:
        return expression
    if expression.name not in ['arguments', 'expression']:
        return expression
    if len(expression) != 1:
        return expression
    if expression.first.name not in ['arguments', 'expression']:
        return expression
    return unwarp(expression.first)

