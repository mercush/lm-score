"""Main entry point for the lm-score CLI.

This module serves as the command-line interface entry point for the lm-score
package. It can be invoked using the 'lm-score' command after installation.

Example:
    $ lm-score
    Hello from lm-score!
"""


def main() -> None:
    """Main CLI entry point.

    This function is called when the user runs the 'lm-score' command.
    Currently prints a welcome message. Future versions will include
    CLI commands for database setup, scoring, and benchmarking.

    Returns:
        None
    """
    print("Hello from lm-score!")


if __name__ == "__main__":
    main()
