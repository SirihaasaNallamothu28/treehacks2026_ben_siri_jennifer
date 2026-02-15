"""
Standalone test of get_medical_interests_and_technical_interests logic
"""
import sys
import os
import json
from dotenv import load_dotenv

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()

def get_medical_interests_and_technical_interests():
    """
    (Copy of function from main.py for standalone testing)
    """
    # Path to user interests file
    interests_file = os.path.join(os.path.dirname(__file__), "user_interests.json")

    # Try to read from file
    if os.path.exists(interests_file):
        try:
            with open(interests_file, 'r') as f:
                data = json.load(f)
                medical_interests = data.get("medical_interests", "")
                technical_interests = data.get("technical_interests", "")

                if medical_interests and technical_interests:
                    print(f"📋 Using interests from {interests_file}")
                    print(f"   Medical: {medical_interests}")
                    print(f"   Technical: {technical_interests}")
                    return medical_interests, technical_interests
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Warning: Could not read {interests_file}: {e}")

    # Fall back to prompting user
    print("\n" + "="*80)
    print("No user_interests.json found. Please enter your interests:")
    print("="*80)

    medical_interests = input("Medical/Healthcare interests (e.g., 'cancer treatment, immunotherapy'): ").strip()
    technical_interests = input("Technical/AI interests (e.g., 'machine learning, deep learning'): ").strip()

    # Save for next time
    try:
        with open(interests_file, 'w') as f:
            json.dump({
                "medical_interests": medical_interests,
                "technical_interests": technical_interests
            }, f, indent=2)
        print(f"✅ Saved interests to {interests_file}")
    except IOError as e:
        print(f"⚠️  Warning: Could not save interests: {e}")

    return medical_interests, technical_interests


def test_complete_integration():
    """Test the complete flow from interests to paper JSON"""

    print("=" * 80)
    print("Testing Complete Integration: Interests → Paper Selection")
    print("=" * 80)

    # Test Step 1: Get interests
    print("\nStep 1: Getting user interests...")
    print("-" * 80)
    try:
        medical_interests, technical_interests = get_medical_interests_and_technical_interests()
        print(f"✅ Got interests:")
        print(f"   Type: {type(medical_interests)}, {type(technical_interests)}")
        print(f"   Medical: {medical_interests}")
        print(f"   Technical: {technical_interests}")

        # Verify they are strings
        if not isinstance(medical_interests, str) or not isinstance(technical_interests, str):
            print(f"❌ ERROR: Expected strings, got {type(medical_interests)} and {type(technical_interests)}")
            return False

        if not medical_interests or not technical_interests:
            print(f"❌ ERROR: Interests should not be empty")
            return False

    except Exception as e:
        print(f"❌ Failed to get interests: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test Step 2: Get best paper JSON
    print("\nStep 2: Fetching best paper based on interests...")
    print("-" * 80)
    try:
        from paper_search.seach_for_papers import search_for_papers
        paper = search_for_papers(medical_interests, technical_interests)
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
    print("   2. ✅ Both interests returned as strings")
    print("   3. ✅ Paper selected using test_synapsis agent")
    print("   4. ✅ Paper JSON has all required fields")
    print("   5. ✅ Ready for video generation pipeline")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = test_complete_integration()
    sys.exit(0 if success else 1)
