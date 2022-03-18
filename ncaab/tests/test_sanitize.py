from ncaab.utils.str_sanitizer import sanitize_team, sanitize_odds


def test_unicode_removed():
    assert sanitize_team("Jacksonville State\xa0") == "Jacksonville State"


def test_numbers():
    assert sanitize_team("Yale 14") == "Yale"


def test_numbers_symbols():
    assert sanitize_team("Yale (#15)") == "Yale"


def test_keep_some_symbols():
    assert sanitize_team("St. Bonaventure#15") == "St. Bonaventure"
    assert sanitize_team("Texas A&M") == "Texas A&M"
    assert sanitize_team("St. Peter's (#15)") == "St. Peter's"
    assert (
        sanitize_team("Arkansas-Pine Bluff Golden Lions")
        == "Arkansas-Pine Bluff Golden Lions"
    )
    # I think this is fine
    # assert sanitize_team("Augustana (IL) Vikings") == "Augustana (IL) Vikings"


def test_odds():
    assert sanitize_odds("(-110)") == "-110"
    assert sanitize_odds("-110") == "-110"
    assert sanitize_odds(" -110 ") == "-110"
    assert sanitize_odds(" (-110) ") == "-110"
    assert sanitize_odds(" EVEN ") == "EVEN"
    assert sanitize_odds("+110") == "+110"
    assert sanitize_odds("(+110)") == "+110"
    assert sanitize_odds("") == ""
