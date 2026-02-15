import os
import time
from Bio import Entrez
import requests
from typing import List, Dict

# Configure Entrez
Entrez.email = "sirihaasanallamothu@gmail.com"
Entrez.api_key = os.getenv("MY_API_KEY", "MY_API_KEY")

# Elasticsearch configuration (to be populated with actual credentials)
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "https://synapsis-c99bf6.es.us-central1.gcp.elastic.cloud")
ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")


def fetch_entrez_with_retry(create_handle, max_retries=5):
    """Helper function to fetch from NCBI with retry logic."""
    for attempt in range(max_retries):
        try:
            handle = create_handle()
            return Entrez.read(handle)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"NCBI connection error, retrying in {wait}s... ({e})")
            time.sleep(wait)


def fetch_pubmed_abstracts(pmids_batch: List[str]):
    """Fetch abstracts and metadata for a batch of PMIDs."""
    return fetch_entrez_with_retry(
        lambda: Entrez.efetch(
            db="pubmed",
            id=",".join(pmids_batch),
            rettype="medline",
            retmode="xml"
        )
    )


def extract_document_info(article) -> Dict:
    """Extract relevant information from a PubMed article."""
    pmid = str(article["MedlineCitation"]["PMID"])
    article_data = article["MedlineCitation"]["Article"]

    # Extract title
    title = article_data.get("ArticleTitle", "")

    # Extract abstract
    abstract_text = ""
    if "Abstract" in article_data and "AbstractText" in article_data["Abstract"]:
        parts = article_data["Abstract"]["AbstractText"]
        abstract_text = "\n".join(str(p) for p in parts)

    # Extract journal and publication year
    journal_data = article_data.get("Journal", {})
    journal = journal_data.get("Title", "")
    pub_year = ""
    if "JournalIssue" in journal_data and "PubDate" in journal_data["JournalIssue"]:
        pubdate = journal_data["JournalIssue"]["PubDate"]
        pub_year = str(pubdate.get("Year", ""))

    # Extract DOI
    doi = ""
    if "ELocationID" in article_data:
        for eid in article_data["ELocationID"]:
            if eid.attributes.get("EIdType") == "doi":
                doi = str(eid)
                break

    # Extract authors
    authors_list = []
    for author in article_data.get("AuthorList", []):
        last = author.get("LastName")
        first = author.get("ForeName") or author.get("Initials")
        if last and first:
            authors_list.append(f"{last}, {first}")
    authors_str = "; ".join(authors_list)

    # Create title_abstract_semantic field (concatenation of title and abstract)
    title_abstract_semantic = f"{title} {abstract_text}"

    return {
        "pmid": pmid,
        "title": title,
        "abstract": abstract_text,  # Add separate abstract field
        "publication_year": pub_year,
        "journal": journal,
        "title_abstract_semantic": title_abstract_semantic,
        "authors": authors_str,
        "pub_year": pub_year,
        "doi": doi
    }


def upload_to_elasticsearch(document: Dict) -> bool:
    """Upload a single document to Elasticsearch."""
    url = f"{ELASTICSEARCH_URL}/papers/_doc?pipeline=paper_embedding_pipeline"
    headers = {
        "Authorization": f"ApiKey {ELASTICSEARCH_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=document, headers=headers, timeout=10)
        if response.status_code in [200, 201]:
            print(f"✓ Uploaded PMID {document['pmid']}")
            return True
        else:
            print(f"✗ Failed to upload PMID {document['pmid']}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error uploading PMID {document['pmid']}: {e}")
        return False


def upload_documents_from_keyword_query(keyword_query):
    """
    This function should upload the top 50 documents for the query to the Elastic vector database.

    Here is the POST format:

    POST /papers/_doc?pipeline=paper_embedding_pipeline
    {
        "pmid": "",
        "title": "",
        "publication_year": "",
        "journal": "",
        "title_abstract_semantic": "",
        "authors": "",
        "pub_year": "",
        "doi": ""
    }

    You should use the functions in pubmed_extractor.py to extract the relevant information (abstract, title, and metadata)from the documents.

    Then, you should run the post request above for each document

    :param keyword_query: Text query
    """
    print(f"Searching PubMed for: {keyword_query}")

    # Step 1: Search PubMed for the query
    try:
        search_results = fetch_entrez_with_retry(
            lambda: Entrez.esearch(
                db="pubmed",
                term=keyword_query,
                retmax=50,
                sort="relevance"
            )
        )
        pmids = search_results.get("IdList", [])

        if not pmids:
            print("No results found for the query.")
            return

        print(f"Found {len(pmids)} documents")

    except Exception as e:
        print(f"Error searching PubMed: {e}")
        return

    # Step 2: Fetch abstracts and metadata in batches
    batch_size = 10
    uploaded_count = 0
    failed_count = 0

    for i in range(0, len(pmids), batch_size):
        batch_pmids = pmids[i:i + batch_size]

        try:
            # Fetch metadata for this batch
            records = fetch_pubmed_abstracts(batch_pmids)

            # Process each article in the batch
            for article in records.get("PubmedArticle", []):
                try:
                    # Extract document information
                    document = extract_document_info(article)

                    # Skip if no title or abstract
                    if not document["title"] and not document["title_abstract_semantic"]:
                        print(f"Skipping PMID {document['pmid']} (no title/abstract)")
                        continue

                    # Upload to Elasticsearch
                    if upload_to_elasticsearch(document):
                        uploaded_count += 1
                    else:
                        failed_count += 1

                except Exception as e:
                    print(f"Error processing article: {e}")
                    failed_count += 1

            # Polite delay between batches
            time.sleep(0.5)

        except Exception as e:
            print(f"Error fetching batch: {e}")
            failed_count += len(batch_pmids)

    # Summary
    print(f"\n{'='*50}")
    print(f"Upload complete!")
    print(f"Successfully uploaded: {uploaded_count} documents")
    print(f"Failed: {failed_count} documents")
    print(f"{'='*50}")