COPY_EVENT_PREFIX_KEY = "ks-copy:"
SEARCH_PREFIX_KEY = "ks-search:"

def get_copy_result_key(from_topic: str, to_topic: str):
    return f"{COPY_EVENT_PREFIX_KEY}{from_topic}||{to_topic}"

def get_search_metadata_key(key: str):
    return f"{SEARCH_PREFIX_KEY}{key}"