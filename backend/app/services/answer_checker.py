from fractions import Fraction
import re


def normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().replace(",", ".").split())


def normalize_answer(answer: str) -> str:
    """Normalize answer for comparison: str → strip → lower → remove spaces → commas to dots."""
    return normalize_text(str(answer)).replace(" ", "")


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


def _split_number_list(value: str) -> list[Fraction] | None:
    """Parse comma/semicolon-separated numeric answers, preserving decimal commas for single numbers."""
    value = str(value).strip().lower()
    if ";" in value:
        parts = [part.strip() for part in value.split(";")]
    elif re.search(r",\s+", value):
        parts = [part.strip() for part in value.split(",")]
    else:
        return None

    numbers = [try_parse_number(part) for part in parts if part]
    if len(numbers) != len([part for part in parts if part]) or len(numbers) < 2:
        return None
    return sorted(numbers)


def check_answer(user_answer: str, correct_answer: str) -> bool:
    user_normalized = normalize_text(user_answer)
    correct_normalized = normalize_text(correct_answer)

    correct_number_list = _split_number_list(correct_answer)
    if correct_number_list is not None:
        user_number_list = _split_number_list(user_answer)
        return user_number_list == correct_number_list

    user_number = try_parse_number(user_normalized)
    correct_number = try_parse_number(correct_normalized)

    if user_number is not None and correct_number is not None:
        return user_number == correct_number

    return user_normalized == correct_normalized
