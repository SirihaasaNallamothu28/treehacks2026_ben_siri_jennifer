"""
Example usage of the upload.py module with Elasticsearch integration.

This demonstrates how to use the bloom filter-based deduplication
when uploading papers to Elasticsearch.
"""

from elasticsearch import Elasticsearch
from upload import upload, get_bloom_filter_stats
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Example of uploading papers with deduplication."""

    # Initialize Elasticsearch client (uncomment when you have credentials)
    # es = Elasticsearch(
    #     cloud_id=os.getenv("ELASTIC_CLOUD_ID"),
    #     api_key=os.getenv("ELASTIC_API_KEY")
    # )

    # For now, we'll use None to run in test mode
    es = None

    # Sample papers to upload
    papers = [
        {
            "title": "The Role of Artificial Intelligence in Modern Healthcare",
            "abstract": "This comprehensive review examines the current applications of AI...",
            "authors": ["John Doe", "Jane Smith"],
            "journal": "Journal of Medical AI",
            "year": 2024,
            "doi": "10.1234/jmai.2024.001"
        },
        {
            "title": "Machine Learning for Drug Discovery",
            "abstract": "We present a novel machine learning approach for identifying...",
            "authors": ["Alice Johnson", "Bob Williams"],
            "journal": "Nature Biotechnology",
            "year": 2024,
            "doi": "10.1038/nbt.2024.002"
        },
        {
            "title": "The Role of Artificial Intelligence in Modern Healthcare",  # Duplicate
            "abstract": "Different abstract but same title - should be caught by bloom filter",
            "authors": ["Different Authors"],
            "journal": "Different Journal",
            "year": 2025,
            "doi": "10.1234/different.001"
        }
    ]

    print("Starting paper upload process...")
    print(f"Papers to process: {len(papers)}\n")

    # Upload each paper
    uploaded_count = 0
    skipped_count = 0

    for i, paper in enumerate(papers, 1):
        print(f"Processing paper {i}/{len(papers)}: '{paper['title'][:50]}...'")

        success = upload(paper, elastic_client=es, index_name="research_papers")

        if success:
            uploaded_count += 1
        else:
            skipped_count += 1

        print()

    # Print summary
    print("=" * 70)
    print("Upload Summary")
    print("=" * 70)
    print(f"Total papers processed: {len(papers)}")
    print(f"Successfully uploaded: {uploaded_count}")
    print(f"Skipped (duplicates): {skipped_count}")
    print()

    # Show bloom filter statistics
    stats = get_bloom_filter_stats()
    print("Bloom Filter Statistics:")
    print(f"  Total entries recorded: {stats['count']}")
    print(f"  Capacity: {stats['capacity']}")
    print(f"  Usage: {stats['count'] / stats['capacity'] * 100:.2f}%")
    print(f"  Error rate: {stats['error_rate'] * 100:.2f}%")
    print(f"  Storage location: {stats['file_path']}")
    print("=" * 70)


if __name__ == "__main__":
    main()
