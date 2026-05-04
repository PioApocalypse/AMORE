import json
import os
import time
from datetime import datetime, timedelta
import threading

class CacheManager:
    """
    Manages application-level caching with TTL (time-to-live) and refresh strategies.
    Frequently-changing data (sample_locator) is handled with less TTL compared to stable data (slots, categories).
    """
    def __init__(self, cache_dir="amore/var/"):
        self.cache_dir = cache_dir
        # self.ttl = TTL in seconds
        self.ttl = {
            'categories': 3600, # 1 hour
            'slots': 3600, # 1 hour too
            'sample_locator': 60 # 1 minute
        }
        # self.cache creates and stores the actual cache.
        # This is supposed to be the starting point.
        # Every time the cache is invalidated it *should* get back to this.
        self.cache = {
            'categories': None,
            'slots': None,
            'sample_locator': None
        }
        self.timestamps = { key: 0 for key in self.cache.keys() } # dict. of zeros, incremented later
        # Creates a lock for threading:
        self.lock = threading.Lock()

    def is_expired(self, key):
        """Checks if cache entry has expired."""
        return time.time() - self.timestamps[key] > self.ttl[key]

    def invalidate(self, key=None):
        """
        Manually invalidates cache. Resets self.cache to initial condition.
        If no key is specified all is invalidated.
        """
        with self.lock:
            if key:
                self.cache[key] = None
                self.timestamps[key] = 0
            else:
            # experimental: if no key is specified invalidates all cache.
            # this WILL go wrong.
                self.cache = { key: None for key in self.cache }
                self.timestamps = { key: 0 for key in self.timestamps }

# Test:
if __name__=="__main__":
    cache = CacheManager()
    cache.timestamps = { key: time.time() for key in cache.timestamps }
    cache.cache['sample_locator'] = { "SLOT_A": "sample X", "SLOT_B": "another sample" }
    while not cache.is_expired('sample_locator'):
        print("NOT EXPIRED")
        time.sleep(10)
        left = time.time() - cache.timestamps['sample_locator']
        if left >= 10: print(cache.cache)
        if left >= 30: cache.invalidate()
    print("EXPIRED")

