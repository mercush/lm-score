# Design specification
- Scores are obtained by prompting the LM to output a score. It is not given by the logprob.

## Client
* LM_SCORE takes in at least two arguments. If _n_ arguments are passed in, the first _n-1_ arguments are the contents to be scored, and the last argument is a yes-or-no question.
* LM_SCORE returns an integer between 0 and 10, where 0 is _no_ and 10 is _yes_.
* Example usage:
```python
LM_SCORE("This is a test", "Is this a test?") = 10
LM_SCORE("We have a meeting today at 3:00", "Are we meeting today at 3:00?") = 10
LM_SCORE("We have a meeting today at 3:00", "Are we meeting today at 4:00?") = 3
LM_SCORE("Weekly invoice 12/12/2022", "$14,000", "Is my invoice greater than $5,000?") = 10
``` 
* LM_SCORE wraps all the content (joined by a "\n") into a prompt and calls the LM.
* The prompt is
```python
content = "\n".join(content_parts)

prompt = f"""Based on the following content, answer this yes/no question: {question}

Content: 
{content}

Provide a score from 0 to 10 based on your confidence in the answer:
- 10 = strongly yes, definitely true
- 7-9 = probably yes, likely true
- 5-6 = uncertain, could go either way
- 3-4 = probably no, likely false
- 0-2 = strongly no, definitely false

Provide only a single number from 0 to 10.
Score:"""
```
## Configurations
* ENSEMBLE: Whether to use ensemble scoring (t) or not (f)
* AGGREGATION: Whether to use majority voting (maj) or average for ensembling (avg)
* THINKING: Whether to allow the LM to think (t) or whether to suppress the tokens by coercing the LM to start with <think>Okay, I think I have finished thinking</think> via the chat template.

When ENSEMBLE is turned on, the LM calls are sequential instead of asynchronous. This is because the server (mlx_lm.server) doesn't support continuous batching yet, so it is not possible to dispatch multiple LM calls at the same time.

## Server
The server is a simple HTTP server that exposes a single endpoint `/lm_score` that accepts a POST request with a JSON payload containing the prompt (above). By default, it runs locally, but can be easily configured to run on a remote server by editing the `.env` file.

## Alternate designs
- Prompting LM to output yes/no and then using the logprob
    - Might lead to lower token usage
- Asynchronous calls when ensembling
    - This will not yield lower token usage, but will yield lower latency.
- Dispatching a separate LM call for each content asynchronously
    - The asynchronous dispatch will lower latency
    - Breaking the content into multiple LM calls will also lower the cost (time/usage) cost associated with prefill
    - The problem here is that independence assumptions are made that are not true in practice. For instance
    ```python
    LM_SCORE("Weekly invoice 12/12/2022", "$14,000", "Is my invoice greater than $5,000?")
    ```
    would not be read properly.


# Future steps
* Optimize prompt with DSPy
* Making LM calls async
* mlx_lm.server doesn't support continuous batching yet, so should be able to speed up async calls more.

