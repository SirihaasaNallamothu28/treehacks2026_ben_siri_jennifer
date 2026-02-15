"""
Run upload_documents_from_keyword_query with a specific query
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the upload function
from upload_documents import upload_documents_from_keyword_query

if __name__ == "__main__":
    query = "brain scan with CNN based classifier"

    print(f"\n{'='*70}")
    print(f"Running upload for query: '{query}'")
    print(f"{'='*70}\n")

    upload_documents_from_keyword_query(query)

    print("\n" + "="*70)
    print("Upload process completed!")
    print("="*70)
