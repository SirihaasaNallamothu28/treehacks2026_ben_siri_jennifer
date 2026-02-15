"""
Search for papers using Elasticsearch Agent API
"""

import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Elasticsearch configuration
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "https://synapsis-c99bf6.es.us-central1.gcp.elastic.cloud")
ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")

def search_papers_with_agent(
    query: str,
    top_k: int = 10,
    min_score: Optional[float] = None,
    filters: Optional[Dict] = None
) -> List[Dict]:
    """
    Search for papers using Elasticsearch Agent API with semantic search.

    This function performs a semantic search on the papers index using the
    title_abstract_semantic_embedding field for vector similarity search.

    Args:
        query (str): Natural language search query
        top_k (int): Number of results to return (default: 10)
        min_score (Optional[float]): Minimum similarity score threshold
        filters (Optional[Dict]): Additional filters (e.g., publication year, journal)

    Returns:
        List[Dict]: List of matching papers with metadata and scores

    Example:
        >>> results = search_papers_with_agent("CNN for brain tumor classification")
        >>> for paper in results:
        >>>     print(f"{paper['title']} - Score: {paper['_score']}")
    """

    if not ELASTICSEARCH_API_KEY:
        raise ValueError("ELASTICSEARCH_API_KEY not set in environment")

    # Construct the search URL
    url = f"{ELASTICSEARCH_URL}/papers/_search"

    # Set up headers
    headers = {
        "Authorization": f"ApiKey {ELASTICSEARCH_API_KEY}",
        "Content-Type": "application/json"
    }

    # Build the search query
    # Using semantic_text search which leverages the embedding pipeline
    search_body = {
        "size": top_k,
        "query": {
            "bool": {
                "must": [
                    {
                        "semantic": {
                            "field": "title_abstract_semantic_embedding",
                            "query": query
                        }
                    }
                ]
            }
        },
        "_source": [
            "pmid",
            "title",
            "abstract",
            "authors",
            "journal",
            "publication_year",
            "doi"
        ]
    }

    # Add filters if provided
    if filters:
        filter_clauses = []

        # Year filter
        if "year_from" in filters or "year_to" in filters:
            range_filter = {"range": {"publication_year": {}}}
            if "year_from" in filters:
                range_filter["range"]["publication_year"]["gte"] = filters["year_from"]
            if "year_to" in filters:
                range_filter["range"]["publication_year"]["lte"] = filters["year_to"]
            filter_clauses.append(range_filter)

        # Journal filter
        if "journal" in filters:
            filter_clauses.append({
                "match": {"journal": filters["journal"]}
            })

        # Author filter
        if "author" in filters:
            filter_clauses.append({
                "match": {"authors": filters["author"]}
            })

        if filter_clauses:
            search_body["query"]["bool"]["filter"] = filter_clauses

    # Add minimum score threshold if provided
    if min_score is not None:
        search_body["min_score"] = min_score

    try:
        # Execute the search
        response = requests.post(url, json=search_body, headers=headers, timeout=30)
        response.raise_for_status()

        # Parse results
        results_data = response.json()
        hits = results_data.get("hits", {}).get("hits", [])

        # Format results
        papers = []
        for hit in hits:
            paper = hit.get("_source", {})
            paper["_score"] = hit.get("_score")
            paper["_id"] = hit.get("_id")
            papers.append(paper)

        return papers

    except requests.exceptions.RequestException as e:
        print(f"Error searching papers: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return []


def search_papers_with_keyword(
    query: str,
    top_k: int = 10,
    search_fields: Optional[List[str]] = None
) -> List[Dict]:
    """
    Search for papers using keyword-based search (BM25).

    This performs traditional text search on specified fields.

    Args:
        query (str): Search query
        top_k (int): Number of results to return
        search_fields (Optional[List[str]]): Fields to search in

    Returns:
        List[Dict]: List of matching papers
    """

    if not ELASTICSEARCH_API_KEY:
        raise ValueError("ELASTICSEARCH_API_KEY not set in environment")

    url = f"{ELASTICSEARCH_URL}/papers/_search"
    headers = {
        "Authorization": f"ApiKey {ELASTICSEARCH_API_KEY}",
        "Content-Type": "application/json"
    }

    # Default search fields
    if search_fields is None:
        search_fields = ["title^3", "abstract^2", "authors", "journal"]

    search_body = {
        "size": top_k,
        "query": {
            "multi_match": {
                "query": query,
                "fields": search_fields,
                "type": "best_fields"
            }
        },
        "_source": [
            "pmid",
            "title",
            "abstract",
            "authors",
            "journal",
            "publication_year",
            "doi"
        ]
    }

    try:
        response = requests.post(url, json=search_body, headers=headers, timeout=30)
        response.raise_for_status()

        results_data = response.json()
        hits = results_data.get("hits", {}).get("hits", [])

        papers = []
        for hit in hits:
            paper = hit.get("_source", {})
            paper["_score"] = hit.get("_score")
            paper["_id"] = hit.get("_id")
            papers.append(paper)

        return papers

    except requests.exceptions.RequestException as e:
        print(f"Error searching papers: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return []


def hybrid_search_papers(
    query: str,
    top_k: int = 10,
    semantic_weight: float = 0.7,
    keyword_weight: float = 0.3
) -> List[Dict]:
    """
    Hybrid search combining semantic and keyword search.

    Args:
        query (str): Search query
        top_k (int): Number of results to return
        semantic_weight (float): Weight for semantic search (0-1)
        keyword_weight (float): Weight for keyword search (0-1)

    Returns:
        List[Dict]: Combined and ranked results
    """

    if not ELASTICSEARCH_API_KEY:
        raise ValueError("ELASTICSEARCH_API_KEY not set in environment")

    url = f"{ELASTICSEARCH_URL}/papers/_search"
    headers = {
        "Authorization": f"ApiKey {ELASTICSEARCH_API_KEY}",
        "Content-Type": "application/json"
    }

    # Hybrid search using RRF (Reciprocal Rank Fusion)
    search_body = {
        "size": top_k,
        "query": {
            "bool": {
                "should": [
                    {
                        "semantic": {
                            "field": "title_abstract_semantic_embedding",
                            "query": query,
                            "boost": semantic_weight
                        }
                    },
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["title^3", "abstract^2", "authors"],
                            "boost": keyword_weight
                        }
                    }
                ]
            }
        },
        "_source": [
            "pmid",
            "title",
            "abstract",
            "authors",
            "journal",
            "publication_year",
            "doi"
        ]
    }

    try:
        response = requests.post(url, json=search_body, headers=headers, timeout=30)
        response.raise_for_status()

        results_data = response.json()
        hits = results_data.get("hits", {}).get("hits", [])

        papers = []
        for hit in hits:
            paper = hit.get("_source", {})
            paper["_score"] = hit.get("_score")
            paper["_id"] = hit.get("_id")
            papers.append(paper)

        return papers

    except requests.exceptions.RequestException as e:
        print(f"Error searching papers: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return []


def medical_focused_search(
    medical_keywords: str,
    cs_keywords: Optional[str] = None,
    top_k: int = 10,
    medical_boost: float = 5.0,
    cs_boost: float = 1.0
) -> List[Dict]:
    """
    Search papers with medical keywords heavily weighted and CS keywords optional.

    This function prioritizes medical/clinical terms while allowing CS/technical
    terms to optionally boost relevance without being required.

    Args:
        medical_keywords (str): Required medical/clinical search terms (highly weighted)
        cs_keywords (Optional[str]): Optional CS/technical terms (lower weight, not required)
        top_k (int): Number of results to return
        medical_boost (float): Boost factor for medical terms (default: 5.0)
        cs_boost (float): Boost factor for CS terms (default: 1.0)

    Returns:
        List[Dict]: List of matching papers prioritizing medical relevance

    Example:
        >>> results = medical_focused_search(
        ...     medical_keywords="brain tumor glioblastoma classification",
        ...     cs_keywords="convolutional neural networks deep learning",
        ...     top_k=10
        ... )
    """

    if not ELASTICSEARCH_API_KEY:
        raise ValueError("ELASTICSEARCH_API_KEY not set in environment")

    url = f"{ELASTICSEARCH_URL}/papers/_search"
    headers = {
        "Authorization": f"ApiKey {ELASTICSEARCH_API_KEY}",
        "Content-Type": "application/json"
    }

    # Build query with medical terms as "must" and CS terms as "should"
    bool_query = {
        "must": [
            # Semantic search on medical terms (required, highly weighted)
            {
                "semantic": {
                    "field": "title_abstract_semantic_embedding",
                    "query": medical_keywords,
                    "boost": medical_boost
                }
            }
        ],
        "should": []
    }

    # Add keyword matching for medical terms with high boost
    bool_query["should"].append({
        "multi_match": {
            "query": medical_keywords,
            "fields": ["title^5", "abstract^3", "journal^2"],
            "boost": medical_boost,
            "type": "best_fields"
        }
    })

    # Add CS keywords as optional boosters if provided
    if cs_keywords:
        # Semantic search on CS terms (optional, lower weight)
        bool_query["should"].append({
            "semantic": {
                "field": "title_abstract_semantic_embedding",
                "query": cs_keywords,
                "boost": cs_boost
            }
        })

        # Keyword matching for CS terms (optional, lower weight)
        bool_query["should"].append({
            "multi_match": {
                "query": cs_keywords,
                "fields": ["title^2", "abstract"],
                "boost": cs_boost,
                "type": "best_fields"
            }
        })

    search_body = {
        "size": top_k,
        "query": {
            "bool": bool_query
        },
        "_source": [
            "pmid",
            "title",
            "abstract",
            "authors",
            "journal",
            "publication_year",
            "doi"
        ]
    }

    try:
        response = requests.post(url, json=search_body, headers=headers, timeout=30)
        response.raise_for_status()

        results_data = response.json()
        hits = results_data.get("hits", {}).get("hits", [])

        papers = []
        for hit in hits:
            paper = hit.get("_source", {})
            paper["_score"] = hit.get("_score")
            paper["_id"] = hit.get("_id")
            papers.append(paper)

        return papers

    except requests.exceptions.RequestException as e:
        print(f"Error searching papers: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return []


# Example usage
if __name__ == "__main__":
    # Test medical-focused search
    print("Testing Medical-Focused Search (Medical keywords weighted, CS optional)...")
    print("="*80)

    medical_terms = "brain tumor glioblastoma classification diagnosis"
    cs_terms = "convolutional neural networks deep learning CNN"

    results = medical_focused_search(
        medical_keywords=medical_terms,
        cs_keywords=cs_terms,
        top_k=5,
        medical_boost=5.0,
        cs_boost=1.0
    )

    print(f"\nMedical Keywords (Required, High Weight): '{medical_terms}'")
    print(f"CS Keywords (Optional, Low Weight): '{cs_terms}'")
    print(f"Found {len(results)} papers:\n")

    for i, paper in enumerate(results, 1):
        print(f"{i}. {paper.get('title', 'No title')}")
        print(f"   PMID: {paper.get('pmid', 'N/A')}")
        print(f"   Score: {paper.get('_score', 0):.4f}")
        print(f"   Authors: {paper.get('authors', 'N/A')[:80]}...")
        print(f"   Journal: {paper.get('journal', 'N/A')}")
        print(f"   Year: {paper.get('publication_year', 'N/A')}")
        print()

    print("\n" + "="*80)
    print("Testing Standard Semantic Search for comparison...")
    print("="*80)

    query = "convolutional neural networks for brain tumor classification"
    results2 = search_papers_with_agent(query, top_k=5)

    print(f"\nQuery: '{query}'")
    print(f"Found {len(results2)} papers:\n")

    for i, paper in enumerate(results2, 1):
        print(f"{i}. {paper.get('title', 'No title')}")
        print(f"   PMID: {paper.get('pmid', 'N/A')}")
        print(f"   Score: {paper.get('_score', 0):.4f}")
        print(f"   Authors: {paper.get('authors', 'N/A')[:80]}...")
        print(f"   Journal: {paper.get('journal', 'N/A')}")
        print(f"   Year: {paper.get('publication_year', 'N/A')}")
        print()
