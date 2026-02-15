"""
Test script for the bloom filter functionality in upload.py
"""

from upload import (
    is_recorded_in_bloom_filter,
    record_in_bloom_filter,
    upload,
    get_bloom_filter_stats,
    BLOOM_FILTER_FILE
)


def test_bloom_filter():
    """Test the bloom filter with sample paper data."""

    print("=" * 60)
    print("Testing Bloom Filter for Paper Deduplication")
    print("=" * 60)

    # Clean up any existing bloom filter for fresh test
    if BLOOM_FILTER_FILE.exists():
        BLOOM_FILTER_FILE.unlink()
        print("Removed existing bloom filter for clean test\n")

    # Sample paper data
    papers = [
        {
            "title": "Deep Learning for Medical Image Analysis",
            "abstract": "This paper presents a novel deep learning approach...",
            "authors": ["Smith, J.", "Johnson, K."],
            "journal": "Nature Medicine",
            "year": 2024
        },
        {
            "title": "Machine Learning in Healthcare: A Review",
            "abstract": "We review recent advances in machine learning...",
            "authors": ["Brown, A.", "Davis, M."],
            "journal": "JAMA",
            "year": 2024
        },
        {
            "title": "Deep Learning for Medical Image Analysis",  # Duplicate!
            "abstract": "This paper presents a novel deep learning approach...",
            "authors": ["Smith, J.", "Johnson, K."],
            "journal": "Nature Medicine",
            "year": 2024
        },
        {
            "title": "DEEP LEARNING FOR MEDICAL IMAGE ANALYSIS",  # Same title, different case
            "abstract": "Different abstract but same title...",
            "authors": ["Other, X."],
            "journal": "Other Journal",
            "year": 2025
        },
        {
            "title": "Transformers in NLP: State of the Art",
            "abstract": "Natural language processing has been revolutionized...",
            "authors": ["Williams, R."],
            "journal": "ACL",
            "year": 2024
        }
    ]

    # Test 1: Check bloom filter is initially empty
    print("Test 1: Initial bloom filter state")
    stats = get_bloom_filter_stats()
    print(f"  Capacity: {stats['capacity']}")
    print(f"  Error rate: {stats['error_rate']}")
    print(f"  Current count: {stats['count']}")
    print()

    # Test 2: Upload papers and check for duplicates
    print("Test 2: Uploading papers (without Elastic client)")
    print("-" * 60)

    upload_count = 0
    duplicate_count = 0

    for i, paper in enumerate(papers, 1):
        print(f"\nPaper {i}:")
        print(f"  Title: {paper['title']}")

        # Check if already in bloom filter before upload
        is_duplicate = is_recorded_in_bloom_filter(paper['title'])
        print(f"  Already recorded: {is_duplicate}")

        # Try to upload
        success = upload(paper, elastic_client=None)

        if success:
            upload_count += 1
            print(f"  Status: ✓ Would be uploaded")
        else:
            duplicate_count += 1
            print(f"  Status: ✗ Skipped (duplicate)")

    print("\n" + "=" * 60)
    print("Upload Summary")
    print("=" * 60)
    print(f"Total papers processed: {len(papers)}")
    print(f"Successfully uploaded: {upload_count}")
    print(f"Duplicates detected: {duplicate_count}")
    print()

    # Test 3: Verify bloom filter state
    print("Test 3: Final bloom filter state")
    stats = get_bloom_filter_stats()
    print(f"  Count: {stats['count']}")
    print(f"  File exists: {stats['file_exists']}")
    print(f"  File path: {stats['file_path']}")
    print()

    # Test 4: Direct bloom filter checks
    print("Test 4: Direct bloom filter lookup tests")
    print("-" * 60)

    test_titles = [
        ("Deep Learning for Medical Image Analysis", True),
        ("Machine Learning in Healthcare: A Review", True),
        ("Transformers in NLP: State of the Art", True),
        ("This Paper Does Not Exist", False),
        ("Another Non-Existent Paper Title", False),
    ]

    all_passed = True
    for title, expected_exists in test_titles:
        exists = is_recorded_in_bloom_filter(title)
        status = "✓" if exists == expected_exists else "✗"
        all_passed = all_passed and (exists == expected_exists)
        print(f"  {status} '{title[:40]}...'")
        print(f"     Expected: {expected_exists}, Got: {exists}")

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("=" * 60)

    # Test 5: Persistence test
    print("\nTest 5: Testing bloom filter persistence")
    print("-" * 60)

    # Force reload by clearing the global cache
    import upload as upload_module
    upload_module._bloom_filter = None

    # Check that we can still detect previously added papers
    reloaded_check = is_recorded_in_bloom_filter("Machine Learning in Healthcare: A Review")
    print(f"  After reload, can still detect previous paper: {reloaded_check}")

    if reloaded_check:
        print("  ✓ Bloom filter successfully persisted and reloaded")
    else:
        print("  ✗ Bloom filter persistence failed")

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


def test_large_scale():
    """Test with a larger number of papers to verify capacity."""

    print("\n\n" + "=" * 60)
    print("Large Scale Test (Simulating 1000 papers)")
    print("=" * 60)

    # Generate 1000 unique papers
    papers = [
        {
            "title": f"Research Paper on Topic {i}: A Comprehensive Study",
            "abstract": f"This is abstract number {i} discussing important research...",
            "year": 2024
        }
        for i in range(1000)
    ]

    # Add some duplicates
    papers.extend(papers[:100])  # Add first 100 papers again

    print(f"Total papers to process: {len(papers)}")
    print(f"Expected unique: 1000")
    print(f"Expected duplicates: 100")
    print()

    upload_count = 0
    duplicate_count = 0

    for paper in papers:
        if upload(paper, elastic_client=None):
            upload_count += 1
        else:
            duplicate_count += 1

    print(f"\nResults:")
    print(f"  Uploaded: {upload_count}")
    print(f"  Duplicates detected: {duplicate_count}")

    stats = get_bloom_filter_stats()
    print(f"\nBloom filter stats:")
    print(f"  Count: {stats['count']}")
    print(f"  Capacity: {stats['capacity']}")
    print(f"  Usage: {stats['count'] / stats['capacity'] * 100:.1f}%")

    if upload_count == 1000 and duplicate_count == 100:
        print("\n✓ Large scale test passed!")
    else:
        print(f"\n✗ Large scale test failed")
        print(f"  Expected: 1000 uploaded, 100 duplicates")
        print(f"  Got: {upload_count} uploaded, {duplicate_count} duplicates")

    print("=" * 60)


if __name__ == "__main__":
    test_bloom_filter()
    test_large_scale()
