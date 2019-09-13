def pathjoin(*args, evaluator=None):
    paths = []
    for arg in args:
        paths.append(arg.first().string)
    return '/'.join(paths)
