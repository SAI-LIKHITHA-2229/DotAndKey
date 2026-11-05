from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Rate limits are counted per client IP. "memory://" keeps counters inside
# one server process; with several processes set RATELIMIT_STORAGE_URI to a
# shared store such as redis://localhost:6379.
limiter = Limiter(key_func=get_remote_address, default_limits=[])
