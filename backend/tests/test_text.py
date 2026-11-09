from app.services.ai.text import clean_quote, normalize_hashtags, quote_fingerprint


def test_clean_quote_strips_wrapping_and_attribution():
    assert clean_quote('  "Know thyself." — Socrates ') == "Know thyself."
    assert clean_quote("1. “Waste no more time.”") == "Waste no more time."


def test_clean_quote_keeps_inner_dash_clauses():
    text = "The mind is everything - what you think, you become."
    assert clean_quote(text) == text


def test_fingerprint_ignores_case_and_punctuation():
    assert quote_fingerprint("Know, thyself!") == quote_fingerprint("know thyself")


def test_normalize_hashtags():
    tags = normalize_hashtags(["#Stoicism", "stoicism", "#inner peace", "#wisdom,#Focus"])
    assert tags == ["#Stoicism", "#inner", "#peace", "#wisdom", "#Focus"]
