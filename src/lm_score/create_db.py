"""Create a company database with emails, invoices, and sales leads.

This module provides functionality to create a sample SQLite database populated
with realistic business data for testing and demonstrating the LM_SCORE function.

The database includes three tables:
    - emails: Sample email messages with sender, subject, and body
    - invoices: Sample invoices with customer, product, amount, and description
    - sales_leads: Sample sales opportunities with client name and description

Example:
    >>> from lm_score.create_db import create_company_database
    >>> create_company_database('my_test.db')
    Database created successfully at: my_test.db
      Emails: 10
      Invoices: 10
      Sales Leads: 10
      Total entries: 30
"""

import sqlite3
from pathlib import Path


def create_company_database(db_path: str = "company.db") -> None:
    """Create a company database with sample data.

    Creates a SQLite database with three tables (emails, invoices, sales_leads)
    and populates each with 10 realistic sample records. The database is designed
    to showcase semantic querying capabilities using the LM_SCORE function.

    If the database already exists, tables will be created only if they don't exist
    (using IF NOT EXISTS), but new sample data will be inserted regardless.

    Args:
        db_path: Path to the database file to create. Defaults to "company.db".
                If the file doesn't exist, it will be created.

    Returns:
        None. Prints a summary of created records to stdout.

    Example:
        >>> create_company_database('test.db')
        Database created successfully at: test.db
          Emails: 10
          Invoices: 10
          Sales Leads: 10
          Total entries: 30
    """
    # Connect to database (creates if doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create emails table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Sample email data (10 entries)
    sample_emails = [
        (
            "john.doe@example.com",
            "Welcome to our service",
            "Thank you for signing up! We're excited to have you on board. "
            "Please verify your email address to get started."
        ),
        (
            "jane.smith@example.com",
            "Your order has been shipped",
            "Great news! Your order #12345 has been shipped and should arrive "
            "within 3-5 business days. Track your package using the link below."
        ),
        (
            "support@company.com",
            "Password reset request",
            "We received a request to reset your password. If you didn't make "
            "this request, please ignore this email. Click the link below to reset."
        ),
        (
            "newsletter@tech.com",
            "This week in technology",
            "Here are the top tech stories of the week: AI breakthroughs, new "
            "smartphone releases, and cybersecurity updates. Read more inside."
        ),
        (
            "billing@service.com",
            "Invoice for January 2025",
            "Your invoice for January 2025 is ready. Amount due: $49.99. "
            "Payment is due by February 1st, 2025. View invoice details below."
        ),
        (
            "team@startup.com",
            "Meeting reminder: Q1 Planning",
            "This is a reminder about our Q1 planning meeting scheduled for "
            "tomorrow at 2 PM. Please review the agenda and come prepared."
        ),
        (
            "marketing@agency.com",
            "New campaign proposal",
            "We have a new marketing campaign proposal for Q2. The campaign will focus on "
            "social media engagement and content marketing strategies."
        ),
        (
            "hr@company.com",
            "Benefits enrollment reminder",
            "This is a reminder that benefits enrollment period ends next Friday. "
            "Please review your health insurance and retirement plan options."
        ),
        (
            "sales@business.com",
            "Quote request follow-up",
            "Following up on the quote request you sent last week. We can offer a "
            "15% discount if you sign the contract before month end."
        ),
        (
            "accounts@vendor.com",
            "Payment confirmation",
            "We have received your payment of $2,500 for invoice #98765. "
            "Thank you for your business."
        ),
    ]

    cursor.executemany(
        "INSERT INTO emails (email, subject, body) VALUES (?, ?, ?)",
        sample_emails
    )

    # Create invoices table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            product TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Sample invoice data (10 entries)
    sample_invoices = [
        ("Acme Corp", "Software License", 1999.99, "Annual enterprise software license renewal"),
        ("Tech Startup Inc", "Consulting Services", 5500.00, "Technical consulting for cloud migration project"),
        ("Global Solutions LLC", "Hardware Equipment", 12500.00, "10 workstations and networking equipment"),
        ("Digital Media Co", "Web Development", 8750.00, "Custom website development and design"),
        ("Retail Chain Ltd", "POS System", 15000.00, "Point of sale system for 5 locations"),
        ("Manufacturing Co", "Training Program", 3200.00, "Employee safety training and certification"),
        ("Finance Group", "Data Analytics", 6800.00, "Business intelligence dashboard implementation"),
        ("Healthcare Partners", "Security Audit", 4500.00, "Cybersecurity assessment and compliance review"),
        ("Education Institute", "Cloud Storage", 2100.00, "Cloud storage subscription for academic year"),
        ("Logistics Corp", "Mobile App", 9500.00, "Custom mobile application for fleet management"),
    ]

    cursor.executemany(
        "INSERT INTO invoices (customer, product, amount, description) VALUES (?, ?, ?, ?)",
        sample_invoices
    )

    # Create sales_leads table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Sample sales leads data (10 entries)
    sample_leads = [
        ("Blue Ocean Enterprises", "Interested in upgrading their legacy CRM system to modern cloud solution"),
        ("Green Energy Partners", "Looking for data analytics platform to track renewable energy production"),
        ("Urban Development Group", "Need project management software for construction projects"),
        ("Premium Retail Brands", "Want to implement AI-powered inventory management system"),
        ("Medical Diagnostics Lab", "Seeking HIPAA-compliant patient data management platform"),
        ("International Shipping Co", "Interested in IoT tracking solution for cargo containers"),
        ("Restaurant Chain Network", "Looking for integrated POS and delivery management system"),
        ("Financial Advisory Firm", "Need secure client portal and document management system"),
        ("Sports Equipment Manufacturer", "Want e-commerce platform with B2B and B2C capabilities"),
        ("Travel Agency Network", "Interested in booking system integration and customer analytics"),
    ]

    cursor.executemany(
        "INSERT INTO sales_leads (client_name, description) VALUES (?, ?)",
        sample_leads
    )

    # Commit changes
    conn.commit()

    # Print summary
    cursor.execute("SELECT COUNT(*) FROM emails")
    email_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM invoices")
    invoice_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM sales_leads")
    leads_count = cursor.fetchone()[0]

    total = email_count + invoice_count + leads_count

    print(f"Database created successfully at: {db_path}")
    print(f"  Emails: {email_count}")
    print(f"  Invoices: {invoice_count}")
    print(f"  Sales Leads: {leads_count}")
    print(f"  Total entries: {total}")

    conn.close()


if __name__ == "__main__":
    create_company_database()
