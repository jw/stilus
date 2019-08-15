from stilus.nodes.color import HSLA, RGBA


def test_hsla():
    hsla = HSLA(100, 100, 100, 0)
    assert hsla.node_name == 'hsla'
    assert hsla.hue == 100
    assert hsla.saturation == 100
    assert hsla.lightness == 100
    assert hsla.a == 0


def test_hsla_clamping_string():
    hsla = HSLA(500, 120, 90, 3)
    assert hsla.node_name == 'hsla'
    assert hsla.hue == 140  # 500 - 360
    assert hsla.saturation == 100
    assert hsla.lightness == 90
    assert hsla.a == 1
    assert str(hsla) == 'hsla(140, 100%, 90%, 1)'
    hsla = HSLA(-10, -20, 0, 0.3)
    assert hsla.node_name == 'hsla'
    assert hsla.hue == 350  # 360 - 10
    assert hsla.saturation == 0
    assert hsla.lightness == 0
    assert hsla.a == 0.3
    assert str(hsla) == 'hsla(350, 0%, 0%, 0.3)'
    hsla = HSLA(42, 42, 42, -42.42)
    assert hsla.node_name == 'hsla'
    assert hsla.hue == 42
    assert hsla.saturation == 42
    assert hsla.lightness == 42
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
    assert hsla == HSLA(105, 42, 11, 0)
    hsla.adjust_lightness(99)
    hsla.adjust_hue(300)
    assert hsla == HSLA(45, 42, 21.89, 0)


def test_hsla_rgba():
    hsla = HSLA(42, 42, 42, -42.42)
    assert hsla.rgba() == RGBA(152, 125, 62, 0.000)


def test_hsla_hash():
    hsla = HSLA(500, 120, 90, 3)
    assert hsla.hash() == 'hsla(140, 100%, 90%, 1)'
    hsla = HSLA(-10, -20, 0, 0.3)
    assert hsla.hash() == 'hsla(350, 0%, 0%, 0.3)'
    hsla = HSLA(42, 42, 42, -42.42)
    assert hsla.hash() == 'hsla(42, 42%, 42%, 0)'


def test_rgba():
    rgba = RGBA(100, 100, 100, 0)
    assert rgba.r == 100
    assert rgba.g == 100
    assert rgba.b == 100
    assert rgba.a == 0
    assert rgba.node_name == 'rgba'


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
    assert str(rgba) == 'rgba(0,0,0,0.42)'
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
    assert str(rgba) == 'rgba(300,300,300,0.003)'


def test_rgba_hash():
    rgba = RGBA.without_clamping(300, 300, 300, 0.003)
    assert rgba.hash() == 'rgba(300,300,300,0.003)'
    rgba = RGBA(300, 300, 300, 42)
    assert rgba.hash() == '#fff'
