"""Tests for lm_score function."""

import unittest
from lm_score.lm_score import lm_score


class TestLmScore(unittest.TestCase):
    """Tests for lm_score function."""
    def test_lm_score_meeting_scheduling(self):
        """Test lm_score with meeting/scheduling content from benchmark."""
        subject = "Meeting reminder: Q1 Planning"
        body = "This is a reminder about our Q1 planning meeting scheduled for next Tuesday at 2pm."
        question = "Is this email about meetings or scheduling?"

        try:
            score = lm_score(subject, body, question)
        except Exception as e:
            print("Make sure the server is running! before running tests!")
            raise e

        # Should return score > 5 for clearly meeting-related content
        self.assertGreater(score, 5)

    def test_lm_score_welcome_not_billing(self):
        """Test lm_score with welcome email that is not about billing."""
        subject = "Welcome to our service"
        body = "Thank you for signing up! We're excited to have you on board. Please verify your email address to get started."
        question = "Is this email about billing or payments?"

        try:
            score = lm_score(subject, body, question)
        except Exception as e:
            print("Make sure the server is running! before running tests!")
            raise e

        # Should return score < 5 for clearly non-billing content
        self.assertLess(score, 5)

    def test_lm_score_yes_question(self):
        """Test lm_score with clearly affirmative content."""
        content = "Yes, this is definitely about payments and billing."
        question = "Is this about billing?"

        score = lm_score(content, question)

        # Should return high score (7-10) for clearly affirmative content
        self.assertGreaterEqual(score, 7)

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

    # Corner case tests
    def test_lm_score_empty_content(self):
        """Test lm_score with empty content string."""
        content = ""
        question = "Is this about billing?"

        score = lm_score(content, question)

        # Should still return a valid score
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 10)

    def test_lm_score_whitespace_content(self):
        """Test lm_score with only whitespace content."""
        content = "   \n\t  "
        question = "Is this urgent?"

        score = lm_score(content, question)

        # Should still return a valid score
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 10)

    def test_lm_score_none_values(self):
        """Test lm_score with None values in content."""
        subject = "Invoice"
        body = None
        question = "Is this about billing?"

        score = lm_score(subject, body, question)

        # Should handle None gracefully and return valid score
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 10)

    def test_lm_score_multiple_none_values(self):
        """Test lm_score with multiple None values."""
        score = lm_score(None, None, "Is this important?")

        # Should handle multiple None values
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 10)

    def test_lm_score_insufficient_arguments(self):
        """Test lm_score with insufficient arguments."""
        with self.assertRaises(TypeError):
            lm_score("only one argument")

    def test_lm_score_no_arguments(self):
        """Test lm_score with no arguments."""
        with self.assertRaises(TypeError):
            lm_score()

    def test_lm_score_very_long_content(self):
        """Test lm_score with very long content."""
        content = "This is a test. " * 500  # ~7500 characters
        question = "Is this repetitive?"

        score = lm_score(content, question)

        # Should handle long content
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 10)

    def test_lm_score_special_characters(self):
        """Test lm_score with special characters and unicode."""
        content = "Café résumé: $1,000.50 due by 12/31! @user #invoice 💰"
        question = "Is this about payments?"

        score = lm_score(content, question)

        # Should handle special characters
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 10)

    def test_lm_score_numeric_content(self):
        """Test lm_score with numeric content fields."""
        amount = 12345
        customer_id = 67890
        question = "Is this a large amount?"

        score = lm_score(amount, customer_id, question)

        # Should convert numbers to strings and score
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 10)

    def test_lm_score_very_short_content(self):
        """Test lm_score with minimal content."""
        content = "Hi"
        question = "Is this a greeting?"

        score = lm_score(content, question)

        # Should handle very short content
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 10)

    def test_lm_score_question_without_question_mark(self):
        """Test lm_score with question missing question mark."""
        content = "Please pay your invoice of $100"
        question = "Is this about billing"  # No question mark

        score = lm_score(content, question)

        # Should still work without question mark
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 10)

    def test_lm_score_mixed_content_types(self):
        """Test lm_score with mixed content types."""
        content1 = "Subject: Invoice"
        content2 = 12345
        content3 = None
        content4 = True
        question = "Is this about an invoice?"

        score = lm_score(content1, content2, content3, content4, question)

        # Should handle mixed types
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 10)

    def test_lm_score_newlines_and_tabs(self):
        """Test lm_score with content containing newlines and tabs."""
        content = "Line 1\n\tLine 2 with tab\n\n\nLine 3 after blank lines"
        question = "Does this have multiple lines?"

        score = lm_score(content, question)

        # Should handle formatting characters
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 10)


if __name__ == "__main__":
    unittest.main()
