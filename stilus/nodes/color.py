import colorsys
import json

from stilus.functions.adjust import adjust
from stilus.nodes.string import String
from stilus.nodes.unit import Unit
from stilus.nodes.boolean import true
from stilus.nodes.node import Node
from stilus.utils import clamp, clamp_alpha, clamp_degrees, clamp_percentage


class Color(Node):

    def __init__(self, a):
        super().__init__()
        self.a = clamp_alpha(a)

    def rgba(self):
        pass


class HSLA(Color):

    def __init__(self, h, s, l, a):
        super().__init__(a)
        self.hue = clamp_degrees(h)
        self.saturation = clamp_percentage(s)
        self.lightness = clamp_percentage(l)
        self._hsla = self

    def hsla(self):
        return self._hsla

    def _cleanup(self, value):
        if int(value) == value:
            return int(value)
        else:
            return value

    def __str__(self):
        return f'hsla({self._cleanup(self.hue)},' \
               f'{self._cleanup(round(self.saturation))}%,' \
               f'{self._cleanup(round(self.lightness))}%,' \
               f'{self._cleanup(self.a)})'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, HSLA):
            return self.hue == other.hue and \
                   self.saturation == other.saturation and \
                   self.lightness == other.lightness and \
                   self.a == other.a
        return False

    def clone(self, parent=None, node=Node):
        clone = HSLA(self.hue, self.saturation, self.lightness, self.a)
        clone.lineno = self.lineno
        clone.column = self.column
        clone.filename = self.filename
        return clone

    def to_json(self):
        return json.dumps({'__type': 'HSLA',
                           'h': self.hue,
                           's': self.saturation,
                           'l': self.lightness,
                           'a': self.a,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})

    def rgba(self):
        return RGBA.from_hsla(self._hsla)

    def __hash__(self):
        return hash(self.__str__())

    def hash(self):
        return str(self)

    def add(self, h, s, l):
        return HSLA(self.hue + h,
                    self.saturation + s,
                    self.lightness + l,
                    self.a)

    def sub(self, h, s, l):
        return self.add(-h, -s, -l)

    def operate(self, op, right, value=None):
        """Operate on `right` with the given `op`."""
        if op in ['==', '!=', '<=', '>=', '<', '>', 'is a', '||', '&&']:
            return self.rgba().operate(op, right)
        else:
            return self.rgba().operate(op, right).hsla()

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
        super().__init__(a)
        self.r = clamp(r)
        self.g = clamp(g)
        self.b = clamp(b)
        self.name = ''
        self._rgba = self
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
        return hash(str(self))

    def hash(self):
        return str(self)

    def hsla(self):
        return HSLA.from_rgba(self.rgba())

    def rgba(self):
        return self._rgba

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
        return RGBA(r * 255, g * 255, b * 255, hsla.a)

    def operate(self, op, right: Node, value=None):
        """Operate on `right` with given `op`."""
        if op != 'in':
            right = right.first()
        if op == 'is a' and right.node_name == 'string' \
                and right.string == 'color':
            return true
        elif op == '+':
            if right.node_name == 'unit':
                n = right.value
                if right.type == '%':
                    return adjust(self, String('lightness'), right)
                elif right.type == 'deg':
                    return self.hsla().adjust_hue(n).rgba()
                else:
                    return self.add(n, n, n, 0)
            elif right.node_name == 'rgba':
                return self.add(right.r, right.g, right.b, right.a)
            elif right.node_name == 'hsla':
                return self.hsla().add(right.hue,
                                       right.saturation,
                                       right.lightness)
        elif op == '-':
            if right.node_name == 'unit':
                n = right.value
                if right.type == '%':
                    return adjust(self, String('lightness'), Unit(-n, '%'))
                elif right.type == 'deg':
                    return self.hsla().adjust_hue(-n).rgba()
                else:
                    return self.sub(n, n, n, 0)
            elif right.node_name == 'rgba':
                return self.sub(right.r, right.g, right.b, right.a)
            elif right.node_name == 'hsla':
                return self.hsla().sub(right.hue,
                                       right.saturation,
                                       right.lightness)
        elif op == '*':
            if right.node_name == 'unit':
                return self.multiply(right.value)
        elif op == '/':
            if right.node_name == 'unit':
                return self.divide(right.value)
        return super().operate(op, right)
