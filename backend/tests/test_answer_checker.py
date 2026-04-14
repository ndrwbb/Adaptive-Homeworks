from app.services.answer_checker import check_answer, normalize_answer


# ── normalize_answer ────────────────────────────────────────────

def test_normalize_answer_strips_and_lowers():
    assert normalize_answer("  Hello World  ") == "helloworld"


def test_normalize_answer_replaces_commas():
    assert normalize_answer("3,14") == "3.14"


# ── check_answer: strings ──────────────────────────────────────

def test_check_answer_exact_match():
    assert check_answer("yes", "yes")


def test_check_answer_case_insensitive():
    assert check_answer("Yes", "yes")


def test_check_answer_extra_spaces():
    assert check_answer(" 6 ", "6")


def test_check_answer_wrong_string():
    assert not check_answer("abc", "xyz")


# ── check_answer: numbers ──────────────────────────────────────

def test_check_answer_integers():
    assert check_answer("42", "42")


def test_check_answer_float_vs_int():
    assert check_answer("6.0", "6")


def test_check_answer_comma_decimal():
    assert check_answer("0,5", "0.5")


def test_check_answer_wrong_number():
    assert not check_answer("7", "6")


# ── check_answer: fractions ────────────────────────────────────

def test_fraction_half():
    assert check_answer("1/2", "0.5")


def test_fraction_two_fifths():
    assert check_answer("2/5", "0.4")


def test_fraction_answers():
    """Original test preserved for backwards compat."""
    assert check_answer("1/2", "0.5")
    assert check_answer("0,5", "0.5")
    assert check_answer("6.0", "6")
    assert check_answer(" 6 ", "6")


def test_wrong_answers():
    assert not check_answer("7", "6")