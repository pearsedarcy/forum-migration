import requests
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import math

# Setup paths
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / 'data' / 'xenforo' / 'users'
PROCESSED_DIR = DATA_DIR / 'processed'

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

# Load environment variables
load_dotenv(ROOT_DIR / '.env')

# XenForo API configuration
XENFORO_BASE_URL = os.getenv('XENFORO_BASE_URL')
API_KEY = os.getenv('XENFORO_API_KEY')

if not all([XENFORO_BASE_URL, API_KEY]):
    raise ValueError("Missing required environment variables. Check your .env file.")

USERS_API_URL = f'{XENFORO_BASE_URL}api/users'

headers = {
    'XF-Api-Key': API_KEY,
    'Accept': 'application/json'
}

# Maximum number of concurrent requests
MAX_WORKERS = 5

def fetch_users(page: int = 1) -> dict:
    """Fetch users from XenForo API with pagination"""
    try:
        params = {
            'page': page,
            'api_bypass_permissions': 1  # Add bypass parameter to get all users
        }
        response = requests.get(
            USERS_API_URL,
            headers=headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Error fetching users page {page}: {str(e)}")
        return None

def save_users(users: list, filename: str) -> None:
    """Save users data to a JSON file"""
    filepath = PROCESSED_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({'users': users}, f, indent=4, ensure_ascii=False)
    print(f"💾 Saved {len(users)} users to {filepath}")

def generate_user_statistics(users: list) -> dict:
    """Generate statistics about harvested users"""
    stats = {
        "total_users": len(users),
        "user_states": {
            "valid": len([u for u in users if u.get("user_state") == "valid"]),
            "email_confirm_pending": len([u for u in users if u.get("user_state") == "email_confirm_pending"]),
            "moderated": len([u for u in users if u.get("user_state") == "moderated"]),
        },
        "user_groups": {},
        "top_posters": [],
        "most_reactions": [],
        "registration_timeline": {},
        "total_messages": sum(u.get("message_count", 0) for u in users),
        "total_reactions": sum(u.get("reaction_score", 0) for u in users),
        "total_trophy_points": sum(u.get("trophy_points", 0) for u in users)
    }
    
    # Collect user group statistics
    for user in users:
        group = user.get("user_group_id")
        if group:
            stats["user_groups"][group] = stats["user_groups"].get(group, 0) + 1
    
    # Get top 10 users by different metrics
    stats["top_posters"] = sorted(
        [{"username": u["username"], "messages": u["message_count"]} for u in users],
        key=lambda x: x["messages"],
        reverse=True
    )[:10]
    
    stats["most_reactions"] = sorted(
        [{"username": u["username"], "reactions": u["reaction_score"]} for u in users],
        key=lambda x: x["reactions"],
        reverse=True
    )[:10]
    
    # Registration timeline by month
    for user in users:
        reg_date = datetime.fromtimestamp(user["register_date"])
        month_key = reg_date.strftime("%Y-%m")
        stats["registration_timeline"][month_key] = stats["registration_timeline"].get(month_key, 0) + 1
    
    stats["registration_timeline"] = dict(sorted(stats["registration_timeline"].items()))
    
    return stats

def get_pagination_info() -> dict:
    """Get pagination information from first page"""
    try:
        data = fetch_users(1)
        if data and 'pagination' in data:
            return data['pagination']
        return {}
    except:
        return {}

def fetch_users_parallel(page_numbers: List[int]) -> List[Dict]:
    """Fetch multiple pages of users in parallel"""
    users = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_page = {
            executor.submit(fetch_users, page): page 
            for page in page_numbers
        }
        
        any_success = False
        for future in as_completed(future_to_page):
            page = future_to_page[future]
            try:
                data = future.result()
                if data and 'users' in data and data['users']:
                    print(f"✅ Retrieved {len(data['users'])} users from page {page}")
                    users.extend(data['users'])
                    any_success = True
                else:
                    print(f"⚠️ No users found on page {page}")
            except Exception as e:
                print(f"❌ Error on page {page}: {str(e)}")
    
    return users if any_success else None

def harvest_users() -> None:
    """Harvest all users with parallel processing"""
    all_users = []
    print("🚀 Starting parallel XenForo user harvest...")
    
    page = 1
    consecutive_empty_batches = 0
    max_empty_batches = 2  # Stop after 2 consecutive empty batches
    
    while consecutive_empty_batches < max_empty_batches:
        # Process pages in batches
        batch_pages = range(page, page + MAX_WORKERS)
        print(f"\n📥 Processing batch of pages {list(batch_pages)}")
        
        batch_users = fetch_users_parallel(batch_pages)
        if not batch_users:
            consecutive_empty_batches += 1
            print(f"⚠️ Empty batch {consecutive_empty_batches}/{max_empty_batches}")
        else:
            consecutive_empty_batches = 0  # Reset counter on successful batch
            all_users.extend(batch_users)
            
        page += MAX_WORKERS
        time.sleep(1)  # Rate limiting protection
    
    if all_users:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save user data
        filename = f"xenforo_users_{timestamp}.json"
        save_users(all_users, filename)
        
        # Generate and save statistics
        stats = generate_user_statistics(all_users)
        stats_file = DATA_DIR / f"xenforo_user_info_{timestamp}.json"
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4, ensure_ascii=False)
        print(f"📊 User statistics saved to {stats_file}")
        
        # Save user IDs for reference
        user_ids = [user['user_id'] for user in all_users]
        with open(DATA_DIR / 'xenforo_user_ids.json', 'w') as f:
            json.dump({'user_ids': user_ids}, f)
            
        print(f"✨ Successfully harvested {len(all_users)} users total")
        print(f"📈 {stats['user_states']['valid']} valid users")
        print(f"👥 {len(stats['user_groups'])} different user groups")
        print(f"📝 Total messages: {stats['total_messages']}")
    else:
        print("❌ No users were harvested")

if __name__ == "__main__":
    print(f"🌐 Using XenForo API at: {XENFORO_BASE_URL}")
    harvest_users()
