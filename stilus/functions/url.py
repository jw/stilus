import base64
import logging
from pathlib import Path
from urllib.parse import urlparse

from stilus import utils
from stilus.nodes.literal import Literal
from stilus.visitor.compiler import Compiler

default_mimes = {
    '.gif': 'image/gif',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.svg': 'image/svg+xml',
    '.webp': 'image/webp',
    '.ttf': 'application/x-font-ttf',
    '.eot': 'application/vnd.ms-fontobject',
    '.woff': 'application/font-woff',
    '.woff2': 'application/font-woff2'
}


encoding_types = {
    'BASE_64': 'base64',
    'UTF8': 'UTF-8'
}


def url(options, evaluator=None):
    o = {}
    if options:
        o = options

    _paths = o.get('paths', [])
    size_limit = o.get('limit', 30000)
    mimes = o.get('mimes', default_mimes)

    def fn(url, enc=None):
        compiler = Compiler(url, {})
        url = ''
        for u in url.nodes:
            url += compiler.visit(u)

        # parse the url
        url = urlparse(url)
        ext = Path(url.path).suffix
        mime = mimes[ext]
        hash = url.frag
        literal = Literal(f'url("{url.geturl()}"')
        if evaluator:
            paths = _paths.extend(evaluator.paths)

        # not mime or absolute
        if not mime or not url.protocol:
            return literal

        # lookup
        found = utils.lookup(url.path, paths)
        if not found:
            # todo: add event management
            logging.warning(f'File not found; File {literal} could not be '
                            f'found, literal url retained!')
            return literal

        # read the url as a utf-8 string
        buf = ''
        if enc and enc.first().value.lower() == 'utf8':
            encoding = 'UTF-8'
            with open(found, 'r', encoding=encoding) as f:
                buf = f.read()
        else:
            encoding = 'base64'
            with open(found, 'r', encoding=encoding) as f:
                data = f.read()
                buf = base64.b64decode(data) + hash

        # too large
        if size_limit and len(buf) > size_limit:
            return literal

        return Literal(f'url("data:{mime};{encoding},{buf}")')

    return fn
