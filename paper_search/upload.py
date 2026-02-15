import pickle
from pathlib import Path
from pybloom_live import BloomFilter
from elasticsearch import Elasticsearch
from typing import Dict, Any

# Configuration
BLOOM_FILTER_FILE = Path(__file__).parent / "bloom_filter.pkl"
BLOOM_FILTER_CAPACITY = 20000  # Expected number of papers
BLOOM_FILTER_ERROR_RATE = 0.01  # 1% false positive rate

# Global bloom filter instance
_bloom_filter = None


def _load_bloom_filter():
    """Load the bloom filter from disk or create a new one if it doesn't exist."""
    global _bloom_filter

    if _bloom_filter is not None:
        return _bloom_filter

    if BLOOM_FILTER_FILE.exists():
        try:
            with open(BLOOM_FILTER_FILE, 'rb') as f:
                _bloom_filter = pickle.load(f)
            print(f"Loaded existing bloom filter with {len(_bloom_filter)} entries")
        except Exception as e:
            print(f"Error loading bloom filter, creating new one: {e}")
            _bloom_filter = BloomFilter(
                capacity=BLOOM_FILTER_CAPACITY,
                error_rate=BLOOM_FILTER_ERROR_RATE
            )
    else:
        _bloom_filter = BloomFilter(
            capacity=BLOOM_FILTER_CAPACITY,
            error_rate=BLOOM_FILTER_ERROR_RATE
        )
        print(f"Created new bloom filter (capacity: {BLOOM_FILTER_CAPACITY}, error_rate: {BLOOM_FILTER_ERROR_RATE})")

    return _bloom_filter


def _save_bloom_filter():
    """Save the bloom filter to disk."""
    global _bloom_filter

    if _bloom_filter is None:
        return

    try:
        with open(BLOOM_FILTER_FILE, 'wb') as f:
            pickle.dump(_bloom_filter, f)
    except Exception as e:
        print(f"Error saving bloom filter: {e}")


def _normalize_title(title: str) -> str:
    """Normalize paper title for consistent comparison."""
    if not title:
        return ""
    # Convert to lowercase and strip whitespace for consistent hashing
    return title.lower().strip()


def is_recorded_in_bloom_filter(paper_title: str) -> bool:
    '''
    This function checks if a paper title is already recorded in the Bloom filter and returns whether it is likely to be a duplicate or not. This is used to avoid uploading duplicate records to the Elastic Vector Database.

    :param paper_title: The title to check for an existing record
    :return: True if the title is likely already recorded (potential duplicate), False otherwise
    '''
    bloom = _load_bloom_filter()
    normalized_title = _normalize_title(paper_title)

    if not normalized_title:
        return False

    return normalized_title in bloom


def record_in_bloom_filter(paper_title: str):
    '''
    This function records a paper title in the Bloom filter to indicate that it has been processed and uploaded to the Elastic Vector Database. This helps to prevent future duplicate uploads.

    :param paper_title: The title record to add to the Bloom filter
    '''
    bloom = _load_bloom_filter()
    normalized_title = _normalize_title(paper_title)

    if not normalized_title:
        return

    bloom.add(normalized_title)
    _save_bloom_filter()


def upload(paper_json: Dict[str, Any], elastic_client: Elasticsearch = None, index_name: str = "papers") -> bool:
    '''
    This function uploads a paper's JSON to the Elastic Vector Database. Before uploading, it checks if the paper's title is already recorded in the Bloom filter to avoid duplicates. If the paper is not a duplicate, it proceeds with the upload and then records the title in the Bloom filter.

    :param paper_json: Dictionary containing paper data with at least 'title' and 'abstract' fields
    :param elastic_client: Elasticsearch client instance (optional for testing)
    :param index_name: Name of the Elasticsearch index to upload to
    :return: True if uploaded successfully, False if duplicate or error
    '''
    # Validate input
    if not paper_json or 'title' not in paper_json:
        print("Error: paper_json must contain a 'title' field")
        return False

    paper_title = paper_json['title']

    # Check for duplicates using bloom filter
    if is_recorded_in_bloom_filter(paper_title):
        print(f"Duplicate detected (bloom filter): '{paper_title[:60]}...'")
        return False

    # Upload to Elasticsearch (if client provided)
    if elastic_client is not None:
        try:
            response = elastic_client.index(
                index=index_name,
                document=paper_json
            )
            print(f"Uploaded paper: '{paper_title[:60]}...' (ID: {response['_id']})")
        except Exception as e:
            print(f"Error uploading to Elasticsearch: {e}")
            return False
    else:
        # In test mode without elastic_client
        print(f"[TEST MODE] Would upload paper: '{paper_title[:60]}...'")

    # Record in bloom filter to prevent future duplicates
    record_in_bloom_filter(paper_title)

    return True


def get_bloom_filter_stats() -> Dict[str, Any]:
    """Get statistics about the current bloom filter."""
    bloom = _load_bloom_filter()
    return {
        "capacity": bloom.capacity,
        "error_rate": bloom.error_rate,
        "count": len(bloom),
        "file_exists": BLOOM_FILTER_FILE.exists(),
        "file_path": str(BLOOM_FILTER_FILE)
    }