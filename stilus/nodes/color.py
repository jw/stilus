import colorsys
import json

from stilus.nodes.boolean import true
from stilus.nodes.node import Node
from stilus.utils import clamp, clamp_alpha, clamp_degrees, clamp_percentage


class Color(Node):

    def rgba(self):
        pass


class HSLA(Color):

    def __init__(self, h, s, l, a):
        super().__init__()
        self.hue = clamp_degrees(h)
        self.saturation = clamp_percentage(s)
        self.lightness = clamp_percentage(l)
        self.alpha = clamp_alpha(a)
        self.hsla = self

    def hsla(self):
        return self.hsla

    def __str__(self):
        return f'hsla({self.hue}, {round(self.saturation)}%, ' \
               f'{round(self.lightness)}%, {self.alpha})'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, HSLA):
            return self.hue == other.hue and \
                   self.saturation == other.saturation and \
                   self.lightness == other.lightness and \
                   self.alpha == other.alpha
        return False

    def clone(self, parent=None, node=Node):
        clone = HSLA(self.hue, self.saturation, self.lightness, self.alpha)
        clone.lineno = self.lineno
        clone.column = self.column
        clone.filename = self.filename
        return clone

    def to_json(self):
        return json.dumps({'__type': 'HSLA',
                           'h': self.hue,
                           's': self.saturation,
                           'l': self.lightness,
                           'a': self.alpha,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})

    def rgba(self):
        return RGBA.from_hsla(self.hsla)

    def __hash__(self):
        return hash(self.__str__())

    def hash(self):
        return str(self)

    def add(self, h, s, l):
        return HSLA(self.hue + h,
                    self.saturation + s,
                    self.lightness + l,
                    self.alpha)

    def sub(self, h, s, l):
        return self.add(-h, -s, -l)

    def operate(self, op, right):
        """Operate on `right` with the given `op`."""
        if op in ['==', '!=', '<=', '>=', '<', '>', 'is a', '||', '&&']:
            return self.rgba.operate(op, right)
        else:
            return self.rgba.operate(op, right).hsla

    @staticmethod
    def from_rgba(rgba):
        (h, l, s) = colorsys.rgb_to_hls(rgba.r / 255,
                                        rgba.g / 255,
                                        rgba.b / 255)
        return HSLA(h * 360, s * 100, l * 100, rgba.a)

    def adjust_lightness(self, percent):
        self.lightness = clamp_percentage(self.lightness +
                                          self.lightness * (percent / 100))
        return self

    def adjust_hue(self, degree):
        self.hue = clamp_degrees(self.hue + degree)
        return self


class RGBA(Color):

    def __init__(self, r, g, b, a):
        super().__init__()
        self.r = clamp(r)
        self.g = clamp(g)
        self.b = clamp(b)
        self.a = clamp_alpha(a)
        self.name = ''
        self.rgba = self
        self.raw = None

    def __str__(self):

        def pad(n):
            return f'{n:02x}'

        if self.name == 'transparent':
            return self.name

        if 1 == self.a:
            r = pad(self.r)
            g = pad(self.g)
            b = pad(self.b)

            if r[0] == r[1] and g[0] == g[1] and b[0] == b[1]:
                return f'#{r[0]}{g[0]}{b[0]}'
            else:
                return f'#{r}{g}{b}'
        else:
            alpha = f'{self.a:.3f}'.rstrip('0').rstrip('.')
            return f'rgba({self.r},{self.g},{self.b},{alpha})'

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def without_clamping(r, g, b, a):
        rgba = RGBA(0, 0, 0, 0)
        rgba.r = r
        rgba.g = g
        rgba.b = b
        rgba.a = a
        return rgba

    def clone(self, parent=None, node=None):
        clone = RGBA(self.r, self.g, self.b, self.a)
        clone.raw = self.raw
        clone.name = self.name
        clone.lineno = self.lineno
        clone.column = self.column
        clone.filename = self.filename
        return clone

    def to_json(self):
        return json.dumps({'__type': 'RGBA',
                           'r': self.r,
                           'g': self.g,
                           'b': self.b,
                           'a': self.a,
                           'raw': self.raw,
                           'node_name': self.name,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})

    def to_boolean(self):
        return true

    def __hash__(self):
        return self.__str__()

    def hash(self):
        return str(self)

    def hsla(self):
        return HSLA.from_rgba(self.rgba)

    def rgba(self):
        return self.rgba

    def add(self, r, g, b, a):
        return RGBA(self.r + r,
                    self.g + g,
                    self.b + b,
                    self.a + a)

    def sub(self, r, g, b, a):
        return RGBA(self.r - r,
                    self.g - g,
                    self.b - b,
                    self.a if a == 1 else self.a - a)

    def multiply(self, n):
        return RGBA(self.r * n,
                    self.g * n,
                    self.b * n,
                    self.a)

    def divide(self, n):
        return RGBA(self.r / n,
                    self.g / n,
                    self.b / n,
                    self.a)

    def __eq__(self, other):
        if isinstance(other, RGBA):
            return self.r == other.r and \
                   self.g == other.g and \
                   self.b == other.b
        return False

    @staticmethod
    def from_hsla(hsla: HSLA):
        (r, g, b) = colorsys.hls_to_rgb(hsla.hue / 360,
                                        hsla.lightness / 100,
                                        hsla.saturation / 100)
        return RGBA(r * 255, g * 255, b * 255, hsla.alpha)

    # todo: implement me!
    def operate(self, op, right: Node, value=None):
        """Operate on `right` with given `op`."""
        if op != 'in':
            right = right.first()
        if op == 'is a' and right.node_name == 'string' \
                and right.string == 'color':
            return true
        elif op == '+':
            if right.node_name == 'unit':
                if right.type == '%':
                    pass
        raise NotImplementedError
