import random

# Alphanumeric charset without confusing characters (no 0, 1, I, O)
CONFIRMATION_CHARSET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


def generate_confirmation_code(length: int = 10) -> str:
    """Generate a 10-character confirmation code (e.g. HM4K9Z2QXA)."""
    return "".join(random.choices(CONFIRMATION_CHARSET, k=length))
