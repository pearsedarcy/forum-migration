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

# 🟢 Old API Configuration
OLD_API_BASE_URL = "https://app.xenforum.net/api/topics"
OLD_API_HEADERS = {
    "Token": os.getenv('XENFORUM_OLD_TOKEN'),
    "Shop": os.getenv('XENFORUM_OLD_SHOP')
}

def fetch_topic_data(topic_id: int) -> dict:
    """Fetch topic data from old API"""
    try:
        url = f"{OLD_API_BASE_URL}/{topic_id}.json"
        response = requests.get(url, headers=OLD_API_HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Error fetching topic {topic_id}: {str(e)}")
        return None

def harvest_data(topic_ids: list) -> None:
    """Harvest multiple topics and save the data"""
    all_data = []
    total = len(topic_ids)
    
    print(f"🚀 Starting harvest of {total} topics...")
    
    for i, topic_id in enumerate(topic_ids, 1):
        print(f"📥 Fetching topic {i}/{total}: {topic_id}")
        data = fetch_topic_data(topic_id)
        if data:
            all_data.append(data)
            print(f"✅ Successfully fetched topic {topic_id}")
        else:
            print(f"❌ Failed to fetch topic {topic_id}")

    if all_data:
        # Save data to a JSON file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = DATA_DIR / f"xenforum_data_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(all_data, file, indent=4, ensure_ascii=False)
        print(f"💾 Data saved to {filename}")
        print(f"✨ Successfully harvested {len(all_data)} of {total} topics")
    else:
        print("❌ No data was harvested")

def main():
    """Main execution function"""
    try:
        # Read topic IDs from JSON file
        topic_ids_file = DATA_DIR / 'topic_ids.json'
        if not topic_ids_file.exists():
            print(f"❌ Could not find {topic_ids_file}")
            return
            
        with open(topic_ids_file, 'r', encoding='utf-8') as file:
            topic_data = json.load(file)
            topic_ids = topic_data['topic_ids']
        
        print(f"📝 Found {len(topic_ids)} topics to process")
        harvest_data(topic_ids)
        
    except Exception as e:
        print(f"💥 An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
