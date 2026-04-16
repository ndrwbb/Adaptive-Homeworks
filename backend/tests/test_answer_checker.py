import unittest

from app.services.answer_checker import check_answer, normalize_answer


class AnswerCheckerTests(unittest.TestCase):
    # normalize_answer

    def test_normalize_answer_strips_and_lowers(self):
        self.assertEqual(normalize_answer("  Hello World  "), "helloworld")

    def test_normalize_answer_replaces_commas(self):
        self.assertEqual(normalize_answer("3,14"), "3.14")

    # check_answer: strings

    def test_check_answer_exact_match(self):
        self.assertTrue(check_answer("yes", "yes"))

    def test_check_answer_case_insensitive(self):
        self.assertTrue(check_answer("Yes", "yes"))

    def test_check_answer_extra_spaces(self):
        self.assertTrue(check_answer(" 6 ", "6"))

    def test_check_answer_wrong_string(self):
        self.assertFalse(check_answer("abc", "xyz"))

    # check_answer: numbers

    def test_check_answer_integers(self):
        self.assertTrue(check_answer("42", "42"))

    def test_check_answer_float_vs_int(self):
        self.assertTrue(check_answer("6.0", "6"))

    def test_check_answer_comma_decimal(self):
        self.assertTrue(check_answer("0,5", "0.5"))

    def test_check_answer_wrong_number(self):
        self.assertFalse(check_answer("7", "6"))

    # check_answer: fractions

    def test_fraction_half(self):
        self.assertTrue(check_answer("1/2", "0.5"))

    def test_fraction_two_fifths(self):
        self.assertTrue(check_answer("2/5", "0.4"))

    def test_fraction_answers(self):
        """Original test preserved for backwards compatibility."""
        self.assertTrue(check_answer("1/2", "0.5"))
        self.assertTrue(check_answer("0,5", "0.5"))
        self.assertTrue(check_answer("6.0", "6"))
        self.assertTrue(check_answer(" 6 ", "6"))

    def test_wrong_answers(self):
        self.assertFalse(check_answer("7", "6"))

    # check_answer: multiple numeric answers

    def test_multiple_numeric_answers_accept_same_order(self):
        self.assertTrue(check_answer("2, 3", "2, 3"))

    def test_multiple_numeric_answers_accept_reordered_values(self):
        self.assertTrue(check_answer("3, 2", "2, 3"))

    def test_multiple_numeric_answers_accept_semicolons(self):
        self.assertTrue(check_answer("3; 2", "2, 3"))

    def test_multiple_numeric_answers_reject_missing_value(self):
        self.assertFalse(check_answer("2", "2, 3"))
