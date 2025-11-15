"""Tests for lm_score function."""

import unittest
from lm_score.lm_score import lm_score


class TestLmScore(unittest.TestCase):
    """Tests for lm_score function."""

    def test_lm_score_basic(self):
        """Test basic lm_score with content and question."""
        content = "This is an invoice for $100. Payment is due by February 1st."
        question = "Is this about billing or payments?"

        score = lm_score(content, question)

        # Should return an integer between 1 and 10
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 1)
        self.assertLessEqual(score, 10)

    def test_lm_score_multiple_fields(self):
        """Test lm_score with multiple content fields."""
        subject = "Invoice #12345"
        body = "Your payment of $50 is due."
        question = "Is this about billing?"

        score = lm_score(subject, body, question)

        # Should return an integer between 1 and 10
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 1)
        self.assertLessEqual(score, 10)

    def test_lm_score_yes_question(self):
        """Test lm_score with clearly affirmative content."""
        content = "Yes, this is definitely about payments and billing."
        question = "Is this about billing?"

        score = lm_score(content, question)

        # Should return high score (7-10) for clearly affirmative content
        self.assertGreaterEqual(score, 7)

    def test_lm_score_no_question(self):
        """Test lm_score with clearly negative content."""
        content = "This email is about scheduling a meeting for next week."
        question = "Is this about billing or payments?"

        score = lm_score(content, question)

        # Should return low score (1-4) for clearly negative content
        self.assertLessEqual(score, 4)


if __name__ == "__main__":
    unittest.main()
