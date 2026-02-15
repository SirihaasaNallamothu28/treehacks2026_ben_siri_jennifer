"""
Test script to diagnose abstract truncation issues
"""

import os
from dotenv import load_dotenv
from Bio import Entrez

load_dotenv()

# Configure Entrez
Entrez.email = "sirihaasanallamothu@gmail.com"
Entrez.api_key = os.getenv("MY_API_KEY")

def test_abstract_extraction():
    """Test how abstracts are extracted from PubMed"""

    # Get a known article with a structured abstract
    pmid = "35771962"  # From our previous test

    print(f"Fetching PMID {pmid}...")
    handle = Entrez.efetch(db="pubmed", id=pmid, rettype="medline", retmode="xml")
    records = Entrez.read(handle)

    article = records["PubmedArticle"][0]
    article_data = article["MedlineCitation"]["Article"]

    print("\n" + "="*80)
    print("ABSTRACT ANALYSIS")
    print("="*80)

    if "Abstract" in article_data:
        abstract = article_data["Abstract"]
        print(f"\nAbstract keys: {abstract.keys()}")

        if "AbstractText" in abstract:
            parts = abstract["AbstractText"]
            print(f"\nAbstractText type: {type(parts)}")
            print(f"Number of parts: {len(parts) if isinstance(parts, list) else 1}")

            print("\n" + "-"*80)
            print("PART-BY-PART ANALYSIS:")
            print("-"*80)

            if isinstance(parts, list):
                for i, part in enumerate(parts):
                    print(f"\n--- Part {i+1} ---")
                    print(f"Type: {type(part)}")
                    print(f"Dir: {[attr for attr in dir(part) if not attr.startswith('_')]}")

                    # Check for attributes
                    if hasattr(part, 'attributes'):
                        print(f"Attributes: {part.attributes}")

                    # Get the text content
                    text_content = str(part)
                    print(f"String representation length: {len(text_content)}")
                    print(f"Content preview: {text_content[:200]}...")

            else:
                # Single element
                print(f"\nSingle AbstractText element")
                print(f"Type: {type(parts)}")
                if hasattr(parts, 'attributes'):
                    print(f"Attributes: {parts.attributes}")
                text_content = str(parts)
                print(f"Length: {len(text_content)}")
                print(f"Content: {text_content}")

            # Now test our current extraction method
            print("\n" + "="*80)
            print("CURRENT EXTRACTION METHOD:")
            print("="*80)
            abstract_text = "\n".join(str(p) for p in parts) if isinstance(parts, list) else str(parts)
            print(f"Total extracted length: {len(abstract_text)} characters")
            print(f"\nExtracted abstract:\n{abstract_text}")

            # Count words
            word_count = len(abstract_text.split())
            print(f"\nWord count: {word_count} words")

    else:
        print("No abstract found!")

if __name__ == "__main__":
    test_abstract_extraction()
