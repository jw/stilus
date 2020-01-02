import base64
import logging
import re
import urllib
from pathlib import Path
from urllib.parse import urlparse

from stilus import utils
from stilus.nodes.literal import Literal
from stilus.visitor.compiler import Compiler

default_mimes = {
    ".gif": "image/gif",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
    ".ttf": "application/x-font-ttf",
    ".eot": "application/vnd.ms-fontobject",
    ".woff": "application/font-woff",
    ".woff2": "application/font-woff2",
}


encoding_types = {"BASE_64": "base64", "UTF8": "UTF-8"}


# todo: rewrite this; this is terrible!
# todo: this should be linked with the resolver?
# note: this is called by the 'embedurl' builtin function.
# todo: docstring this!
def url(url, enc=None, evaluator=None):
    _paths = evaluator.options.get("paths", [])
    size_limit = evaluator.options.get("limit", 30000)
    mimes = evaluator.options.get("mimes", default_mimes)

    def fn(url, enc=None):
        compiler = Compiler(url, {})
        url = compiler.visit(url)

        # parse the url
        url = urlparse(url[1:-1])
        ext = Path(url.path).suffix
        mime = None
        if ext and ext in mimes:
            mime = mimes[ext]
        hash = ""
        if url.fragment:
            hash = f"#{url.fragment}"
        literal = Literal(f'url("{url.geturl()}")')

        # not mime or absolute
        if not mime or url.scheme:
            return literal

        # lookup
        found = utils.lookup(url.path, _paths)
        if not found:
            # todo: add event management
            logging.warning(
                f"File not found; File {literal} could not be "
                f"found, literal url retained!"
            )
            return literal

        # read the url as a binary
        buf = open(found, "rb").read()

        # too large?
        if size_limit and len(buf) > size_limit:
            return literal

        if enc and enc.first().value.lower() == "utf8":
            encoding = "charset=utf-8"
            buf = re.sub(r"\s+", " ", buf.decode("utf-8"))
            result = urllib.parse.quote(buf, safe=" ?=:/").strip()
        else:
            encoding = "base64"
            result = f'{base64.b64encode(buf).decode("utf-8")}{hash}'

        return Literal(f'url("data:{mime};{encoding},{result}")')

    return fn(url, enc)
