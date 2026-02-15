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


def search_for_papers(medical_interests, technical_interests):
    """
    Docstring for search_for_papers
    
    :param medical_interests: Description
    :param technical_interests: Description
    """
    # Build the query for the agent
    query = (
        f"Please find recent papers that match the following criteria:\n"
        f"- Medical Interests: {medical_interests}\n"
        f"- Technical Interests: {technical_interests}\n\n"
        f"Find the top 3 most relevant papers that someone with these interests would like to learn more about. In your response, include each paper's title split by a new line."
    )

    # Call the agent (replace 'paper-search-agent' with your actual agent ID)
    response = call_elastic_agent(
        agent_id="paper-search-agent",
        input_query=query
    )

    return response["response"]



# Example usage and testing
if __name__ == "__main__":

    results = search_for_papers("ear aches, neuroscience, chromosomes", "diffusion, transformers")

    print(results)

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
