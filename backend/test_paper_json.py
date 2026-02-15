"""
Direct test of get_best_paper_json logic without importing full main.py
"""
import sys
import os
from dotenv import load_dotenv

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()

# Import only what we need
from paper_search.seach_for_papers import search_for_papers

def get_best_paper_json(medical_interests, technical_interests):
    """
    Get the single best paper JSON based on medical and technical interests.
    (Copy of the function from main.py for testing)
    """
    paper = search_for_papers(medical_interests, technical_interests)

    # Ensure it's a dict
    if isinstance(paper, str):
        import json
        paper = json.loads(paper)

    return paper

def test_get_best_paper_json():
    """Test that get_best_paper_json returns the correct format"""

    print("=" * 80)
    print("Testing get_best_paper_json() function")
    print("=" * 80)

    # Test with sample interests
    medical_interests = "cancer treatment using immunotherapy"
    technical_interests = "machine learning and deep learning approaches"

    print(f"\nMedical interests: {medical_interests}")
    print(f"Technical interests: {technical_interests}")
    print("\nCalling get_best_paper_json()...")

    try:
        paper = get_best_paper_json(medical_interests, technical_interests)

        print("\n✅ Function executed successfully!")
        print("\nReturned type:", type(paper))

        # Check if it's a dict
        if not isinstance(paper, dict):
            print("❌ ERROR: Expected dict, got", type(paper))
            return False

        # Check required fields for video generation
        required_fields = ['title', 'authors', 'journal', 'publication_year', 'abstract']
        missing_fields = []

        print("\n📋 Checking required fields for generate_video_from_paper():")
        for field in required_fields:
            if field in paper:
                value = paper[field]
                # Show preview of value
                if isinstance(value, list):
                    value_preview = f"[list with {len(value)} items]"
                else:
                    value_str = str(value)
                    value_preview = value_str[:80] + "..." if len(value_str) > 80 else value_str
                print(f"  ✅ {field}: {value_preview}")
            else:
                print(f"  ❌ {field}: MISSING")
                missing_fields.append(field)

        if missing_fields:
            print(f"\n❌ Missing required fields: {missing_fields}")
            return False

        # Additional fields
        print("\n📋 Additional fields:")
        for key, value in paper.items():
            if key not in required_fields:
                if isinstance(value, list):
                    value_preview = f"[list with {len(value)} items]"
                else:
                    value_str = str(value)
                    value_preview = value_str[:80] + "..." if len(value_str) > 80 else value_str
                print(f"  - {key}: {value_preview}")

        print("\n" + "=" * 80)
        print("✅ TEST PASSED: get_best_paper_json() returns correct format!")
        print("   The function returns a Python dict (not string)")
        print("   All required fields for video generation are present")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_get_best_paper_json()
    sys.exit(0 if success else 1)
