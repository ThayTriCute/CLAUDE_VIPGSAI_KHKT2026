"""Small, deterministic guards for persisted Streamlit widget state."""


def valid_option_index(value, option_count):
    """Keep a real in-range index; reset stale labels/types to the first option.

    A label or numeric string is not an index: coercing it can silently select
    another exam after the subject/grade catalogue has changed.
    """
    if type(value) is int and 0 <= value < option_count:
        return value
    return 0
