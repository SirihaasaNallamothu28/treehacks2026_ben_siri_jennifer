"""
Test to verify abstract extraction and upload
"""

import os
import json
from dotenv import load_dotenv
from Bio import Entrez

load_dotenv()

# Import functions
from upload_documents import (
    extract_document_info,
    fetch_pubmed_abstracts,
    fetch_entrez_with_retry
)

# Configure Entrez
Entrez.email = "sirihaasanallamothu@gmail.com"
Entrez.api_key = os.getenv("MY_API_KEY")

def test_abstract_extraction_detailed():
    """Test abstract extraction in detail"""

    print("\n" + "="*80)
    print("TESTING ABSTRACT EXTRACTION")
    print("="*80)

    # Search for a paper we just uploaded
    print("\nSearching for 'brain scan CNN' papers...")
    search_results = fetch_entrez_with_retry(
        lambda: Entrez.esearch(
            db="pubmed",
            term="brain scan CNN",
            retmax=5
        )
    )

    pmids = search_results.get("IdList", [])
    print(f"Found PMIDs: {pmids[:5]}")

    # Fetch first 2 papers
    test_pmids = pmids[:2]
    records = fetch_pubmed_abstracts(test_pmids)

    for article in records.get("PubmedArticle", []):
        print("\n" + "="*80)

        # Get raw article data
        pmid = str(article["MedlineCitation"]["PMID"])
        article_data = article["MedlineCitation"]["Article"]

        print(f"PMID: {pmid}")
        print("-"*80)

        # Check if abstract exists in raw data
        if "Abstract" in article_data:
            print("✓ Abstract field EXISTS in article data")
            abstract = article_data["Abstract"]
            print(f"  Abstract keys: {abstract.keys()}")

            if "AbstractText" in abstract:
                print("✓ AbstractText field EXISTS")
                parts = abstract["AbstractText"]
                print(f"  Type: {type(parts)}")
                print(f"  Length: {len(parts) if isinstance(parts, list) else 'single element'}")

                # Show raw abstract
                if isinstance(parts, list):
                    for i, part in enumerate(parts):
                        print(f"\n  Part {i+1}:")
                        print(f"    Has attributes: {hasattr(part, 'attributes')}")
                        if hasattr(part, 'attributes'):
                            print(f"    Attributes: {part.attributes}")
                        text = str(part)
                        print(f"    Length: {len(text)} characters")
                        print(f"    Preview: {text[:100]}...")
                else:
                    text = str(parts)
                    print(f"  Single element length: {len(text)} characters")
                    print(f"  Preview: {text[:100]}...")
            else:
                print("✗ NO AbstractText field!")
        else:
            print("✗ NO Abstract field in article data!")

        # Now test our extraction function
        print("\n" + "-"*80)
        print("TESTING extract_document_info():")
        print("-"*80)

        document = extract_document_info(article)

        # Check what we got
        print(f"\nExtracted fields:")
        print(f"  pmid: {document['pmid']}")
        print(f"  title: {document['title'][:80]}...")
        print(f"  title length: {len(document['title'])} chars")

        # Check title_abstract_semantic
        semantic = document['title_abstract_semantic']
        print(f"\n  title_abstract_semantic:")
        print(f"    Length: {len(semantic)} characters")
        print(f"    Word count: {len(semantic.split())} words")

        # Check if it's just the title (which would mean abstract is empty)
        if len(semantic) <= len(document['title']) + 10:
            print("    ⚠️  WARNING: Appears to be TITLE ONLY - abstract may be missing!")
            print(f"    Content: {semantic}")
        else:
            print("    ✓ Contains more than just title")
            print(f"    First 200 chars: {semantic[:200]}...")
            print(f"    Last 200 chars: ...{semantic[-200:]}")

        # Show the full document that would be uploaded
        print("\n" + "-"*80)
        print("DOCUMENT JSON TO BE UPLOADED:")
        print("-"*80)
        print(json.dumps(document, indent=2))

        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_abstract_extraction_detailed()
