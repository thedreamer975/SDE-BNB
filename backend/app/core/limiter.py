from slowapi import Limiter
from slowapi.util import get_remote_address

# Default limiter with client IP key function
limiter = Limiter(key_func=get_remote_address, default_limits=[])
