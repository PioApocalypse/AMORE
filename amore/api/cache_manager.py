import json
import os
import time
from datetime import datetime, timedelta
import threading


class CacheManager:
    """
    Manages application-level caching with TTL (time-to-live) and refresh strategies.
    Frequently-changing data (sample_locator) is handled with less TTL compared to stable data (slots, categories).

    Attributes:
        cache_dir:  Directory to which save the cache (JSON format).
        ttl:        Dictionary containing every field's Time-to-Live.
        cache:      Dictionary containing the actual cached data.
        timestamps: Creates a dictionary of zeros, which is later populated with the
                    mtimes of every key: when a "cache" key is updated its timestamp
                    is set to current time, and the cache expires when current time
                    `time.time()` minus the timestamp value `self.timestamps[key]`
                    is bigger than the TTL `self.ttl[key]`.
        lock:       Enables thread-based parallelism to accelerate cache updates.
    """

    # fun fact of the day: in English both "zeros" and "zeroes" (noun) are correct,
    # unless of course you're using it as a verb ("he zeroES in on his target").

    def __init__(self, cache_dir="amore/var/"):
        self.cache_dir = cache_dir
        # self.ttl = TTL in seconds
        self.ttl = {
            "categories": 3600,  # 1 hour
            "slots": 3600,  # 1 hour too
            "sample_locator": 60,  # 1 minute
        }
        # self.cache creates and stores the actual cache.
        # This is supposed to be the starting point.
        # Every time the cache is invalidated it *should* get back to this.
        self.cache = {"categories": None, "slots": None, "sample_locator": None}
        self.timestamps = {
            key: 0 for key in self.cache.keys()
        }  # dict. of zeros, incremented later
        # Creates a lock for threading:
        # To-do: check how Lock objects (prev. functions) changed in Python 3.13.
        self.lock = threading.Lock()

    def _load_from_disk(self, key):
        """Loads cache from JSON file. Returns json.load(file), or None."""
        # filepath should be the same in _load_from_disk and _save_to_disk:
        filepath = os.path.join(self.cache_dir, f"{key}.json")
        try:
            if os.path.isfile(filepath):
                with open(filepath, "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading {key} from disk: {str(e)}")
        return None

    def _save_to_disk(self, key, data):
        """Persists cache to JSON file."""
        # filepath should be the same in _load_from_disk and _save_to_disk:
        filepath = os.path.join(self.cache_dir, f"{key}.json")
        # error handling favor of Claude Code:
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            # NOTE: if file exists it gets overwritten.
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {key} to disk: {str(e)}")

    def is_expired(self, key):
        """Checks if cache entry has expired. Returns boolean value."""
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
                self.cache = {key: None for key in self.cache}
                self.timestamps = {key: 0 for key in self.timestamps}


# Test:
if __name__ == "__main__":
    cache = CacheManager()
    cache.timestamps = {key: time.time() for key in cache.timestamps}
    cache.cache["sample_locator"] = {"SLOT_A": "sample X", "SLOT_B": "another sample"}
    cache._save_to_disk("sample_locator", data=cache.cache["sample_locator"])
    while not cache.is_expired("sample_locator"):
        print("NOT EXPIRED")
        time.sleep(10)
        left = time.time() - cache.timestamps["sample_locator"]
        if left >= 10:
            print(cache.cache)
        if left >= 30:
            cache.invalidate()
    print("EXPIRED")
    testcache = cache._load_from_disk("sample_locator")
    print(testcache)
