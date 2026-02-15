"""
Test file for perplexity_analysis module
Run this file to test the various analysis functions
"""

from perplexity_analysis import (
    get_pmid_by_index,
    load_paper_json,
    analyze_with_perplexity,
    batch_analyze_papers
)


def test_single_paper_medium_json(index=0, analysis_type="summarize_medium_text"):
    """Test analyzing a single paper"""
    print("=" * 80)
    print("TEST 1: Single Paper Analysis")
    print("=" * 80)

    # Load one paper by index
    pmid = get_pmid_by_index(index)  # Get first paper's PMID
    paper = load_paper_json(pmid)

    print(f"\nTitle: {paper['title']}")
    print(f"Authors: {', '.join(paper['authors'][:3])}")
    print(f"Journal: {paper['journal']}")
    print(f"Year: {paper['publication_year']}")
    print(f"Abstract length: {len(paper['abstract'])} characters\n")

    # Analyze with Perplexity
    print("Getting summary from Perplexity...")
    summary = analyze_with_perplexity(paper, analysis_type)
    print(f"\nSummary:\n{summary}\n")


def test_single_paper_medium_text():
    """Test analyzing a single paper with medium text output"""
    print("=" * 80)
    print("TEST 2: Single Paper Analysis (Medium Text)")
    print("=" * 80)

    # Load second paper
    pmid = get_pmid_by_index(1)
    paper = load_paper_json(pmid)

    print(f"\nTitle: {paper['title'][:60]}...")
    print(f"PMID: {pmid}\n")

    # Analyze with Perplexity (text only)
    print("Getting text-only summary from Perplexity...")
    summary = analyze_with_perplexity(paper, "summarize_medium_text")
    print(f"\nSummary:\n{summary}\n")


def test_single_paper_short_json():
    """Test analyzing a single paper with short JSON output"""
    print("=" * 80)
    print("TEST 3: Single Paper Analysis (Short JSON)")
    print("=" * 80)

    # Load third paper
    pmid = get_pmid_by_index(2)
    paper = load_paper_json(pmid)

    print(f"\nTitle: {paper['title'][:60]}...")
    print(f"PMID: {pmid}\n")

    # Analyze with Perplexity (short version)
    print("Getting short summary from Perplexity...")
    summary = analyze_with_perplexity(paper, "summarize_short_json")
    print(f"\nSummary:\n{summary}\n")


def test_batch_analysis():
    """Test batch analyzing multiple papers"""
    print("=" * 80)
    print("TEST 4: Batch Analysis (3 papers)")
    print("=" * 80)

    results = batch_analyze_papers(limit=3, analysis_type="summarize_medium_text")

    print(f"\nCompleted batch analysis of {len(results)} papers")
    for i, result in enumerate(results, 1):
        print(f"{i}. PMID {result['pmid']}: {result['title'][:50]}...")


def test_specific_pmid():
    """Test loading a specific PMID directly"""
    print("=" * 80)
    print("TEST 5: Load Specific PMID")
    print("=" * 80)

    # Get PMID from index 0 to use as example
    pmid = get_pmid_by_index(0)
    print(f"\nLoading PMID: {pmid}")

    paper = load_paper_json(pmid)
    print(f"Successfully loaded: {paper['title'][:60]}...")
    print(f"Authors: {len(paper['authors'])} authors")
    print(f"Year: {paper['publication_year']}")


def run_all_tests():
    """Run all tests"""
    tests = [
        ("Single Paper (Medium JSON)", test_single_paper_medium_json),
        ("Single Paper (Medium Text)", test_single_paper_medium_text),
        ("Single Paper (Short JSON)", test_single_paper_short_json),
        ("Batch Analysis", test_batch_analysis),
        ("Specific PMID", test_specific_pmid),
    ]

    print("\n" + "=" * 80)
    print("PERPLEXITY ANALYSIS TEST SUITE")
    print("=" * 80)
    print(f"\nRunning {len(tests)} tests...\n")

    for i, (name, test_func) in enumerate(tests, 1):
        try:
            print(f"\n[{i}/{len(tests)}] Running: {name}")
            test_func()
            print(f"✓ {name} - PASSED")
        except Exception as e:
            print(f"✗ {name} - FAILED")
            print(f"Error: {e}")

    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    # You can run individual tests or all tests
    # Uncomment the test you want to run:

    # Run single test
    test_single_paper_medium_json(2, "summarize_medium_text")

    # Or run all tests (warning: will use more API credits)
    # run_all_tests()
