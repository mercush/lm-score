## Setup
For running locally, simply run 
```zsh
mlx_lm.server --model "mlx-community/DeepSeek-R1-Distill-Qwen-7B-4bit"
```
on Mac.
To suppress the thinking tokens, run 
```zsh
mlx_lm.server \
    --model "mlx-community/DeepSeek-R1-Distill-Qwen-7B-4bit" \
    --max-tokens 4000 \
    --chat-template "$(cat src/server/chat.template)"
```

To run from another OpenAI-compatible server, simply update the SERVER_URL and API_KEY fields
in .env.

### Example usage
Run the following in your terminal:
```zsh
python -i src/lm_score/lm_score.py
```
Now that you are in the python interactive environment, you can run one of the examples that is displayed.

## Experiments
Use `uv`. Run `uv venv; source .venv/bin/activate; uv sync; time uv run tests/benchmark_lm_score.py`
Scoring is based on subjective reasonability of answers. I label every score as either "reasonable" or "unreasonable".

* DSPy Predict, one pass.
* Time: 6:10.11
* Score: 27/30
* Tokens: 406.62

* DSPy suppress thinking tokens, Predict, one pass.
* Time: 1:08
* Score: 19/30
* Tokens: 78.50

* DSPy suppress thinking tokens, Predict, 3 passes, majority vote.
* Time: 3:50:38
* Score: 23/30
* Score: ~237.97

* DSPy suppress thinking tokens, Predict, 3 passes, average.
* Time: 3:29.47
* Score: 25/30
* Score: ~237.97

Run `uv run python analysis/viz.py` for a visualization of these results.

## AI tools
Registering LM_SCORE in SQL.

Created company.db database.

Created docstrings for functions.

Ran benchmarking script.

Visualizing bar plots for benchmarking.


## Future steps
Optimize prompt with DSPy
Making LM calls async
mlx_lm.server doesn't support continuous batching yet, so
should be able to speed up async calls more.
