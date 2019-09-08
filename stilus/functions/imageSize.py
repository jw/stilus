from pathlib import Path

from PIL import Image
from bs4 import BeautifulSoup

from stilus.exceptions import StilusError
from stilus.nodes.unit import Unit
from stilus.utils import assert_type, lookup


def _x_and_y_from_svg(path):
    print(path)
    with open(path) as f:
        soup = BeautifulSoup(f, 'lxml')
    width = soup.svg['width']
    height = soup.svg['height']
    return [Unit(width), Unit(height)]


def image_size(img: str, ignore_errors=False, evaluator=None):
    assert_type(img, 'string', 'img')
    p = Path(img.string)
    path = lookup(p, evaluator.paths)
    if p.suffix == '.svg':
        return _x_and_y_from_svg(path)
    if path:
        with Image.open(path) as image:
            x, y = image.size
            return [Unit(x, 'px'), Unit(y, 'px')]
    elif ignore_errors:
        return [Unit(0), Unit(0)]
    else:
        raise StilusError('Could not find image.')
