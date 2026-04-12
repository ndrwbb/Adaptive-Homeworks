from fractions import Fraction


def normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().replace(",", ".").split())


def try_parse_number(value: str):
    value = normalize_text(value)

    try:
        return Fraction(value)
    except ValueError:
        pass

    try:
        return Fraction(float(value)).limit_denominator()
    except ValueError:
        return None


def check_answer(user_answer: str, correct_answer: str) -> bool:
    user_normalized = normalize_text(user_answer)
    correct_normalized = normalize_text(correct_answer)

    user_number = try_parse_number(user_normalized)
    correct_number = try_parse_number(correct_normalized)

    if user_number is not None and correct_number is not None:
        return user_number == correct_number

    return user_normalized == correct_normalized