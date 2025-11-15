"""LM_SCORE: SQL function for semantic scoring using language models."""

import os
import sqlite3
from dotenv import load_dotenv
import dspy
import argparse
from dspy.predict import aggregation
import statistics

# Load environment variables
load_dotenv()

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8080")
API_TOKEN = os.getenv("API_TOKEN", "")

# Configure DSPy
lm = dspy.LM(
    model="openai/mlx-community/DeepSeek-R1-Distill-Qwen-7B-4bit",
    api_base=SERVER_URL,
    api_key=API_TOKEN,
    max_tokens=2000,
    temperature=0.7,  # Higher temperature for diversity in ensemble
    cache=False  # for benchmarking reproducibility
)
dspy.settings.configure(lm=lm, track_usage=True)


class LMScorer(dspy.Module):
    """Basic LM scorer with single prediction.

    This scorer makes a single call to the language model to evaluate content
    based on a question. It's faster but less robust than the EnsembleScorer.

    Attributes:
        predictor: DSPy Predict module configured for question-to-answer mapping
    """

    def __init__(self):
        """Initialize the LMScorer with a DSPy predictor."""
        super().__init__()
        self.predictor = dspy.Predict("question -> answer: int")

    def forward(self, question: str) -> dspy.Prediction:
        """Score content based on a question.

        Args:
            question: A yes/no question to evaluate

        Returns:
            Integer score from the language model
        """
        response = self.predictor(question=question)
        return response

class EnsembleScorer(dspy.Module):
    """Ensemble LM scorer with majority voting across multiple predictions.

    This scorer makes k independent predictions and returns the most common result
    (mode) to improve reliability. If predictions fail, they default to a neutral
    score of 5. This approach provides more robust results at the cost of increased
    latency and API calls.

    Attributes:
        k: Number of independent predictions to make (default: 3)
        predictor: DSPy Predict module configured for question-to-answer mapping

    Example:
        >>> scorer = EnsembleScorer(k=5)
        >>> result = scorer(question="Is this content about billing?")
    """

    def __init__(self, k: int = 3):
        """Initialize the ensemble scorer.

        Args:
            k: Number of parallel predictions to make for majority voting.
               Higher values increase robustness but also latency. Default is 3.
        """
        super().__init__()
        self.k = k
        self.predictor = dspy.Predict("question -> answer: int")

    def forward(self, question: str) -> dspy.Prediction:
        """Score content using ensemble majority voting.

        Makes k independent predictions and returns the most frequently occurring
        score (mode). Failed predictions default to a neutral score of 5.

        Args:
            question: A yes/no question with scoring instructions

        Returns:
            Integer score that appears most frequently across k predictions
        """
        scores = []
        for _ in range(self.k):
            try:
                p = self.predictor(question=question)
                scores.append(p.answer)
                
            except Exception:
                scores.append(5)
        return dspy.Prediction(answer=sum(scores) // self.k)
        # return dspy.Prediction(answer=max(set(scores), key=scores.count))

# Use ensemble scorer with 3 parallel predictions
lm_scorer = LMScorer()

def lm_score(*args) -> int:
    """Score content based on a yes/no question using a language model.

    This function can be used as a SQLite user-defined function to semantically
    evaluate database content.

    Args:
        *args: Variable number of arguments where:
            - All arguments except the last are content fields from the database
            - The last argument is a yes/no question

    Returns:
        Integer score from 1 to 10, where:
        - 10 = strongly yes
        - 1 = strongly no
        - 5-6 = uncertain/neutral

    Example:
        SELECT email, subject,
               LM_SCORE(subject, body, 'Is this about billing?') as score
        FROM emails
        WHERE LM_SCORE(subject, body, 'Is this about billing?') > 7;
    """
    if len(args) < 2:
        raise TypeError("lm_score() requires at least 2 arguments: content and question")

    # Last argument is the question, everything else is content
    question = args[-1]
    content_parts = args[:-1]

    # Combine content parts
    content = " ".join(str(part) for part in content_parts if part is not None)

    prompt = f"""Based on the following content, answer this yes/no question: {question}

Content: {content}

Provide a score from 0 to 10 based on your confidence in the answer:
- 10 = strongly yes, definitely true
- 7-9 = probably yes, likely true
- 5-6 = uncertain, could go either way
- 3-4 = probably no, likely false
- 0-2 = strongly no, definitely false

Provide only a single number from 0 to 10.
Score:"""
    try: 
        response = lm_scorer(question=prompt)
    except Exception as e:
        print(f"Warning: {e}")
        return 5
    print(response.get_lm_usage())
    return response.answer

def register_lm_score_function(conn: sqlite3.Connection) -> None:
    """Register the LM_SCORE function with a SQLite connection.

    This function registers lm_score() as a SQL user-defined function that can
    be called from SQL queries. The function accepts a variable number of arguments
    (-1 in SQLite terminology).

    Args:
        conn: SQLite database connection to register the function with

    Example:
        >>> conn = sqlite3.connect('data.db')
        >>> register_lm_score_function(conn)
        >>> cursor = conn.cursor()
        >>> cursor.execute("SELECT LM_SCORE(text, 'Is this urgent?') FROM messages")
    """
    conn.create_function("LM_SCORE", -1, lm_score)  # -1 means variable number of arguments


def get_connection(db_path: str = "company.db") -> sqlite3.Connection:
    """Get a database connection with LM_SCORE function registered.

    This is a convenience function that creates a SQLite connection and
    automatically registers the LM_SCORE user-defined function, so you can
    immediately start using semantic queries.

    Args:
        db_path: Path to the SQLite database file. Defaults to "company.db".
                Creates the file if it doesn't exist.

    Returns:
        SQLite connection object with LM_SCORE function ready to use

    Example:
        >>> conn = get_connection('emails.db')
        >>> cursor = conn.cursor()
        >>> cursor.execute('''
        ...     SELECT subject, LM_SCORE(subject, body, 'Is this spam?') as score
        ...     FROM emails WHERE score > 7
        ... ''')
    """
    conn = sqlite3.connect(db_path)
    register_lm_score_function(conn)
    return conn


if __name__ == "__main__":
    print("LM_SCORE module loaded successfully.")
    print("Use get_connection() to create a database connection with LM_SCORE registered.")
    parser = argparse.ArgumentParser()
    parser.add_argument("--cot", description="Whether to use ChainOfThought instead of Prediction")
    parser.add_argument("--k", description="Number of parallel threads")


