from stilus.functions.match import match
from stilus.nodes.null import null
from stilus.nodes.string import String


def test_match():
    result = match(
        String("^(height|width)?([<>=]{1,})(.*)"), String("height>=1024px")
    )
    assert result == ["height>=1024px", "height", ">=", "1024px"]

    result = match(String("^foo(?:bar)?"), String("foo"))
    assert result == ["foo"]

    result = match(String("^foo(?:bar)?"), String("foobar"))
    assert result == ["foobar"]

    result = match(String("^foo(?:bar)?"), String("bar"))
    assert result == null

    result = match(
        String("ain"), String("The rain in SPAIN stays mainly in the plain")
    )
    assert result == ["ain"]

    result = match(
        String("ain"),
        String("The rain in SPAIN stays mainly in the plain"),
        String("g"),
    )
    assert result == ["ain", "ain", "ain"]

    result = match(
        String("ain"),
        String("The rain in SPAIN stays mainly in the plain"),
        String("ig"),
    )
    assert result == ["ain", "AIN", "ain", "ain"]
