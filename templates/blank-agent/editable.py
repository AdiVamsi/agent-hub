"""The ONE file the agent modifies.

Replace this with your baseline implementation. The agent will iteratively
improve this file to optimize your chosen metric.

Tips:
- Start with the simplest possible implementation
- Make sure the interface matches what harness.py expects
- Keep it readable — the agent builds on previous experiments
"""


def process(input_data: dict) -> dict:
    """Process a single input and return a result.

    Replace this function signature and logic with your own.
    The harness will call this function for each input in your dataset.

    Args:
        input_data: A single item from your dataset

    Returns:
        A result dict that harness.py knows how to score
    """
    # BASELINE: no optimization. The agent will improve this.
    return {"result": input_data}
