"""
Test script for upload_documents.py

This script tests:
1. PubMed document retrieval
2. Document information extraction
3. Elasticsearch upload functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the functions to test
from upload_documents import (
    fetch_entrez_with_retry,
    fetch_pubmed_abstracts,
    extract_document_info,
    upload_to_elasticsearch,
    upload_documents_from_keyword_query
)

def test_pubmed_retrieval():
    """Test that we can retrieve documents from PubMed"""
    print("\n" + "="*60)
    print("TEST 1: PubMed Document Retrieval")
    print("="*60)

    try:
        from Bio import Entrez

        # First, search for a few recent documents
        print("Searching PubMed for recent diabetes articles...")
        search_results = fetch_entrez_with_retry(
            lambda: Entrez.esearch(
                db="pubmed",
                term="diabetes",
                retmax=3,
                sort="relevance"
            )
        )

        test_pmids = search_results.get("IdList", [])

        if not test_pmids:
            print("✗ No PMIDs found from search")
            return False, None

        print(f"Found PMIDs: {test_pmids}")
        print(f"Fetching details for {len(test_pmids)} articles...")

        records = fetch_pubmed_abstracts(test_pmids)

        if records and "PubmedArticle" in records:
            num_articles = len(records["PubmedArticle"])
            print(f"✓ Successfully retrieved {num_articles} articles")
            return True, records
        else:
            print("✗ No articles found in response")
            return False, None

    except Exception as e:
        print(f"✗ Error retrieving documents: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_document_extraction(records):
    """Test document information extraction"""
    print("\n" + "="*60)
    print("TEST 2: Document Information Extraction")
    print("="*60)

    if not records or "PubmedArticle" not in records:
        print("✗ No records to extract from")
        return False

    try:
        articles = records["PubmedArticle"]
        if not articles:
            print("✗ No articles in records")
            return False

        article = articles[0]
        document = extract_document_info(article)

        # Verify all required fields are present
        required_fields = ["pmid", "title", "publication_year", "journal",
                          "title_abstract_semantic", "authors", "pub_year", "doi"]

        print("\nExtracted document fields:")
        for field in required_fields:
            if field in document:
                value = document[field]
                # Truncate long values for display
                display_value = (value[:50] + "...") if isinstance(value, str) and len(value) > 50 else value
                print(f"  {field}: {display_value}")
            else:
                print(f"  {field}: MISSING!")
                return False

        print("\n✓ All required fields extracted successfully")
        return True, document

    except Exception as e:
        print(f"✗ Error extracting document info: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_elasticsearch_upload(document):
    """Test Elasticsearch upload"""
    print("\n" + "="*60)
    print("TEST 3: Elasticsearch Upload")
    print("="*60)

    # Check if Elasticsearch credentials are configured
    es_url = os.getenv("ELASTICSEARCH_URL")
    es_api_key = os.getenv("ELASTICSEARCH_API_KEY")

    if not es_url or not es_api_key:
        print("⚠ Elasticsearch credentials not configured")
        print(f"  ELASTICSEARCH_URL: {'Set' if es_url else 'NOT SET'}")
        print(f"  ELASTICSEARCH_API_KEY: {'Set' if es_api_key else 'NOT SET'}")
        print("\nSkipping actual upload test (would fail without credentials)")
        return None

    if not document:
        print("✗ No document to upload")
        return False

    try:
        print(f"Attempting to upload PMID {document['pmid']}...")
        success = upload_to_elasticsearch(document)

        if success:
            print("✓ Document uploaded successfully")
            return True
        else:
            print("✗ Document upload failed")
            return False

    except Exception as e:
        print(f"✗ Error during upload: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_workflow():
    """Test the complete workflow with a simple query"""
    print("\n" + "="*60)
    print("TEST 4: Full Workflow Test")
    print("="*60)

    # Check if Elasticsearch is configured
    es_url = os.getenv("ELASTICSEARCH_URL")
    es_api_key = os.getenv("ELASTICSEARCH_API_KEY")

    if not es_url or not es_api_key:
        print("⚠ Elasticsearch not configured, skipping full workflow test")
        return None

    try:
        # Use a very specific query to get a small number of results
        test_query = "cancer AND 2024[PDAT]"
        print(f"Testing with query: '{test_query}'")
        print("This will search, extract, and upload documents...\n")

        # This will run the full pipeline
        upload_documents_from_keyword_query(test_query)

        print("\n✓ Full workflow completed")
        return True

    except Exception as e:
        print(f"✗ Error in full workflow: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "#"*60)
    print("# UPLOAD DOCUMENTS TEST SUITE")
    print("#"*60)

    results = {}

    # Test 1: PubMed Retrieval
    success, records = test_pubmed_retrieval()
    results["PubMed Retrieval"] = success

    # Test 2: Document Extraction (only if retrieval succeeded)
    if success and records:
        success, document = test_document_extraction(records)
        results["Document Extraction"] = success

        # Test 3: Elasticsearch Upload (only if extraction succeeded)
        if success and document:
            upload_result = test_elasticsearch_upload(document)
            if upload_result is not None:
                results["Elasticsearch Upload"] = upload_result
    else:
        results["Document Extraction"] = False
        print("\nSkipping extraction test (retrieval failed)")

    # Test 4: Full Workflow (optional, only if ES is configured)
    # Commenting this out by default as it uploads 50 documents
    # Uncomment to test the full pipeline
    # workflow_result = test_full_workflow()
    # if workflow_result is not None:
    #     results["Full Workflow"] = workflow_result

    # Print summary
    print("\n" + "#"*60)
    print("# TEST SUMMARY")
    print("#"*60)

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")

    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)

    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    print("#"*60 + "\n")

    return all(results.values())


if __name__ == "__main__":
    try:
        all_passed = run_all_tests()
        sys.exit(0 if all_passed else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
