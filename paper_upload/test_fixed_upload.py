"""
Test upload with the fixed abstract field
"""

import os
from dotenv import load_dotenv
from Bio import Entrez

load_dotenv()

from upload_documents import (
    extract_document_info,
    fetch_pubmed_abstracts,
    fetch_entrez_with_retry,
    upload_to_elasticsearch
)

Entrez.email = "sirihaasanallamothu@gmail.com"
Entrez.api_key = os.getenv("MY_API_KEY")

def test_upload_with_abstract():
    """Test that abstract field is uploaded correctly"""

    print("\n" + "="*80)
    print("TESTING UPLOAD WITH ABSTRACT FIELD")
    print("="*80)

    # Get a test paper
    print("\nSearching for a test paper...")
    search_results = fetch_entrez_with_retry(
        lambda: Entrez.esearch(
            db="pubmed",
            term="machine learning medical imaging",
            retmax=1
        )
    )

    pmids = search_results.get("IdList", [])
    if not pmids:
        print("No papers found!")
        return

    pmid = pmids[0]
    print(f"Testing with PMID: {pmid}")

    # Fetch and extract
    records = fetch_pubmed_abstracts([pmid])
    article = records["PubmedArticle"][0]
    document = extract_document_info(article)

    # Verify abstract field exists
    print("\n" + "-"*80)
    print("DOCUMENT TO UPLOAD:")
    print("-"*80)
    print(f"PMID: {document['pmid']}")
    print(f"Title: {document['title'][:80]}...")
    print(f"\n✓ Abstract field present: {'abstract' in document}")
    if 'abstract' in document:
        print(f"  Abstract length: {len(document['abstract'])} characters")
        print(f"  Abstract preview: {document['abstract'][:150]}...")

    # Upload to Elasticsearch
    print("\n" + "-"*80)
    print("UPLOADING TO ELASTICSEARCH:")
    print("-"*80)

    success = upload_to_elasticsearch(document)

    if success:
        print("\n✅ SUCCESS! Document uploaded with abstract field")
        print(f"   PMID: {document['pmid']}")
        print(f"   Abstract length: {len(document['abstract'])} chars")
        print(f"   The 'abstract' field should now be visible in Elasticsearch")
    else:
        print("\n❌ FAILED to upload")

    return success

if __name__ == "__main__":
    test_upload_with_abstract()
