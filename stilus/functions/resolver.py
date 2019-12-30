import inspect
import logging
from pathlib import Path
from urllib.parse import urlparse

from stilus import utils
from stilus.nodes.literal import Literal
from stilus.visitor.compiler import Compiler

log = logging.getLogger(__name__)


# todo: check evaluator; could be stilus?
# fixme: rewrite this
def resolver(url, options=None, evaluator=None):
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    log.debug(
        f"Resolver called by {module.__file__} " f"({frame[0].f_lineno})."
    )
    log.debug(f'Functions: {evaluator.options["functions"]}.')
    if not options:
        options = {}

    original = url  # super ugly

    # compile the urls nodes and create a url from the result
    compiler = Compiler(url, options)
    filename = url.filename
    compiler.is_url = True
    url = urlparse(compiler.visit(url))

    # fixme: dirty hack
    if url.geturl() == "" and f"{original}" in ["'#'", "('#')"]:
        literal = Literal('url("#")')
    else:
        # regular call
        literal = Literal(f'url("{url.geturl()}")')
    path = url.path
    dest = options.get("dest", "")
    tail = ""

    # absolute or hash
    if url.scheme or not path or "/" == path[0]:
        return literal

    # check that a file exists
    if options.get("nocheck", True):
        _paths = options.get("paths", [])
        _paths.extend(evaluator.paths)
        path = utils.lookup(path, _paths)
        if not path:
            return literal
        else:
            path = Path(path)

    if evaluator.include_css and path.suffix == ".css":
        return Literal(url.geturl())

    if url.query or url.fragment:
        # fixme: extend url with a sep!
        if "#" in f"{original}":
            tail += "#"
        else:
            tail += "?"
    if url.query:
        tail += url.query
    if url.fragment:
        tail += url.fragment

    if dest and dest.suffix == ".css":
        dest = dest.parent

    if dest:
        first = dest.parents[1]
    else:
        first = Path(evaluator.filename).parent
    if options.get("nocheck", False):
        other = Path(filename).parent
    else:
        other = path

    res = other.relative_to(first.resolve())

    # use the first path of the options['paths'] list as cwd
    cwd = Path(evaluator.options.get("paths", ["."])[0])
    try:
        res = f"{res.resolve().relative_to(cwd)}{tail}"
    except ValueError:
        res = f"{res}{tail}"

    # todo: handle windows separators?

    return Literal(f'url("{res}")')


def get_resolver():
    return resolver
