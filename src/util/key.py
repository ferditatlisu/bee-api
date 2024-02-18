COPY_EVENT_PREFIX_KEY = "ks-copy:"
SEARCH_PREFIX_KEY = "ks-search:"
PARTITION_EVENT_PREFIX_KEY = "ks-partition:"

def get_copy_result_key(from_topic: str, to_topic: str):
    return f"{COPY_EVENT_PREFIX_KEY}{from_topic}||{to_topic}"

def get_search_metadata_key(key: str):
    return f"{SEARCH_PREFIX_KEY}{key}"

def get_partition_result_key(topic: str, ignored_partitions: str):
    return f"{PARTITION_EVENT_PREFIX_KEY}{topic}||{ignored_partitions}"