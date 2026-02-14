import os
import time
from http.client import IncompleteRead
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from Bio import Entrez
import requests
import tarfile
import io
from tqdm import tqdm
import json

Entrez.email = "sirihaasanallamothu@gmail.com"

output_dir = "output_pmc_papers"
os.makedirs(output_dir, exist_ok=True)
# Clear existing files so each run overwrites the entire directory
for f in os.listdir(output_dir):
    path = os.path.join(output_dir, f)
    if os.path.isfile(path):
        os.remove(path)
print(f"Output directory '{output_dir}' ready (cleared)")

Entrez.api_key = os.getenv("MY_API_KEY")

MAX_RESULTS = 2000
BATCH_SIZE = 50

def fetch_entrez(create_handle, max_retries=5):
    for attempt in range(max_retries):
        try:
            handle = create_handle()
            return Entrez.read(handle)
        except (IncompleteRead, OSError, URLError, socket.timeout) as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"NCBI dropped connection, retrying in {wait}s...")
            time.sleep(wait)

def get_citations_europepmc(pmid):
    """Fetch number of citations from Europe PMC. Returns None if unavailable."""
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:{pmid}+AND+SRC:MED&format=json"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            result = r.json()
            results = result.get('resultList', {}).get('result', [])
            if not results:
                return None
            hit = results[0]
            if 'citedByCount' not in hit:
                return None
            return hit.get('citedByCount', 0)
    except Exception as e:
        print(f"Error fetching citations for {pmid}: {e}")
    return None

def fetch_pubmed_abstracts(pmids_batch):
    return fetch_entrez(
        lambda: Entrez.efetch(
            db="pubmed",
            id=",".join(pmids_batch),
            rettype="medline",
            retmode="xml"
        )
    )



query = (
    '('
        '"Postural Orthostatic Tachycardia Syndrome"[MeSH Terms] OR '
        '"Post-Acute COVID-19 Syndrome"[MeSH Terms] OR '
        '"COVID-19"[MeSH Terms] OR '
        '"Cardiovascular Diseases"[MeSH Terms] OR '
        '"Heart"[MeSH Terms] OR '
        '"Drug Discovery"[MeSH Terms] OR '
        '"High-Throughput Screening"[MeSH Terms] OR '
        '"Computational Biology"[MeSH Terms] OR '
        '"Clinical Trials as Topic"[MeSH Terms] OR '
        '"Neoplasms"[MeSH Terms] OR '
        '"Oncology"[MeSH Terms] OR '
        '"Cancer"[MeSH Terms] OR '
        '"Early Detection of Cancer"[MeSH Terms] OR '
        '"Infectious Diseases"[MeSH Terms] OR '
        '"Dementia"[MeSH Terms] OR '
        '"Brain"[MeSH Terms] OR '
        '"Cognition Disorders"[MeSH Terms] OR '
        '"Cognitive Dysfunction"[MeSH Terms] OR '
        '"Uric Acid"[MeSH Terms] OR '
        '"Hyperuricemia"[MeSH Terms] OR '
        '"Autonomic Nervous System Diseases"[MeSH Terms] OR '
        '"Neuroinflammatory Diseases"[MeSH Terms] OR '
        '"Alzheimer Disease"[MeSH Terms] OR '
        '"Parkinson Disease"[MeSH Terms] OR '
        '"Diabetes Mellitus"[MeSH Terms] OR '
        '"Hypertension"[MeSH Terms] OR '
        '"Obesity"[MeSH Terms] OR '
        '"Risk Assessment"[MeSH Terms] OR '
        '"Cardiovascular Diseases/diagnosis"[MeSH Terms] OR '
        '"Diagnostic Imaging"[MeSH Terms] OR '
        '"Image Processing, Computer-Assisted"[MeSH Terms]'
    ')'
)

# ------------------------------
# Search and fetch until we have MAX_RESULTS valid papers
# ------------------------------
TARGET_COUNT = 2000  # set to MAX_RESULTS for full run
retmax_search = 1000  # fetch extra PMIDs to account for skips
saved_count = 0

print("Searching PubMed...")
record = fetch_entrez(lambda: Entrez.esearch(db="pubmed", term=query, retmax=retmax_search))
pmids = record["IdList"]
print(f"Found {len(pmids)} PMIDs, collecting up to {TARGET_COUNT} with data...")

# ------------------------------
# Fetch abstracts and metadata
# ------------------------------
for i in tqdm(range(0, len(pmids), BATCH_SIZE)):
    if saved_count >= TARGET_COUNT:
        break
    batch_pmids = pmids[i:i+BATCH_SIZE]
    records = fetch_pubmed_abstracts(batch_pmids)

    for article in records.get("PubmedArticle", []):
        if saved_count >= TARGET_COUNT:
            break
        pmid = article["MedlineCitation"]["PMID"]
        article_data = article["MedlineCitation"]["Article"]

        # Title
        title = article_data.get("ArticleTitle", "").strip()

        # Abstract
        abstract_text = ""
        if "Abstract" in article_data and "AbstractText" in article_data["Abstract"]:
            parts = article_data["Abstract"]["AbstractText"]
            abstract_text = "\n".join(str(p) for p in parts)

        # Skip if no meaningful data
        if not title and not abstract_text.strip():
            continue

        # Journal & publication year
        journal_data = article_data.get("Journal", {})
        journal = journal_data.get("Title", "")
        pub_year = ""
        if "JournalIssue" in journal_data and "PubDate" in journal_data["JournalIssue"]:
            pubdate = journal_data["JournalIssue"]["PubDate"]
            pub_year = pubdate.get("Year", "")

        # DOI
        doi = ""
        if "ELocationID" in article_data:
            for eid in article_data["ELocationID"]:
                if eid.attributes.get("EIdType") == "doi":
                    doi = str(eid)

        # Authors
        authors_list = []
        for author in article_data.get("AuthorList", []):
            last = author.get("LastName")
            first = author.get("ForeName") or author.get("Initials")
            if last and first:
                authors_list.append(f"{last}, {first}")

        # Number of authors
        num_authors = len(authors_list)

        # Citation count - only if available
        citations = get_citations_europepmc(pmid)

        # ------------------------------
        # Build JSON
        # ------------------------------
        paper_json = {
            "pmid": pmid,
            "title": title,
            "abstract": abstract_text,
            "publication_year": pub_year,
            "journal": journal,
            "doi": doi,
            "authors": authors_list,
            "num_authors": num_authors,
        }
        if citations is not None:
            paper_json["citations"] = citations

        # Save JSON per paper
        json_file = os.path.join(output_dir, f"PMID_{pmid}.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(paper_json, f, indent=4)

        saved_count += 1

    time.sleep(0.5)  # polite delay

print(f"Saved {saved_count} papers to {output_dir}")



# # ------------------------------
# def fetch_entrez(create_handle, max_retries=5):
#     for attempt in range(max_retries):
#         try:
#             handle = create_handle()
#             return Entrez.read(handle)
#         except (IncompleteRead, OSError, URLError, socket.timeout) as e:
#             if attempt == max_retries - 1:
#                 raise
#             wait = 2 ** attempt
#             print(f"NCBI dropped connection, retrying in {wait}s...")
#             time.sleep(wait)

# # ------------------------------
# # Extended query
# # ------------------------------
# query = (
#     '('
#         '"Postural Orthostatic Tachycardia Syndrome"[MeSH Terms] OR '
#         '"Post-Acute COVID-19 Syndrome"[MeSH Terms] OR '
#         '"COVID-19"[MeSH Terms] OR '
#         '"Cardiovascular Diseases"[MeSH Terms] OR '
#         '"Heart"[MeSH Terms] OR '
#         '"Drug Discovery"[MeSH Terms] OR '
#         '"High-Throughput Screening"[MeSH Terms] OR '
#         '"Computational Biology"[MeSH Terms] OR '
#         '"Clinical Trials as Topic"[MeSH Terms] OR '
#         '"Neoplasms"[MeSH Terms] OR '
#         '"Oncology"[MeSH Terms] OR '
#         '"Cancer"[MeSH Terms] OR '
#         '"Early Detection of Cancer"[MeSH Terms] OR '
#         '"Infectious Diseases"[MeSH Terms] OR '
#         '"Dementia"[MeSH Terms] OR '
#         '"Brain"[MeSH Terms] OR '
#         '"Cognition Disorders"[MeSH Terms] OR '
#         '"Cognitive Dysfunction"[MeSH Terms] OR '
#         '"Uric Acid"[MeSH Terms] OR '
#         '"Hyperuricemia"[MeSH Terms] OR '
#         '"Autonomic Nervous System Diseases"[MeSH Terms] OR '
#         '"Neuroinflammatory Diseases"[MeSH Terms] OR '
#         '"Alzheimer Disease"[MeSH Terms] OR '
#         '"Parkinson Disease"[MeSH Terms] OR '
#         '"Diabetes Mellitus"[MeSH Terms] OR '
#         '"Hypertension"[MeSH Terms] OR '
#         '"Obesity"[MeSH Terms] OR '
#         '"Risk Assessment"[MeSH Terms] OR '
#         '"Cardiovascular Diseases/diagnosis"[MeSH Terms] OR '
#         '"Diagnostic Imaging"[MeSH Terms] OR '
#         '"Image Processing, Computer-Assisted"[MeSH Terms]'
#     ')'
# )
# # ------------------------------
# # STEP 1: Search PubMed
# # ------------------------------
# print("Searching PubMed...")
# MAX_RESULTS = 2000
# record = fetch_entrez(lambda: Entrez.esearch(db="pubmed", term=query, retmax=MAX_RESULTS))
# pmids = record["IdList"]

# # Save PMIDs
# pubmed_file = os.path.join(output_dir, "pubmed_ids.txt")
# with open(pubmed_file, "w") as f:
#     for pmid in pmids:
#         f.write(pmid + "\n")

# print(f"Saved {len(pmids)} PMIDs to {pubmed_file}")

# time.sleep(1)
# def fetch_pubmed_abstracts(pmids_batch):
#     return fetch_entrez(
#         lambda: Entrez.efetch(
#             db="pubmed",
#             id=",".join(pmids_batch),
#             rettype="medline",
#             retmode="xml"
#         )
#     )

# print("Fetching abstracts and titles...")
# batch_size = 50
# for i in tqdm(range(0, len(pmids), batch_size)):
#     batch_pmids = pmids[i:i+batch_size]
#     records = fetch_pubmed_abstracts(batch_pmids)

#     for article in records["PubmedArticle"]:
#         pmid = article["MedlineCitation"]["PMID"]
#         article_data = article["MedlineCitation"]["Article"]

#         # Title
#         title = article_data.get("ArticleTitle", "").strip()

#         # Abstract
#         abstract_text = ""
#         if "Abstract" in article_data and "AbstractText" in article_data["Abstract"]:
#             parts = article_data["Abstract"]["AbstractText"]
#             abstract_text = "\n".join(str(p) for p in parts)

#         # Journal

#         journal_data = article_data.get("Journal")
#         if journal_data:
#             if isinstance(journal_data, dict):
#                 journal = journal_data.get("Title", "")
#             elif isinstance(journal_data, list) and len(journal_data) > 0:
#                 journal = journal_data[0].get("Title", "")

#         # Authors
#         authors_list = []
#         for author in article_data.get("AuthorList", []):
#             last = author.get("LastName")
#             first = author.get("ForeName") or author.get("Initials")
#             if last and first:
#                 authors_list.append(f"{last}, {first}")
#         authors_str = "; ".join(authors_list)

#         # Save each paper to its own file
#         paper_file = os.path.join(output_dir, f"PMID_{pmid}.txt")
#         with open(paper_file, "w", encoding="utf-8") as f:
#             f.write(f"PMID: {pmid}\n")
#             f.write(f"Title: {title}\n")
#             f.write(f"Journal: {journal}\n")
#             f.write(f"Authors: {authors_str}\n\n")
#             f.write(f"Abstract:\n{abstract_text}\n")

#     time.sleep(0.5)  # polite delay to NCBI
