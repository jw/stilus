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

    v = url.value  # super ugly

    # compile the urls nodes and create a url from the result
    compiler = Compiler(url, options)
    filename = url.filename
    compiler.is_url = True
    # print(url)
    url = urlparse(url.value)

    # fixme: make sure that the url is an Expression
    # ''.join([compiler.visit(node)
    #                         for node in url.nodes]))

    # fixme: dirty hack
    if url.geturl() == '' and v == '#':
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
        path = utils.lookup_index(path, _paths, filename)
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
        first = evaluator.filename
    if options.get('nocheck', True):
        other = Path(filename).parent
    else:
        other = path
    res = first.relative_to(other) + tail

    # todo: handle windows separators?

    return Literal(f'url("{res}")')


def get_resolver(options):
    return resolver
