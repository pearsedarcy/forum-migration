import requests
import json
from pprint import pprint
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

# Setup paths
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / 'data' / 'xenforo'
PROCESSED_DIR = DATA_DIR / 'processed'

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

# Load environment variables
load_dotenv(ROOT_DIR / '.env')

# XenForo API configuration from environment variables
XENFORO_BASE_URL = os.getenv('XENFORO_BASE_URL')
API_KEY = os.getenv('XENFORO_API_KEY')

# Validate required environment variables
if not all([XENFORO_BASE_URL, API_KEY]):
    raise ValueError("Missing required environment variables. Check your .env file.")

XENFORO_API_URL = f'{XENFORO_BASE_URL}api'

headers = {
    'XF-Api-Key': API_KEY,
    'Accept': 'application/json'
}

def save_response(endpoint: str, data: dict):
    """Save API response to a JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Clean endpoint name for filename
    endpoint_name = endpoint.strip('/').replace('/', '_') or 'index'
    filename = DATA_DIR / f"xenforo_{endpoint_name}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"📝 Saved response to: {filename}")

def test_api_endpoints():
    """Test various API endpoints"""
    endpoints = [
        '/',               # Index
        '/threads/',       # Threads
        '/forums/',        # Forums list
        '/categories/',    # Categories
    ]
    
    results = {}
    for endpoint in endpoints:
        try:
            url = f"{XENFORO_API_URL}{endpoint}"
            print(f"\n🎯 Testing endpoint: {url}")
            
            response = requests.get(
                url,
                headers=headers,
                timeout=10
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✨ Response received successfully")
                save_response(endpoint, data)
                print(f"💾 Data saved for endpoint: {endpoint}")
                results[endpoint] = data
            else:
                print("❌ Error Response:")
                print(f"⚠️ {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"💥 Connection Error: {str(e)}")
    
    # Save combined results
    if results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        combined_filename = f"xenforo_all_responses_{timestamp}.json"
        with open(combined_filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        print(f"\n📦 Saved combined responses to: {combined_filename}")
        print("🎉 All tasks completed successfully!")

if __name__ == "__main__":
    print("🚀 Starting XenForo API tests...\n")
    print(f"🌐 Base URL: {XENFORO_BASE_URL}")
    print(f"🔑 Using API key: {API_KEY}")
    test_api_endpoints()
