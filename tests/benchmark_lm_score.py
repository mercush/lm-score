"""Benchmark LM_SCORE function on company.db."""

from lm_score.lm_score import get_connection
import argparse


def benchmark_lm_score(run_full: bool):
    """Run LM_SCORE on all entries in company.db with 2 questions per table."""
    conn = get_connection("company.db")
    cursor = conn.cursor()

    print("=" * 80)
    print("LM_SCORE Evaluation on company.db")
    print("=" * 80)

    # EMAILS TABLE - Question 1 (first 5 entries)
    print("\n[EMAILS - Question 1/2] Is this email about billing or payments?")
    print("-" * 80)
    cursor.execute("""
        SELECT
            email,
            subject,
            LM_SCORE(subject, body, 'Is this email about billing or payments?') as score
        FROM emails
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"Email: {row[0]}")
        print(f"Subject: {row[1]}")
        print(f"Score: {row[2]}/10")
        print("-" * 80)

    # EMAILS TABLE - Question 2 (last 5 entries)
    print("\n[EMAILS - Question 2/2] Is this email about meetings or scheduling?")
    print("-" * 80)
    cursor.execute("""
        SELECT
            email,
            subject,
            LM_SCORE(subject, body, 'Is this email about meetings or scheduling?') as score
        FROM emails
        LIMIT 5 OFFSET 5
    """)
    for row in cursor.fetchall():
        print(f"Email: {row[0]}")
        print(f"Subject: {row[1]}")
        print(f"Score: {row[2]}/10")
        print("-" * 80)

    if not run_full:
        return

    # INVOICES TABLE - Question 1 (first 5 entries)
    print(
        "\n[INVOICES - Question 1/2] Is this invoice for a software or technology product?"
    )
    print("-" * 80)
    cursor.execute("""
        SELECT
            customer,
            product,
            amount,
            LM_SCORE(product, description, 'Is this invoice for a software or technology product?') as score
        FROM invoices
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"Customer: {row[0]}")
        print(f"Product: {row[1]}")
        print(f"Amount: ${row[2]}")
        print(f"Score: {row[3]}/10")
        print("-" * 80)

    # INVOICES TABLE - Question 2 (last 5 entries)
    print("\n[INVOICES - Question 2/2] Is this invoice for a service or consulting engagement?")
    print("-" * 80)
    cursor.execute("""
        SELECT
            customer,
            product,
            amount,
            LM_SCORE(product, description, 'Is this invoice for a service or consulting engagement?') as score
        FROM invoices
        LIMIT 5 OFFSET 5
    """)
    for row in cursor.fetchall():
        print(f"Customer: {row[0]}")
        print(f"Product: {row[1]}")
        print(f"Amount: ${row[2]}")
        print(f"Score: {row[3]}/10")
        print("-" * 80)


    # SALES_LEADS TABLE - Question 1 (first 5 entries)
    print(
        "\n[SALES LEADS - Question 1/2] Is this lead interested in cloud or SaaS solutions?"
    )
    print("-" * 80)
    cursor.execute("""
        SELECT
            client_name,
            LM_SCORE(client_name, description, 'Is this lead interested in cloud or SaaS solutions?') as score
        FROM sales_leads
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"Client: {row[0]}")
        print(f"Score: {row[1]}/10")
        print("-" * 80)

    # SALES_LEADS TABLE - Question 2 (last 5 entries)
    print(
        "\n[SALES LEADS - Question 2/2] Is this lead in healthcare or medical industry?"
    )
    print("-" * 80)
    cursor.execute("""
        SELECT
            client_name,
            LM_SCORE(client_name, description, 'Is this lead in healthcare or medical industry?') as score
        FROM sales_leads
        LIMIT 5 OFFSET 5
    """)
    for row in cursor.fetchall():
        print(f"Client: {row[0]}")
        print(f"Score: {row[1]}/10")
        print("-" * 80)

    print("\n" + "=" * 80)
    print("Evaluation Complete!")
    print("=" * 80)

    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full",
        default=False,
        action="store_true",
        help="Run full benchmark on all entries",
    )
    args = parser.parse_args()
    benchmark_lm_score(args.full)
