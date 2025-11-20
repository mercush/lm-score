# Design specification
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
## Error handling
Reasonably often, the LM will give an output that does not conform to the DSPy format so we need to handle this case. In the cases where the LM fails to output in the correct format, LM_SCORE will output 5.

## Configurations
* ENSEMBLE: Whether to use ensemble scoring (t) or not (f)
* AGGREGATION: Whether to use majority voting (maj) or average for ensembling (avg)
* THINKING: Whether to allow the LM to think (t) or whether to suppress the tokens by coercing the LM to start with <think>Okay, I think I have finished thinking</think> via the chat template, which has been shown the dramatically [lower token usage and marginally decrease performance](https://arxiv.org/abs/2504.09858).
* SERVER_URL: The URL of the server to use for making LM calls
* API_TOKEN: The API token to use for making LM calls
* MODEL: The model to use for making LM calls

* LM_AS_JUDGE_SERVER_URL: The URL of the server to use for making LM calls for the judge
* LM_AS_JUDGE_API_TOKEN: The API token to use for making LM calls for the judge
* LM_AS_JUDGE_MODEL: The model to use for making LM calls for the judge

## Server
The server is a simple OpenAI-compatible API server that accepts POST requests with a JSON payload containing the prompt (above). By default, it runs locally, but can be easily configured to run on a remote server by editing the `.env` file.

## Efficiency
* **Compute**: scales quadratically with the number of contents passed into `LM_SCORE`.
* **Latency**: If `ENSEMBLE` is enabled, the primary bottleneck is the sequential execution of ensemble queries. Since `mlx_lm.server` is currently treated as a synchronous endpoint in this implementation, enabling `ENSEMBLE` results in roughly 3x the latency of a single call.
* **Token Usage**: Reduced significantly when `THINKING` is disabled. When `THINKING` is enabled, output cost and latency increase significantly due to the generation of chain-of-thought tokens.
* **Caching**: Caching is currently disabled (`cache=False`) to ensure independent samples for the ensemble and accurate benchmarking, meaning every `LM_SCORE` call incurs a full model inference cost. However, this can easily be turned on and would yield a speedup.

## Alternate designs
- Prompting LM to output yes/no and then using the logprob
    - Might lead to lower token usage
    - Would be difficult to evaluate because logprobs are not comparable across models and across prompts
- Asynchronous calls when ensembling
    - This will not yield lower token usage, but will yield lower latency
- Dispatching a separate LM call for each content passed into `LM_SCORE` asynchronously
    - The asynchronous dispatch will lower latency
    - Breaking the content into multiple LM calls will also lower the cost (time/usage) cost associated with prefill
    - The problem here is that independence assumptions are made that are not true in practice. For instance
    ```python
    LM_SCORE("Weekly invoice 12/12/2022", "$14,000", "Is my invoice greater than $5,000?")
    ```
    would not be read properly.

# Future steps
* Optimize prompt with DSPy

