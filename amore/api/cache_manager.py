import json
import os
import time
from datetime import datetime, timedelta
import threading


class CacheManager:
    """
    Manages application-level caching with TTL (time-to-live) and refresh strategies.
    Frequently-changing data (sample_positions) is handled with less TTL compared to stable data (slots, categories).

    Arguments:
        cache_dir: Directory to which save the cache (JSON format). Default is "amore/var/".

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

    Methods:
        _load_from_disk:    Loads cache from a JSON file in cache_dir.
                            Returns json.load(file), or None.
        _save_to_disk:      Persists cache to a JSON file in cache_dir.
        is_expired:         Checks if a cache entry has expired based on its timestamp and TTL.
        invalidate:         Manually invalidates cache entries, either specific keys or all cache.
        get:                Retrieves cache entry.
                            If expired or force_refresh is True, it calls the API to update the cache,
                            then returns cached data (or None if not available).
    """

    # fun fact of the day: in English both "zeros" and "zeroes" (noun) are correct,
    # unless of course you're using it as a verb ("he zeroES in on his target").

    def __init__(self, cache_dir="amore/var/"):
        self.cache_dir = cache_dir
        # self.ttl = TTL in seconds
        # Categories should never change, it's possible I will just implement manual refresh;
        # Sample Positions change frequently because samples are moved frequently - sometimes outside the interface;
        # Substrates Batches chenge frequently because of residuals; Note for self: should I just decrement residual pieces from the cache too?
        # Proposals change every 5 minutes because they can be added manually and I won't have people waiting needlessly.
        self.ttl = {
            "categories": 3600 * 24,  # 1 day
            "slots": 30,  # 30 seconds because their metadata changes frequently.
            "substrates_batches": 60,  # 1 minute
            "proposals": 300,  # 5 minutes
        }
        # self.cache creates and stores the actual cache.
        # This is supposed to be the starting point.
        # Every time the cache is invalidated it *should* get back to this.
        self.cache = {
            "categories": None,
            "slots": None,
            "substrates_batches": None,
            "proposals": None,
        }
        self.timestamps = {
            key: 0 for key in self.cache.keys()
        }  # dict. of zeros, incremented later
        # Creates a lock for threading:
        # To-do: check how Lock objects (prev. functions) changed in Python 3.13.
        self.lock = threading.Lock()

    def _load_from_disk(self, key):
        """
        Loads cache from JSON file. Returns json.load(file), or None.
        Filename must not be specified, all cache is saved in cache_dir.
        Arg: category key to load. Must be one of the keys in self.cache.
        """
        # filepath should be the same in _load_from_disk and _save_to_disk:
        filepath = os.path.join(self.cache_dir, f"{key}.json")
        try:
            if os.path.isfile(filepath):
                with open(filepath, "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading {key} from disk: {str(e)}")
        return None

    def _save_to_disk(self, key, data=None):
        """
        Persists cache to JSON file.
        Filename must not be specified, all cache is saved in cache_dir.
        Args:
            key:    Category key to save. Must be one of the keys in self.cache.
            data:   Cache data to save. Must be JSON-serializable (dict, list, etc.).
        """
        # filepath should be the same in _load_from_disk and _save_to_disk:
        filepath = os.path.join(self.cache_dir, f"{key}.json")
        # if data is None try to get it from cache:
        data = data if data is not None else self.cache[key]

        # error handling favor of Claude Code:
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            # NOTE: if file exists it gets overwritten.
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {key} to disk: {str(e)}")

    def is_expired(self, key):
        """
        Checks if cache entry has expired. Returns True if it has.
        Arg: key: Category key to check. Must be one of the keys in self.cache.
        """
        return time.time() - self.timestamps[key] > self.ttl[key]

    def invalidate(self, key=None):
        """
        Manually invalidates cache. Resets self.cache to initial condition.
        Arg: key: Category key to invalidate. Must be one of the keys in self.cache.
             If no key is specified all cache is invalidated.
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

    def get(self, key, api_key=None, loader_func=None, force_refresh=False):
        """
        Retrieves cache entry. If expired or force_refresh is True, it calls the API to update the cache.
        Returns cached data - or None if that's not available.

        Part of this was written with assistance from Claude Code.

        Args:
            key:            Category key to retrieve. Must be one of the keys in self.cache.
            api_key:        Mandatory API key to call the API if cache is expired or force_refresh is True.

            loader_func:    Optional function to load data from API. Should return data to be cached.
            force_refresh:  If True, forces cache refresh by calling the API even if cache is valid and not expired.
                            Default is False, of course.
        """
        with self.lock:
            # If cache is valid and force_refresh is False, return cached data:
            if (
                not force_refresh
                and self.cache[key] is not None
                and not self.is_expired(key)
            ):
                return self.cache[key]

            # If cache is None and force_refresh is False, try loading from disk:
            if self.cache[key] is None and not force_refresh:
                disk_data = self._load_from_disk(key)
                if disk_data is not None:
                    self.cache[key] = disk_data
                    self.timestamps[key] = time.time()
                    return disk_data

            # If force_refresh, key is expired or None (implied from previous conditions),
            # call API to update cache  - which requires API key and loader function:
            if loader_func is not None and api_key is not None:
                try:
                    self.cache[key] = loader_func(api_key)
                    self.timestamps[key] = time.time()
                    self._save_to_disk(key, data=self.cache[key])
                    return self.cache[key]
                except:
                    # Failsafe: try fallback to stale cache if available, otherwise raise exception:
                    print(
                        f"Error loading {key} from API. Attempting fallback to stale cache..."
                    )
                    try:
                        if self.cache[key] is not None:
                            return self.cache[key]
                    except:
                        raise Exception(f"No stale cache available for {key}.")

            # If program reaches this point, it means API call failed and no stale cache is available.
            # This means we have to raise an exception, because returning None would be indistinguishable
            # from a valid cache entry that is actually None.
            # Note for self: LazyVim + Copilot is one hell of a setup.
            raise Exception(
                f"Failed to retrieve {key} from API and no stale cache available."
            )


# Test:
if __name__ == "__main__":
    cache = CacheManager()
    cache.timestamps = {key: time.time() for key in cache.timestamps}
    cache.cache["sample_positions"] = {"SLOT_A": "sample X", "SLOT_B": "another sample"}
    cache._save_to_disk("sample_positions", data=cache.cache["sample_positions"])
    while not cache.is_expired("sample_positions"):
        print("NOT EXPIRED")
        time.sleep(10)
        left = time.time() - cache.timestamps["sample_positions"]
        if left >= 10:
            print(cache.cache)
        if left >= 30:
            cache.invalidate()
    print("EXPIRED")
    testcache = cache._load_from_disk("sample_positions")
    print(testcache)
