"""Benchmark LM_SCORE function on company.db."""

from lm_score.lm_score import get_connection, lm_score, lm
import argparse
import time
import json
import os
import dspy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure LM-as-judge with separate server
JUDGE_SERVER_URL = os.environ["LM_AS_JUDGE_SERVER_URL"]
JUDGE_API_TOKEN = os.environ["LM_AS_JUDGE_API_TOKEN"]
JUDGE_MODEL = os.environ["JUDGE_MODEL"]
MODEL = os.environ["MODEL"]

judge_lm = dspy.LM(
    model=JUDGE_MODEL,
    api_base=JUDGE_SERVER_URL,
    api_key=JUDGE_API_TOKEN,
    max_tokens=16000,
    temperature=None,
    cache=False
)


class LMJudge(dspy.Module):
    """Judge LM_SCORE outputs for reasonableness."""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict("question, content, score -> judgment: str, explanation: str")
        self.predictor.lm = judge_lm

    def forward(self, question: str, content: str, score: int) -> dspy.Prediction:
        """Evaluate if the LM_SCORE output is reasonable.

        Args:
            question: The yes/no question asked
            content: The content being evaluated
            score: The score (0-10) given by LM_SCORE

        Returns:
            Prediction with judgment ('reasonable' or 'unreasonable') and explanation
        """
        prompt = f"""Evaluate if this LM_SCORE output is reasonable.

Question: {question}
Content: {content}
Score Given: {score}/10

A score of 10 means "strongly yes", 5-6 means "uncertain", and 0 means "strongly no".

Is this score reasonable for the given question and content?
Respond with 'reasonable' or 'unreasonable' and provide a brief explanation.

Judgment (reasonable/unreasonable):"""

        response = self.predictor(question=prompt, content=content, score=score)
        return response


judge = LMJudge()


def evaluate_single_item(content_parts: list, question: str, description: str, item_info: dict) -> dict:
    """Evaluate a single item with LM_SCORE, LM-as-judge, and human evaluation.

    Args:
        content_parts: List of content strings to evaluate
        question: The yes/no question to ask
        description: Description of what's being evaluated (e.g., "Email: john@example.com")
        item_info: Dictionary with additional info to display (e.g., {"Subject": "Meeting"})

    Returns:
        Dictionary with all evaluation results
    """
    # Prepare inputs
    content = "\n".join(str(part) for part in content_parts if part is not None)

    # Build the full prompt that lm_score will use
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

    # Time the LM_SCORE call and track tokens
    start_time = time.time()
    from lm_score.lm_score import lm_scorer
    response = lm_scorer(question=prompt)
    score = response.answer
    elapsed_time = time.time() - start_time

    # Get token usage from the response
    usage = response.get_lm_usage()
    total_tokens = usage[MODEL]['completion_tokens'] if usage else 0

    # Display the result
    print(f"\nContent being evaluated:")
    print(f"{content}")
    print(f"\nQuestion: {question}")
    print(f"LM_SCORE Output: {score}/10")
    print(f"Time: {elapsed_time:.2f}s | Tokens: {total_tokens}")

    # Get LM-as-judge evaluation
    print("\nQuerying LM-as-judge...")
    judge_response = judge(question=question, content=content, score=score)

    # Parse judge response
    judge_judgment = getattr(judge_response, 'judgment', 'unknown')
    judge_explanation = getattr(judge_response, 'explanation', 'No explanation')

    print(f"LM-as-judge: {judge_judgment}")
    print(f"Explanation: {judge_explanation}")

    # Get human evaluation
    while True:
        human_eval = input("\nIs this score reasonable? (y/n): ").strip().lower()
        if human_eval in ['y', 'n']:
            break
        print("Please enter 'y' or 'n'")

    human_reasonable = human_eval == 'y'

    print("-" * 80)

    # Return structured result
    return {
        "inputs": {
            "content_parts": content_parts,
            "question": question,
            "combined_content": content
        },
        "lm_score_output": score,
        "lm_score_time_seconds": elapsed_time,
        "lm_score_tokens": total_tokens,
        "lm_judge_evaluation": {
            "judgment": judge_judgment,
            "explanation": judge_explanation
        },
        "human_evaluation": {
            "reasonable": human_reasonable
        },
        "item_info": item_info,
        "description": description
    }


def benchmark_lm_score(run_full: bool, prefix: str):
    """Run LM_SCORE on all entries in company.db with 2 questions per table."""
    conn = get_connection("company.db")
    cursor = conn.cursor()

    results = []

    print("=" * 80)
    print("LM_SCORE Evaluation on company.db")
    print("=" * 80)

    # EMAILS TABLE - Question 1 (first 5 entries)
    print("\n[EMAILS - Question 1/2] Is this email about billing or payments?")
    print("=" * 80)
    cursor.execute("SELECT email, subject, body FROM emails LIMIT 5")
    question1 = 'Is this email about billing or payments?'
    for row in cursor.fetchall():
        email, subject, body = row
        result = evaluate_single_item(
            content_parts=[subject, body],
            question=question1,
            description=f"Email: {email}",
            item_info={"Subject": subject}
        )
        results.append(result)

    # EMAILS TABLE - Question 2 (last 5 entries)
    print("\n[EMAILS - Question 2/2] Is this email about meetings or scheduling?")
    print("=" * 80)
    cursor.execute("SELECT email, subject, body FROM emails LIMIT 5 OFFSET 5")
    question2 = 'Is this email about meetings or scheduling?'
    for row in cursor.fetchall():
        email, subject, body = row
        result = evaluate_single_item(
            content_parts=[subject, body],
            question=question2,
            description=f"Email: {email}",
            item_info={"Subject": subject}
        )
        results.append(result)

    if not run_full:
        # Save results and exit early
        save_results(results, prefix)
        conn.close()
        return

    # INVOICES TABLE - Question 1 (first 5 entries)
    print("\n[INVOICES - Question 1/2] Is this invoice for a software or technology product?")
    print("=" * 80)
    cursor.execute("SELECT customer, product, amount, description FROM invoices LIMIT 5")
    question3 = 'Is this invoice for a software or technology product?'
    for row in cursor.fetchall():
        customer, product, amount, description = row
        result = evaluate_single_item(
            content_parts=[product, description],
            question=question3,
            description=f"Customer: {customer}",
            item_info={"Product": product, "Amount": f"${amount}"}
        )
        results.append(result)

    # INVOICES TABLE - Question 2 (last 5 entries)
    print("\n[INVOICES - Question 2/2] Is this invoice for a service or consulting engagement?")
    print("=" * 80)
    cursor.execute("SELECT customer, product, amount, description FROM invoices LIMIT 5 OFFSET 5")
    question4 = 'Is this invoice for a service or consulting engagement?'
    for row in cursor.fetchall():
        customer, product, amount, description = row
        result = evaluate_single_item(
            content_parts=[product, description],
            question=question4,
            description=f"Customer: {customer}",
            item_info={"Product": product, "Amount": f"${amount}"}
        )
        results.append(result)

    # SALES_LEADS TABLE - Question 1 (first 5 entries)
    print("\n[SALES LEADS - Question 1/2] Is this lead interested in cloud or SaaS solutions?")
    print("=" * 80)
    cursor.execute("SELECT client_name, description FROM sales_leads LIMIT 5")
    question5 = 'Is this lead interested in cloud or SaaS solutions?'
    for row in cursor.fetchall():
        client_name, description = row
        result = evaluate_single_item(
            content_parts=[client_name, description],
            question=question5,
            description=f"Client: {client_name}",
            item_info={}
        )
        results.append(result)

    # SALES_LEADS TABLE - Question 2 (last 5 entries)
    print("\n[SALES LEADS - Question 2/2] Is this lead in healthcare or medical industry?")
    print("=" * 80)
    cursor.execute("SELECT client_name, description FROM sales_leads LIMIT 5 OFFSET 5")
    question6 = 'Is this lead in healthcare or medical industry?'
    for row in cursor.fetchall():
        client_name, description = row
        result = evaluate_single_item(
            content_parts=[client_name, description],
            question=question6,
            description=f"Client: {client_name}",
            item_info={}
        )
        results.append(result)

    # Save results to JSON
    save_results(results, prefix)

    print("\n" + "=" * 80)
    print("Evaluation Complete!")
    print("=" * 80)

    conn.close()


def save_results(results: list, prefix: str):
    """Save benchmark results to JSON file.

    Args:
        results: List of evaluation result dictionaries
        prefix: Prefix for the output filename
    """
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{prefix}_benchmark_result.json")

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full",
        default=False,
        action="store_true",
        help="Run full benchmark on all entries",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        required=True,
        help="Prefix for output filename (e.g., 'test1' will create 'out/test1_benchmark_result.json')",
    )
    args = parser.parse_args()
    benchmark_lm_score(args.full, args.prefix)
