from app.services.answer_checker import check_answer


def test_fraction_answers():
    assert check_answer("1/2", "0.5")
    assert check_answer("0,5", "0.5")
    assert check_answer("6.0", "6")
    assert check_answer(" 6 ", "6")


def test_wrong_answers():
    assert not check_answer("7", "6")