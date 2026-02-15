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
        error_msg = f"Error calling Elastic Agent: {e}"
        print(f"✗ {error_msg}")
        return {
            "error": str(e),
            "output": f"Failed to connect to agent: {e}"
        }


def search_elasticsearch_directly(query_text: str, top_k: int = 3) -> list:
    """
    Search Elasticsearch directly using semantic search to get actual document JSON.

    This bypasses the agent and queries the database directly for reliable JSON.

    Args:
        query_text: Search query
        top_k: Number of results to return

    Returns:
        List of paper JSON documents with all fields
    """
    if not ELASTICSEARCH_API_KEY:
        raise ValueError("ELASTICSEARCH_API_KEY not set")

    url = f"{ELASTICSEARCH_URL}/papers/_search"
    headers = {
        "Authorization": f"ApiKey {ELASTICSEARCH_API_KEY}",
        "Content-Type": "application/json"
    }

    # Use simple_query_string which is more forgiving than query_string
    search_body = {
        "size": top_k,
        "query": {
            "simple_query_string": {
                "query": query_text,
                "fields": ["title^3", "abstract^2"],  # Boost title matches more
                "default_operator": "OR"
            }
        },
        "_source": ["pmid", "title", "abstract", "authors", "journal", "publication_year", "doi"]
    }

    try:
        response = requests.post(url, json=search_body, headers=headers, timeout=30)

        # Debug: print response if error
        if response.status_code != 200:
            print(f"Elasticsearch error response: {response.text}")

        response.raise_for_status()

        results = response.json()
        hits = results.get("hits", {}).get("hits", [])

        # Extract just the source documents
        papers = []
        for hit in hits:
            paper = hit.get("_source", {})
            paper["_score"] = hit.get("_score")
            papers.append(paper)

        return papers

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")

        # Try fallback: get any documents
        try:
            print("Trying fallback query...")
            fallback_body = {
                "size": top_k,
                "query": {"match_all": {}},
                "_source": ["pmid", "title", "abstract", "authors", "journal", "publication_year", "doi"]
            }
            response = requests.post(url, json=fallback_body, headers=headers, timeout=30)
            response.raise_for_status()
            results = response.json()
            hits = results.get("hits", {}).get("hits", [])
            papers = [hit.get("_source", {}) for hit in hits]
            print(f"✓ Fallback returned {len(papers)} papers")
            return papers
        except Exception as e2:
            print(f"Fallback also failed: {e2}")
            return []

    except Exception as e:
        print(f"Error searching Elasticsearch: {e}")
        return []


def get_papers_from_agent_then_fetch_json(medical_interests: str, technical_interests: str) -> list:
    """
    Method 1: Ask agent for paper recommendations, then fetch actual JSON from Elasticsearch.

    This ensures we get real document data, not AI-generated content.
    """
    # Ask agent for paper IDs/titles
    query = (
        f"Search for the top 3 papers matching these interests:\n"
        f"Medical: {medical_interests}\n"
        f"Technical: {technical_interests}\n\n"
        f"Return ONLY the PMID numbers, one per line, no other text."
    )

    response = call_elastic_agent(
        agent_id="test_synapsis",
        input_query=query
    )

    # Extract PMIDs from response
    output = response.get("response", "")
    pmids = []
    for line in output.split('\n'):
        line = line.strip()
        # Try to extract numbers that look like PMIDs
        if line.isdigit() and len(line) >= 6:
            pmids.append(line)

    # Fetch actual documents from Elasticsearch by PMID
    if not pmids:
        print("No PMIDs found in agent response")
        return []

    papers = []
    for pmid in pmids[:3]:
        try:
            url = f"{ELASTICSEARCH_URL}/papers/_search"
            headers = {
                "Authorization": f"ApiKey {ELASTICSEARCH_API_KEY}",
                "Content-Type": "application/json"
            }

            search_body = {
                "query": {"term": {"pmid": pmid}},
                "_source": ["pmid", "title", "abstract", "authors", "journal", "publication_year", "doi"]
            }

            response = requests.post(url, json=search_body, headers=headers, timeout=10)
            response.raise_for_status()

            results = response.json()
            hits = results.get("hits", {}).get("hits", [])
            if hits:
                papers.append(hits[0]["_source"])

        except Exception as e:
            print(f"Error fetching PMID {pmid}: {e}")

    return papers


def pick_most_relevant_paper_with_agent(papers: list, medical_interests: str, technical_interests: str) -> dict:
    """
    Use the agent to pick the most relevant paper from a list of candidates.

    Args:
        papers: List of paper JSON documents
        medical_interests: Medical research interests
        technical_interests: Technical research interests

    Returns:
        The single most relevant paper JSON document
    """
    if not papers:
        return None

    if len(papers) == 1:
        return papers[0]

    # Build prompt with paper summaries for the agent
    papers_text = ""
    for i, paper in enumerate(papers, 1):
        papers_text += f"\n{'='*60}\nPaper {i}:\n"
        papers_text += f"PMID: {paper.get('pmid', 'N/A')}\n"
        papers_text += f"Title: {paper.get('title', 'N/A')}\n"
        papers_text += f"Abstract: {paper.get('abstract', 'N/A')[:500]}...\n"  # First 500 chars

    query = (
        f"I am looking for papers related to:\n"
        f"Medical Interests: {medical_interests}\n"
        f"Technical Interests: {technical_interests}\n\n"
        f"Here are {len(papers)} candidate papers:\n"
        f"{papers_text}\n\n"
        f"Which paper is MOST relevant to my interests? "
        f"Respond with ONLY the number (1, 2, or 3) of the most relevant paper. "
        f"No explanation, just the number."
    )

    try:
        response = call_elastic_agent(
            agent_id="test_synapsis",
            input_query=query
        )

        # Extract the number from response
        # Handle different response formats
        if isinstance(response, dict):
            output = response.get("response", response.get("output", ""))
        else:
            output = str(response)

        # Convert to string if it's still a dict
        if isinstance(output, dict):
            output = str(output)

        output = output.strip()

        print(f"Agent response: {output[:200]}...")  # Debug output

        # Try to find a digit in the response
        import re
        match = re.search(r'\b([1-3])\b', output)

        if match:
            choice = int(match.group(1))
            if 1 <= choice <= len(papers):
                print(f"✓ Agent selected paper {choice}")
                return papers[choice - 1]

        # Fallback: if agent response is unclear, return first paper
        print("⚠ Could not parse agent response, returning first paper")
        return papers[0]

    except Exception as e:
        print(f"✗ Error using agent to pick paper: {e}")
        import traceback
        traceback.print_exc()
        print("⚠ Returning first paper as fallback")
        return papers[0]


def search_for_papers(medical_interests, technical_interests):
    """
    Search for papers related to medical and technical interests.

    Returns the SINGLE most relevant paper JSON document from Elasticsearch.
    The agent analyzes multiple candidates and picks the best match.

    :param medical_interests: Medical research interests (e.g., "brain tumors, neuroscience")
    :param technical_interests: Technical methods of interest (e.g., "CNNs, transformers")
    :return: Single paper JSON document with all fields (pmid, title, abstract, authors, journal, publication_year, doi)

    Example:
        >>> paper = search_for_papers("brain tumors", "CNN, deep learning")
        >>> print(paper['title'])
        >>> print(paper['abstract'])
        >>> print(f"PMID: {paper['pmid']}")
    """

    print(f"\n{'='*80}")
    print("SEARCHING FOR PAPERS")
    print(f"{'='*80}")
    print(f"Medical Interests: {medical_interests}")
    print(f"Technical Interests: {technical_interests}")
    print()

    # Combine interests into search query
    combined_query = f"{medical_interests} {technical_interests}"

    # Step 1: Get candidate papers from Elasticsearch
    print("Step 1: Finding candidate papers...")
    papers = search_elasticsearch_directly(combined_query, top_k=3)

    if not papers:
        print("✗ No papers found, trying broader search...")
        papers = search_elasticsearch_directly(medical_interests, top_k=3)

    if not papers:
        print("✗ Still no papers, trying technical interests...")
        papers = search_elasticsearch_directly(technical_interests, top_k=3)

    if not papers:
        print("✗ No papers found")
        return None

    print(f"✓ Found {len(papers)} candidate papers")

    # Step 2: Have agent pick the most relevant one
    print("\nStep 2: Agent selecting most relevant paper...")
    most_relevant = pick_most_relevant_paper_with_agent(papers, medical_interests, technical_interests)

    if most_relevant:
        print(f"✓ Selected paper: {most_relevant.get('title', 'Unknown')[:60]}...")

    return most_relevant



# Example usage and testing
if __name__ == "__main__":
    import json

    # Test the search function
    result = search_for_papers(
        medical_interests="brain tumors, neuroscience, medical imaging",
        technical_interests="CNN, deep learning, classification"
    )

    print(f"\n{'='*80}")
    print("RESULT - MOST RELEVANT PAPER JSON")
    print(f"{'='*80}\n")

    if result:
        print("Selected Paper:")
        print(json.dumps(result, indent=2))
    else:
        print("No paper found")

    # import sys

    # print("="*80)
    # print("Elastic Agent Builder API - Test")
    # print("="*80)

    # # Check if API key is configured
    # if not ELASTICSEARCH_API_KEY:
    #     print("\n❌ ERROR: ELASTICSEARCH_API_KEY not found in environment")
    #     print("Please set it in your .env file:")
    #     print('ELASTICSEARCH_API_KEY="your-api-key-here"')
    #     sys.exit(1)

    # print(f"\n✓ Elasticsearch URL: {ELASTICSEARCH_URL}")
    # print(f"✓ Kibana URL: {KIBANA_URL}")
    # print(f"✓ API Key: {'*' * 20}{ELASTICSEARCH_API_KEY[-8:] if len(ELASTICSEARCH_API_KEY) > 8 else '***'}")

    # # Example agent ID (you'll need to create an agent in Kibana UI first)
    # # Replace with your actual agent ID
    # example_agent_id = "test_synapsis"

    # print(f"\n{'='*80}")
    # print("Test 1: Simple Agent Call")
    # print(f"{'='*80}\n")

    # test_query = "Please find a paper about CNNs and brain tumors and summarize the abstract."

    # try:
    #     response = call_elastic_agent(
    #         agent_id=example_agent_id,
    #         input_query=test_query
    #     )

    #     print("Response keys:", list(response.keys()))


    #     print("\nAgent Response:")
    #     print("-"*80)
    #     if "response" in response:
    #         print(response["response"])
    #     else:
    #         print("Response structure:", response.keys())
    #         print(response)

    #     if "conversation_id" in response:
    #         print(f"\nConversation ID: {response['conversation_id']}")
    #         print("(Use this ID for follow-up questions)")

    # except Exception as e:
    #     print(f"\n❌ Error: {e}")
    #     print("\nNote: Make sure you've created an agent with ID '{example_agent_id}' in Kibana UI")
    #     print("Or update the example_agent_id variable with your agent's ID")

    # print(f"\n{'='*80}")
