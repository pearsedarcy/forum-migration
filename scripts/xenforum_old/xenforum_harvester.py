import requests
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import os

# Setup paths
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / 'data' / 'xenforum'
PROCESSED_DIR = DATA_DIR / 'processed'

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

# Load environment variables
load_dotenv(ROOT_DIR / '.env')

# API Endpoints
BASE_URL = "https://app.xenforum.net/api"
API_ENDPOINTS = {
    'topics': f"{BASE_URL}/topics",
    'users': f"{BASE_URL}/users",
    'forums': f"{BASE_URL}/forums",
    'posts': f"{BASE_URL}/posts"
}

OLD_API_HEADERS = {
    "Token": os.getenv('XENFORUM_OLD_TOKEN'),
    "Shop": os.getenv('XENFORUM_OLD_SHOP')
}

def fetch_data(endpoint: str, item_id: int = None) -> dict:
    """Generic fetch function for any data type"""
    try:
        url = f"{API_ENDPOINTS[endpoint]}/{str(item_id) + '.json' if item_id else '.json'}"
        response = requests.get(url, headers=OLD_API_HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Error fetching {endpoint} {item_id if item_id else ''}: {str(e)}")
        return None

def fetch_all_forums() -> list:
    """Fetch all forum data"""
    return fetch_data('forums')

def fetch_all_users() -> list:
    """Fetch all users data"""
    return fetch_data('users')

def fetch_posts_for_topic(topic_id: int) -> list:
    """Fetch all posts for a specific topic"""
    return fetch_data('posts', topic_id)

def harvest_data(data_type: str, ids: list = None) -> None:
    """Harvest data for specified type and save it"""
    all_data = []
    
    print(f"🚀 Starting harvest of {data_type}...")
    
    if ids:
        total = len(ids)
        for i, item_id in enumerate(ids, 1):
            print(f"📥 Fetching {data_type} {i}/{total}: {item_id}")
            data = fetch_data(data_type, item_id)
            if data:
                all_data.append(data)
                # Fetch posts if we're processing topics
                if data_type == 'topics':
                    posts = fetch_posts_for_topic(item_id)
                    if posts:
                        posts_file = PROCESSED_DIR / f"posts_topic_{item_id}.json"
                        with open(posts_file, "w", encoding="utf-8") as f:
                            json.dump(posts, f, indent=4, ensure_ascii=False)
    else:
        # For forums and users, fetch all at once
        data = fetch_data(data_type)
        if data:
            all_data = data

    if all_data:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = PROCESSED_DIR / f"{data_type}_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(all_data, file, indent=4, ensure_ascii=False)
        print(f"💾 {data_type.capitalize()} data saved to {filename}")
        print(f"✨ Successfully harvested {len(all_data)} {data_type}")
    else:
        print(f"❌ No {data_type} data was harvested")

def main():
    """Main execution function"""
    try:
        # First harvest forums and users (no IDs needed)
        harvest_data('forums')
        harvest_data('users')
        
        # Then harvest topics and their posts
        topic_ids_file = DATA_DIR / 'topic_ids.json'
        if not topic_ids_file.exists():
            print(f"❌ Could not find {topic_ids_file}")
            return
            
        with open(topic_ids_file, 'r', encoding='utf-8') as file:
            topic_data = json.load(file)
            topic_ids = topic_data['topic_ids']
        
        print(f"📝 Found {len(topic_ids)} topics to process")
        harvest_data('topics', topic_ids)
        
    except Exception as e:
        print(f"💥 An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
