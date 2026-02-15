"""
Test what data is actually being sent to Elasticsearch
"""

import os
import json
from dotenv import load_dotenv
from Bio import Entrez

load_dotenv()

# Import extraction functions
from upload_documents import extract_document_info, fetch_pubmed_abstracts, fetch_entrez_with_retry

# Configure Entrez
Entrez.email = "sirihaasanallamothu@gmail.com"
Entrez.api_key = os.getenv("MY_API_KEY")

def test_elasticsearch_payload():
    """Test what's actually being sent to Elasticsearch"""

    # Get a known article
    print("Searching for diabetes articles...")
    search_results = fetch_entrez_with_retry(
        lambda: Entrez.esearch(
            db="pubmed",
            term="diabetes",
            retmax=2
        )
    )

    pmids = search_results.get("IdList", [])
    print(f"Testing with PMIDs: {pmids}\n")

    # Fetch and extract
    records = fetch_pubmed_abstracts(pmids)

    for article in records.get("PubmedArticle", []):
        document = extract_document_info(article)

        print("="*80)
        print(f"PMID: {document['pmid']}")
        print("="*80)

        # Check each field
        print(f"\nTitle length: {len(document['title'])} characters")
        print(f"Title: {document['title'][:100]}...")

        # Check the abstract from the raw data
        article_data = article["MedlineCitation"]["Article"]
        if "Abstract" in article_data and "AbstractText" in article_data["Abstract"]:
            parts = article_data["Abstract"]["AbstractText"]
            raw_abstract = "\n".join(str(p) for p in parts)
            print(f"\nRaw abstract length: {len(raw_abstract)} characters")
            print(f"Raw abstract word count: {len(raw_abstract.split())} words")

        # Check what's in title_abstract_semantic
        print(f"\ntitle_abstract_semantic length: {len(document['title_abstract_semantic'])} characters")
        print(f"title_abstract_semantic word count: {len(document['title_abstract_semantic'].split())} words")

        # Show structure
        print(f"\nFirst 500 chars of title_abstract_semantic:")
        print(document['title_abstract_semantic'][:500])
        print("...")
        print(f"\nLast 500 chars of title_abstract_semantic:")
        print("..." + document['title_abstract_semantic'][-500:])

        # Check JSON serialization size
        json_payload = json.dumps(document, indent=2)
        print(f"\nJSON payload size: {len(json_payload)} bytes")
        print(f"JSON payload size: {len(json_payload)/1024:.2f} KB")

        # Check if there are any size limits we might be hitting
        if len(document['title_abstract_semantic']) > 10000:
            print("\n⚠️  WARNING: title_abstract_semantic is over 10KB")
        if len(json_payload) > 100000:
            print("\n⚠️  WARNING: JSON payload is over 100KB")

        print("\n" + "="*80 + "\n")

        # Show the full document structure
        print("Full document structure:")
        print(json.dumps(document, indent=2)[:2000])
        print("...\n")

if __name__ == "__main__":
    test_elasticsearch_payload()
