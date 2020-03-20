import datetime

class CharCache:
    """cache for storing character and user info"""
    def __init__(self):
        """constructor"""
        self.cache = {}
        self.max_cache_size = 1000

    def __contains__(self, key):
        """
        returns bool confirming key is in cache
        """
        return key in self.cache

    def update(self, key, value):
        """
        Update the cache dictionary and optionally remove the oldest item
        """
        if key not in self.cache and len(self.cache) >= self.max_cache_size:
            self.remove_oldest()

        self.cache[key] = {'date_accessed': datetime.datetime.now(),
                           'value': value}

    def remove_oldest(self):
        """
        remove oldest entry
        """
        oldest_entry = None
        for key in self.cache:
            if oldest_entry is None:
                oldest_entry = key
            elif self.cache[key]['date_accessed'] < self.cache[oldest_entry]['date_accessed']:
                oldest_entry = key
        self.cache.pop(oldest_entry)

    @property
    def size(self):
        """
        Return the size of the cache
        """
        return len(self.cache)

