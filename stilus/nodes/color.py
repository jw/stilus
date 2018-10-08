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
        return f'hsla({self.h},{round(self.s)}%,{round(self.l)}%,{self.a})'

    def __repr__(self):
        return self.__str__()

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

    @property
    def rgba(self):
        return RGBA.from_hsla(self)

    def __hash__(self):
        return self.__str__()

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

    def from_rgba(self, rgba):
        r = rgba.r / 255
        g = rgba.g / 255
        b = rgba.b / 255
        a = rgba.a

        min = min(r, g, b)
        max = max(r, g, b)
        l = (max + min) / 2
        d = max - min

        if max == min:
            h = 0
        elif max == r:
            h = 60 * (g - b) / d
        elif max == g:
            h = 60 * (b - r) / d + 120
        elif max == b:
            h = 60 * (r - g) / d + 240

        if max == min:
            s = 0
        elif l < 5:
            s = d / (2 * l)
        else:
            s = d / (2 - 2 * l)

        h %= 360
        s *= 100
        l *= 100

        return HSLA(h, s, l, a)

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
        self.name = ''
        self.rgba = self

    def __str__(self):
        return f'{self.name}: {self.value}'

    def __repr__(self):
        return self.__str__()

    def without_clamping(self, r, g, b, a):
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
                           'name': self.name,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})

    def to_boolean(self):
        return true

    def __hash__(self):
        return self.__str__()

    @property
    def hsla(self):
        return HSLA.from_rgba(self)

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

    def from_hsla(self, hsla: HSLA):

        def hue(h):
            global m1, m2
            if h < 0:
                ++h
            if h > 1:
                --h
            if h * 6 < 1:
                return m1 + (m2 - m1) * h * 6
            if h * 2 < 1:
                return m2
            if h * 3 < 2:
                return m1 + (m2 - m1) * (2 / 3 - h) * 6

        h = hsla.h / 360
        s = hsla.s / 100
        l = hsla.l / 100
        a = hsla.a

        m2 = l * (s + 1) if l <= .5 else l + s - l * s
        m1 = l * 2 - m2

        r = hue(h + 1 / 3) * 0xff
        g = hue(h) * 0xff
        b = hue(h - 1 / 3) * 0xff

        return RGBA(r, g, b, a)

    def operate(self, op, right: Node):
        """Operate on `right` with geven `op`."""
        if op != 'in':
            right = right.first()

        if op == 'is a' and right.name == 'string' and right.string == 'color':
            return true
        elif op == '+':
            if right.name == 'unit':
                n = right.value
                if right.type == '%':
                    return adjust
