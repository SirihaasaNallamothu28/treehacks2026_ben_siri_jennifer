import requests
import os
from dotenv import load_dotenv
import json

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
API_KEY = os.getenv("HEYGEN_API_KEY")

def list_voices():
    url = "https://api.heygen.com/v2/voices"  # Trying v2 endpoint which is common
    headers = {
        "x-api-key": API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        # response.raise_for_status() 
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # The structure might be data -> voices or just a list
            voices = data.get("data", {}).get("voices", [])
            # If empty, try different structure
            if not voices and isinstance(data.get("data"), list):
                 voices = data.get("data")
            
            print(f"Found {len(voices)} voices.")
            
            # Print first 5 interactive voices
            count = 0
            for v in voices:
                if v.get("support_interactive_avatar") == True and count < 5:
                    print(f"Supported Voice: {json.dumps(v, indent=2)}")
                    count += 1
            
            if count == 0:
                print("No interactive-supported voices found.")
                    
        else:
             print(f"Error response: {response.text}")

    except Exception as e:
        print(f"Error fetching voices: {e}")

if __name__ == "__main__":
    list_voices()
