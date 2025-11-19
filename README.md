## Setup
For running the server locally, simply run 
```zsh
source src/server/server.sh
```
on Mac.

To run from another OpenAI-compatible server, simply update the SERVER_URL and API_KEY fields
in .env.

To set up the client, 
1. Install `uv` with `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Run `uv venv && source .venv/bin/activate` to activate the virtual environment

### Example usage
Run the following in your terminal:
```zsh
uv run python -i src/lm_score/lm_score.py --database company.db
```
Now that you are in the python interactive environment, you can run one of the examples that is displayed to make SQL queries that utilize the LM_SCORE function that we've defined. If you would like to use your own SQL database, pass its path into the command line in place of `company.db`.
### Configuration
Set the config in .env (AGGREGATION, ENSEMBLE, THINKING)
* ENSEMBLE: Whether or not to make multiple LM queries and aggregate the output with the method defined in AGGREGATION (either "t" or "f")
* AGGREGATION: How to aggregate the results if ENSEMBLE=t. 
* THINKING: Whether or not thinking is activated in the LM server.
