# Paper Upload with Bloom Filter Deduplication

This module provides efficient paper deduplication using a Bloom filter before uploading to Elasticsearch.

## Overview

The `upload.py` module implements a Bloom filter-based deduplication system designed to handle 20,000+ research papers. It prevents duplicate papers from being uploaded to Elasticsearch by checking paper titles against a probabilistic data structure.

## Key Features

- **Efficient Deduplication**: Uses a Bloom filter with 1% false positive rate
- **Persistent Storage**: Bloom filter is saved to disk (`bloom_filter.pkl`) and automatically reloaded
- **Case-Insensitive Matching**: Normalizes titles to catch duplicates regardless of capitalization
- **Scalable Design**: Configured for 20,000 papers with room to grow
- **Test Mode**: Can run without Elasticsearch for testing

## File Structure

- `upload.py` - Main module with upload and bloom filter functions
- `bloom_filter.pkl` - Persistent bloom filter data (auto-generated)
- `test_bloom_filter.py` - Comprehensive test suite
- `example_usage.py` - Example integration with Elasticsearch

## Configuration

The bloom filter is configured in `upload.py`:

```python
BLOOM_FILTER_CAPACITY = 20000  # Expected number of papers
BLOOM_FILTER_ERROR_RATE = 0.01  # 1% false positive rate
```

### Bloom Filter Parameters

For 20,000 papers:
- **Capacity**: 20,000 entries
- **Error Rate**: 0.01 (1% false positive rate)
- **Storage**: ~24KB on disk
- **Memory**: Efficient bit array representation

## API Functions

### `upload(paper_json, elastic_client=None, index_name="papers")`

Main function to upload a paper with deduplication.

**Parameters:**
- `paper_json` (dict): Paper data with at least a 'title' field
- `elastic_client` (Elasticsearch, optional): ES client instance
- `index_name` (str): Target index name

**Returns:**
- `bool`: True if uploaded, False if duplicate or error

**Example:**
```python
from elasticsearch import Elasticsearch
from upload import upload

es = Elasticsearch(cloud_id="...", api_key="...")

paper = {
    "title": "Deep Learning in Healthcare",
    "abstract": "This paper presents...",
    "authors": ["Smith, J."],
    "year": 2024
}

success = upload(paper, elastic_client=es)
```

### `is_recorded_in_bloom_filter(paper_title)`

Check if a title exists in the bloom filter.

**Parameters:**
- `paper_title` (str): Paper title to check

**Returns:**
- `bool`: True if likely duplicate, False if new

### `record_in_bloom_filter(paper_title)`

Add a title to the bloom filter.

**Parameters:**
- `paper_title` (str): Paper title to record

### `get_bloom_filter_stats()`

Get bloom filter statistics.

**Returns:**
- `dict`: Statistics including capacity, count, error_rate

## Testing

### Run Basic Tests

```bash
cd paper_search
python test_bloom_filter.py
```

This runs:
1. **Basic functionality test**: 5 papers with duplicates
2. **Large scale test**: 1,000 unique + 100 duplicate papers

### Expected Output

```
✓ All tests passed!
✓ Large scale test passed!

Bloom filter stats:
  Count: 1003
  Capacity: 20000
  Usage: 5.0%
```

## Integration with Elasticsearch

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure Elasticsearch credentials:
```bash
# .env file
ELASTIC_CLOUD_ID=your-cloud-id
ELASTIC_API_KEY=your-api-key
```

3. Use the upload function:
```python
from elasticsearch import Elasticsearch
from upload import upload
import os

es = Elasticsearch(
    cloud_id=os.getenv("ELASTIC_CLOUD_ID"),
    api_key=os.getenv("ELASTIC_API_KEY")
)

# Upload with automatic deduplication
for paper in papers:
    upload(paper, elastic_client=es, index_name="research_papers")
```

## How It Works

1. **Title Normalization**: Titles are converted to lowercase and stripped of whitespace
2. **Bloom Filter Check**: Fast O(1) probabilistic lookup
3. **Upload Decision**: If not in bloom filter, proceed with upload
4. **Record Title**: After successful upload, add title to bloom filter
5. **Persist to Disk**: Bloom filter is saved to `bloom_filter.pkl`

## Deduplication Strategy

The system uses **paper title** as the deduplication key because:
- Titles are generally unique identifiers
- More stable than DOIs (which may be missing)
- More practical than full abstract comparison
- Case-insensitive comparison catches minor variations

## Performance

- **Lookup**: O(1) constant time
- **Insert**: O(1) constant time
- **Memory**: ~24KB for 20,000 papers
- **False Positive Rate**: 1% (configurable)
- **False Negative Rate**: 0% (guaranteed)

## Scaling Considerations

Current configuration supports 20,000 papers at 5% usage. To scale:

```python
# For 50,000 papers
BLOOM_FILTER_CAPACITY = 50000

# For lower false positive rate (0.1%)
BLOOM_FILTER_ERROR_RATE = 0.001
```

## Limitations

1. **False Positives**: 1% chance of incorrectly marking a new paper as duplicate
2. **No Deletion**: Bloom filters don't support removing entries
3. **Title-Based Only**: Doesn't catch papers with different titles but same content
4. **Storage Growth**: File size grows with more entries (but remains efficient)

## Troubleshooting

### Reset Bloom Filter

If you need to start fresh:
```bash
rm paper_search/bloom_filter.pkl
```

### Check Statistics

```python
from upload import get_bloom_filter_stats

stats = get_bloom_filter_stats()
print(f"Current entries: {stats['count']}/{stats['capacity']}")
```

## Dependencies

- `pybloom-live>=4.0.0` - Bloom filter implementation
- `elasticsearch>=8.0.0` - Elasticsearch client
- `python-dotenv==1.0.0` - Environment variable management
