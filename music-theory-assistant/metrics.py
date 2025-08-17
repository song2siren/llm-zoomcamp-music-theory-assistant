import time
from contextlib import contextmanager

@contextmanager
def timer():
    start = time.perf_counter()
    try:
        yield lambda: time.perf_counter() - start
    finally:
        pass

def empty_token_usage():
    # Replace with real counts from your LLM client if available
    return dict(
        prompt_tokens=0,
        completion_tokens=0,
        total_tokens=0,
        eval_prompt_tokens=0,
        eval_completion_tokens=0,
        eval_total_tokens=0,
    )