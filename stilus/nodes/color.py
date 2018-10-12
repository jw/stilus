import colorsys
import copy
import json

from stilus.nodes.boolean import true
from stilus.nodes.node import Node
from stilus.utils import clamp, clamp_alpha, clamp_degrees, clamp_percentage


class HSLA(Node):

    def __init__(self, h, s, l, a):
        super().__init__()
        self.h = clamp_degrees(h)
        self.s = clamp_percentage(s)
        self.l = clamp_percentage(l)
        self.a = clamp_alpha(a)
        self.hsla = self

    def __str__(self):
        return f'hsla({self.h}, {round(self.s)}%, {round(self.l)}%, {self.a})'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, HSLA):
            return self.h == other.h and self.s == other.s and \
                   self.l == other.l and self.a == other.a
        return False

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'HSLA',
                           'h': self.h,
                           's': self.s,
                           'l': self.l,
                           'a': self.a,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})

    def rgba(self):
        return RGBA.from_hsla(self.hsla)

    def __hash__(self):
        return hash(self.__str__())

    def add(self, h, s, l):
        return HSLA(self.h + h,
                    self.s + s,
                    self.l + l,
                    self.a)

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
        (h, s, l) = colorsys.rgb_to_hls(rgba.r / 255,
                                        rgba.g / 255,
                                        rgba.b / 255)
        return HSLA(h * 360, s * 100, l * 100, rgba.a)

    def adjust_lightness(self, percent):
        self.l = clamp_percentage(self.l + self.l * (percent / 100))
        return self

    def adjust_hue(self, degree):
        self.h = clamp_degrees(self.h + degree)
        return self


class RGBA(Node):

    def __init__(self, r, g, b, a):
        super().__init__()
        self.r = clamp(r)
        self.g = clamp(g)
        self.b = clamp(b)
        self.a = clamp_alpha(a)
        self.colorname = ''
        self.rgba = self

    def __str__(self):

        def pad(n):
            return f'{n:02x}'

        if self.colorname == 'transparent':
            return self.colorname

        if 1 == self.a:
            r = pad(self.r)
            g = pad(self.g)
            b = pad(self.b)

            if r[0] == r[1] and g[0] == g[1] and b[0] == b[1]:
                return f'#{r[0]}{g[0]}{b[0]}'
            else:
                return f'#{r}{g}{b}'
        else:
            return f'rgba({self.r}, {self.g}, {self.b}, {self.a:.3f})'

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

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'RGBA',
                           'r': self.r,
                           'g': self.g,
                           'b': self.b,
                           'a': self.a,
                           'raw': self.raw,
                           'name': self.colorname,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})

    def to_boolean(self):
        return true

    def __hash__(self):
        return self.__str__()

    def hsla(self):
        return HSLA.from_rgba(self.rgba)

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
        (r, g, b) = colorsys.hls_to_rgb(hsla.h / 360,
                                        hsla.l / 100,
                                        hsla.s / 100)
        return RGBA(r * 255, g * 255, b * 255, hsla.a)

    def operate(self, op, right: Node):
        """Operate on `right` with given `op`."""
        if op != 'in':
            right = right.first()

        if op == 'is a' and right.name == 'string' and right.string == 'color':
            return true
        elif op == '+':
            if right.name == 'unit':
                n = right.value
                if right.type == '%':
                    return adjust
