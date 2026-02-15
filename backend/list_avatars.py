import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
API_KEY = os.getenv("HEYGEN_API_KEY")

def list_avatars():
    # Trying v1 streaming list endpoint
    url = "https://api.heygen.com/v1/streaming.list" 
    headers = {
        "x-api-key": API_KEY,
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        # response.raise_for_status() # Don't raise immediately, let's see text
        
        print(f"Status: {response.status_code}")
        try:
            data = response.json()
            avatars = data.get("data", {}).get("avatars", [])
            print(f"Found {len(avatars)} streaming avatars.")
            
            count = 0
            import json
            for av in avatars:
                 # Check if interactive avatar is supported (field might be differnet, let's dump first 5)
                 if count < 5:
                     print(f"Canddiate Avatar {count}: {json.dumps(av, indent=2)}")
                     count += 1
        except:
             print(f"Text response: {response.text}")
            
    except Exception as e:
        print(f"Error fetching avatars: {e}")            
    except Exception as e:
        print(f"Error fetching avatars: {e}")

if __name__ == "__main__":
    list_avatars()
