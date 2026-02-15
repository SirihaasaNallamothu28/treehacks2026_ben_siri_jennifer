"""
Test the complete integration:
1. get_medical_interests_and_technical_interests() reads from JSON
2. get_best_paper_json() uses those interests
3. Returns proper format for video generation
"""
import sys
import os
from dotenv import load_dotenv

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()

def test_complete_integration():
    """Test the complete flow from interests to paper JSON"""

    print("=" * 80)
    print("Testing Complete Integration: Interests → Paper Selection")
    print("=" * 80)

    # Import the functions
    from main import get_medical_interests_and_technical_interests, get_best_paper_json

    # Test Step 1: Get interests
    print("\nStep 1: Getting user interests...")
    print("-" * 80)
    try:
        medical_interests, technical_interests = get_medical_interests_and_technical_interests()
        print(f"✅ Got interests:")
        print(f"   Medical: {medical_interests}")
        print(f"   Technical: {technical_interests}")
    except Exception as e:
        print(f"❌ Failed to get interests: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test Step 2: Get best paper JSON
    print("\nStep 2: Fetching best paper based on interests...")
    print("-" * 80)
    try:
        paper = get_best_paper_json()
        print(f"✅ Got paper JSON")
        print(f"\nReturned type: {type(paper)}")
    except Exception as e:
        print(f"❌ Failed to get paper: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test Step 3: Verify format
    print("\nStep 3: Verifying paper format...")
    print("-" * 80)

    # Check if it's a dict
    if not isinstance(paper, dict):
        print(f"❌ ERROR: Expected dict, got {type(paper)}")
        return False

    # Check required fields for video generation
    required_fields = ['title', 'authors', 'journal', 'publication_year', 'abstract']
    missing_fields = []

    print("Required fields for generate_video_from_paper():")
    for field in required_fields:
        if field in paper:
            value = paper[field]
            # Show preview
            if isinstance(value, list):
                value_preview = f"[list with {len(value)} items]"
                if len(value) > 0:
                    value_preview += f" First: {str(value[0])[:50]}..."
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

    # Show full paper details
    print("\n" + "=" * 80)
    print("📄 Selected Paper Details:")
    print("=" * 80)
    print(f"Title: {paper['title']}")
    print(f"Journal: {paper['journal']}")
    print(f"Year: {paper['publication_year']}")
    if isinstance(paper['authors'], list):
        authors_str = ', '.join(paper['authors'][:3])
        if len(paper['authors']) > 3:
            authors_str += f" (and {len(paper['authors']) - 3} more)"
    else:
        authors_str = paper['authors']
    print(f"Authors: {authors_str}")
    print(f"\nAbstract: {paper['abstract'][:200]}...")

    print("\n" + "=" * 80)
    print("✅ INTEGRATION TEST PASSED!")
    print("   All components work together correctly:")
    print("   1. ✅ Interests loaded from user_interests.json")
    print("   2. ✅ Paper selected using test_synapsis agent")
    print("   3. ✅ Paper JSON has all required fields")
    print("   4. ✅ Ready for video generation")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = test_complete_integration()
    sys.exit(0 if success else 1)
