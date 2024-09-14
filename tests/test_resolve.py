from bibmancli import resolve


def test_resolve_identifier():
    identifier = "10.1002/andp.19053221004"
    response = resolve.resolve_identifier(identifier, 5.0)
    assert response["author"] == "Einstein, A."
    assert response["ENTRYTYPE"] == "article"
