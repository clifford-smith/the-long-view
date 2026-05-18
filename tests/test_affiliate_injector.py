from monetization.affiliate_injector import inject_affiliates


def test_inject_bookshop_for_book_content():
    text = "Today we discussed a fascinating book about medieval history."
    affiliates = {"bookshop": "https://bookshop.org/affiliate/longview"}
    result = inject_affiliates(text, affiliates)
    assert "bookshop.org" in result


def test_inject_brilliant_for_science_content():
    text = "The mathematics of music involves fascinating probability theory."
    affiliates = {"brilliant": "https://brilliant.org/longview"}
    result = inject_affiliates(text, affiliates)
    assert "brilliant.org" in result


def test_no_injection_when_no_match():
    text = "General conversation about culture and art."
    affiliates = {"bookshop": "https://bookshop.org/affiliate/longview"}
    result = inject_affiliates(text, affiliates)
    assert "bookshop.org" not in result


def test_inject_skips_empty_affiliates():
    text = "We read a great book today."
    result = inject_affiliates(text, {})
    assert result == text
