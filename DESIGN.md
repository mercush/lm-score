# Design specification
## Roadmap
* Goal
* Base Implementation
* Configurations
* Efficiency
* Alternate designs
* Benchmarking
## Goal
The goal of this project is to extend SQL with a Python function `LM_SCORE` that 
* takes in at least 2 arguments. If _n_ arguments are passed in, the first _n-1_ arguments are the contents to be scored, and the last argument is a yes-or-no question.
* returns an integer between 0 and 10, where 0 is _no_ and 10 is _yes_.
Example usage:
```python
LM_SCORE("This is a test", "Is this a test?") = 10
LM_SCORE("We have a meeting today at 3:00", "Are we meeting today at 3:00?") = 10
LM_SCORE("We have a meeting today at 3:00", "Are we meeting today at 4:00?") = 3
LM_SCORE("Weekly invoice 12/12/2022", "$14,000", "Is my invoice greater than $5,000?") = 10
``` 
The key objectives are to balance efficiency (as measured by token usage and time) with performance.
## Base Implementation
In the base implementation, `LM_SCORE` simply wraps all the content (joined by a "\n") into a prompt and calls the LM. The prompt is
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
Interactions with the LM API use DSPy, which adds a system prompt that instructs the language model on how to format its response and implements logic for extracting the numerical value response from the language model's output.

## Server
By default, the server runs locally with `mlx_lm.server` and `mlx-community/DeepSeek-R1-Distill-Qwen-7B-4bit`, but can be easily configured to run on a remote server by editing the `.env` file.

## Configurations
* `ENSEMBLE`: Whether to use ensemble scoring (t) or not (f)
* `AGGREGATION`: Whether to use majority voting (`maj`) or average (`avg`) for ensembling
* `THINKING`: Whether to allow the LM to think (t) or whether to suppress the tokens by coercing the LM to start with `<think>Okay, I think I have finished thinking</think>` via the chat template, which has been shown the dramatically [lower token usage and marginally decrease performance](https://arxiv.org/abs/2504.09858).

## Efficiency
* **Compute**: FLOPs scale quadratically with the number of contents passed into `LM_SCORE`.
* **Latency**: If `ENSEMBLE` is enabled, the primary bottleneck is the sequential execution of ensemble queries. Since `mlx_lm.server` is currently treated as a synchronous endpoint in this implementation, enabling `ENSEMBLE` results in roughly 3x the latency of a single call.
* **Token Usage**: Reduced significantly when `THINKING` is disabled. When `THINKING` is enabled, output cost and latency increase due to the generation of chain-of-thought tokens.
* **Caching**: Caching is currently disabled (`cache=False`) to ensure independent samples for the ensemble and accurate benchmarking, meaning every `LM_SCORE` call incurs a full model inference cost. However, this can easily be turned on and would yield a speedup.

## Alternate designs
- Prompting LM to output yes/no and then using the logprob
    - Might lead to lower token usage
    - Would be difficult to evaluate because logprobs are not comparable across models and across prompts
- Asynchronous calls when ensembling
    - This will not yield lower token usage, but will lower the latency
- Dispatching a separate LM call for each content passed into `LM_SCORE` asynchronously
    - The asynchronous dispatch will lower latency
    - Breaking the content into multiple LM calls will also lower the compute cost associated with prefill
    - The problem here is that independence assumptions are made that are not true in practice. For instance
    ```python
    LM_SCORE("Weekly invoice 12/12/2022", "$14,000", "Is my invoice greater than $5,000?")
    ```
    would likely output a score ≤5

## Benchmarking
Benchmarking details are included in [BENCHMARK.md](BENCHMARK.md)

## Error handling
Reasonably often, the LM will give an output that does not conform to the DSPy format so we need to handle this case. In the cases where the LM fails to output in the correct format, `LM_SCORE` will output 5.
