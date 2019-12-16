from pathlib import Path

import utils
from nodes.literal import Literal
from visitor.compiler import Compiler
from urllib.parse import urlparse


# todo: check evaluator; could be stilus?
# fixme: rewrite this
def resolver(url, options=None, evaluator=None):
    if not options:
        options = {}

    original = url  # super ugly

    # compile the urls nodes and create a url from the result
    compiler = Compiler(url, options)
    filename = url.filename
    compiler.is_url = True
    url = urlparse(compiler.visit(url))

    # fixme: dirty hack
    if url.geturl() == '' and f'{original}' == '(\'#\')':
        literal = Literal('url("#")')
    else:
        # regular call
        literal = Literal(f'url("{url.geturl()}")')
    path = url.path
    dest = options.get('dest', '')
    tail = ''

    # absolute or hash
    if url.scheme or not path or '/' == path[0]:
        return literal

    # check that a file exists
    if options.get('nocheck', True):
        _paths = options.get('paths', [])
        _paths.extend(evaluator.paths)
        path = utils.lookup(path, _paths)
        if not path:
            return literal
        else:
            path = Path(path)

    if evaluator.include_css and path.suffix == '.css':
        return Literal(url.href)

    if url.query:
        tail += url.query
    if url.fragment:
        tail += url.fragment

    if dest and dest.suffix == '.css':
        dest = dest.parent

    if dest:
        first = dest.parents[1]
    else:
        first = Path(evaluator.filename).parent
    if options.get('nocheck', False):
        other = Path(filename).parent
    else:
        other = path

    res = other.relative_to(first.resolve())

    # use the first path of the options['paths'] list as cwd
    cwd = Path(evaluator.options.get('paths', ['.'])[0])
    try:
        res = f'{res.resolve().relative_to(cwd)}{tail}'
    except ValueError:
        res = f'{res}{tail}'

    # todo: handle windows separators?

    return Literal(f'url("{res}")')


def get_resolver():
    return resolver
