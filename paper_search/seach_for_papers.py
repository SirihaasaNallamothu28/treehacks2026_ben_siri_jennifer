"""
Search for papers using Elastic Agent Builder API

This module provides functions to call custom Elastic agents that have been
configured with system prompts in the Kibana UI.

References:
- Elastic Agent Builder: https://www.elastic.co/elasticsearch/agent-builder
- API Documentation: https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/kibana-api
- Agent Builder Overview: https://www.elastic.co/docs/solutions/search/agent-builder/agent-builder-agents
"""

import os
import requests
from typing import Dict, Optional, Iterator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "https://synapsis-c99bf6.es.us-central1.gcp.elastic.cloud")
ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")

# Kibana URL (typically on same domain as Elasticsearch)
# Convert es.domain.com to kb.domain.com if needed
KIBANA_URL = os.getenv("KIBANA_URL", ELASTICSEARCH_URL.replace("es.", "kb.") if ELASTICSEARCH_URL else "")


def call_elastic_agent(
    agent_id: str,
    input_query: str,
    conversation_id: Optional[str] = None,
    space_name: Optional[str] = None
) -> Dict:
    """
    Call a custom Elastic Agent Builder agent by ID.

    This function invokes an Elastic Agent that has been configured with custom
    system prompts in the Kibana UI. Agents can be designed for various tasks like
    document search, analysis, question answering, etc.

    The agent uses its configured system prompt (instructions) along with any
    tools you've assigned to it to process the input query and generate a response.

    Args:
        agent_id (str): The unique ID of the agent to invoke (created in Kibana UI)
        input_query (str): The message/query to send to the agent
        conversation_id (Optional[str]): ID to maintain conversation context across
                                         multiple requests (for follow-up questions)
        space_name (Optional[str]): Kibana space name (if not using default space)

    Returns:
        Dict: Agent response containing:
            - output (str): The agent's response text
            - conversation_id (str): ID for continuing the conversation
            - Additional metadata depending on agent configuration

    Raises:
        ValueError: If ELASTICSEARCH_API_KEY is not configured
        requests.exceptions.RequestException: If the API call fails

    Example:
        >>> # Simple query
        >>> response = call_elastic_agent(
        ...     agent_id="paper-search-agent",
        ...     input_query="Find recent papers on CNN for brain tumor classification"
        ... )
        >>> print(response['output'])

        >>> # Follow-up question using conversation ID
        >>> followup = call_elastic_agent(
        ...     agent_id="paper-search-agent",
        ...     input_query="Which of those papers has the highest citation count?",
        ...     conversation_id=response['conversation_id']
        ... )

    References:
        - Elastic Agent Builder: https://www.elastic.co/elasticsearch/agent-builder
        - API Docs: https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/kibana-api
    """

    if not ELASTICSEARCH_API_KEY:
        raise ValueError(
            "ELASTICSEARCH_API_KEY not set in environment. "
            "Please set it in your .env file."
        )

    # Build the API endpoint
    # Format: /api/agent_builder/converse
    # Or: /s/{space_name}/api/agent_builder/converse for non-default spaces
    base_path = f"/s/{space_name}" if space_name else ""
    url = f"{KIBANA_URL}{base_path}/api/agent_builder/converse"

    # Required headers for Kibana API
    headers = {
        "Authorization": f"ApiKey {ELASTICSEARCH_API_KEY}",
        "kbn-xsrf": "true",  # Required for Kibana XSRF protection
        "Content-Type": "application/json"
    }

    # Build request body
    request_body = {
        "input": input_query,
        "agent_id": agent_id
    }

    # Add conversation ID if provided (for maintaining context)
    if conversation_id:
        request_body["conversation_id"] = conversation_id

    try:
        # Call the agent
        print(f"Calling agent '{agent_id}' with query: '{input_query[:80]}...'")
        response = requests.post(url, json=request_body, headers=headers, timeout=60)
        response.raise_for_status()

        # Parse and return the response
        result = response.json()
        print(f"✓ Agent responded successfully")
        return result

    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error calling Elastic Agent: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f"\nResponse: {e.response.text}"
        print(f"✗ {error_msg}")
        return {
            "error": str(e),
            "output": f"Failed to get response from agent: {e}"
        }

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
