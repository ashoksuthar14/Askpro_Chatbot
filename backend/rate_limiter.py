import time
from typing import Dict
from flask import Request


class RateLimiter:
	def __init__(self, cooldown_seconds: int = 2):
		self.cooldown = cooldown_seconds
		self.ip_to_last: Dict[str, float] = {}

	def is_limited(self, req: Request) -> bool:
		ip = req.headers.get("X-Forwarded-For", req.remote_addr or "unknown")
		now = time.time()
		last = self.ip_to_last.get(ip, 0)
		limited = now - last < self.cooldown
		if not limited:
			self.ip_to_last[ip] = now
		return limited
