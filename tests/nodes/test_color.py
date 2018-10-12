from stilus.nodes.color import HSLA, RGBA


def test_hsla():
    hsla = HSLA(100, 100, 100, 0)
    assert hsla.name == 'hsla'
    assert hsla.h == 100
    assert hsla.s == 100
    assert hsla.l == 100
    assert hsla.a == 0


def test_hsla_clamping_string():
    hsla = HSLA(500, 120, 90, 3)
    assert hsla.name == 'hsla'
    assert hsla.h == 140  # 500 - 360
    assert hsla.s == 100
    assert hsla.l == 90
    assert hsla.a == 1
    assert str(hsla) == 'hsla(140, 100%, 90%, 1)'
    hsla = HSLA(-10, -20, 0, 0.3)
    assert hsla.name == 'hsla'
    assert hsla.h == 350  # 360 - 10
    assert hsla.s == 0
    assert hsla.l == 0
    assert hsla.a == 0.3
    assert str(hsla) == 'hsla(350, 0%, 0%, 0.3)'
    hsla = HSLA(42, 42, 42, -42.42)
    assert hsla.name == 'hsla'
    assert hsla.h == 42
    assert hsla.s == 42
    assert hsla.l == 42
    assert hsla.a == 0
    assert str(hsla) == 'hsla(42, 42%, 42%, 0)'


def test_hsla_add_and_sub():
    hsla = HSLA(42, 42, 42, -42.42)
    assert hsla.add(42, 42, 42) == HSLA(84, 84, 84, 0)
    hsla = HSLA(42, 42, 42, -42.42)
    assert hsla.sub(21, 21, 21) == HSLA(21, 21, 21, 0)


def test_hsla_adjust_lightness_and_hue():
    hsla = HSLA(100, 42, 10, 0)
    hsla.adjust_lightness(10)
    hsla.adjust_hue(5)
    print(hsla)
    assert hsla == HSLA(105, 42, 11, 0)
    hsla.adjust_lightness(99)
    hsla.adjust_hue(300)
    print(hsla)
    assert hsla == HSLA(45, 42, 21.89, 0)


def test_hsla_rgba():
    hsla = HSLA(42, 42, 42, -42.42)
    assert hsla.rgba() == RGBA(152, 125, 62, 0.000)


def test_rgba():
    rgba = RGBA(100, 100, 100, 0)
    assert rgba.r == 100
    assert rgba.g == 100
    assert rgba.b == 100
    assert rgba.a == 0
    assert rgba.name == 'rgba'


def test_rbga_clamping_and_string():
    rgba = RGBA(300, 300, 300, 42)
    assert rgba.r == 255
    assert rgba.g == 255
    assert rgba.b == 255
    assert rgba.a == 1
    assert str(rgba) == '#fff'
    rgba = RGBA(-30, 0, -60, 0.42)
    assert rgba.r == 0
    assert rgba.g == 0
    assert rgba.b == 0
    assert rgba.a == 0.42
    assert str(rgba) == 'rgba(0, 0, 0, 0.420)'
    rgba = RGBA(-30, 0, -60, 0.42)
    assert rgba.r == 0
    assert rgba.g == 0
    assert rgba.b == 0
    assert rgba.a == 0.42


def test_rbga_no_clamping():
    rgba = RGBA.without_clamping(300, 300, 300, 0.003)
    assert rgba.r == 300
    assert rgba.g == 300
    assert rgba.b == 300
    assert rgba.a == 0.003
    assert str(rgba) == 'rgba(300, 300, 300, 0.003)'


def test_rgba_hsla():
    rgba = RGBA(152, 125, 62, 0.000)
    assert rgba.hsla() == HSLA(41.99999999999999, 42, 42, -42.42)
