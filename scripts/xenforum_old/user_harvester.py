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
DATA_DIR = ROOT_DIR / 'data' / 'xenforum' / 'users'
PROCESSED_DIR = DATA_DIR / 'processed'

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

# Load environment variables
load_dotenv(ROOT_DIR / '.env')

# API Configuration
BASE_URL = "https://app.xenforum.net/api/users"
API_HEADERS = {
    "Token": os.getenv('XENFORUM_OLD_TOKEN'),
    "Shop": os.getenv('XENFORUM_OLD_SHOP')
}

# Maximum number of concurrent requests
MAX_WORKERS = 5

def fetch_users(page: int = 1) -> dict:
    """Fetch users from XenForum API with pagination support"""
    try:
        url = f"{BASE_URL}.json"
        params = {
            'page': page,
            'include_pagination': 1  # Request pagination info
        }
        response = requests.get(
            url, 
            headers=API_HEADERS, 
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
        "verified_users": len([u for u in users if u.get("verified_email")]),
        "users_with_avatar": len([u for u in users if u.get("avatar")]),
        "staff_users": len([u for u in users if u.get("is_staff")]),
        "countries": {},
        "top_posters": [],
        "most_viewed": [],
        "most_liked": [],
        "registration_timeline": {},
        "total_posts": sum(u.get("post_count", 0) for u in users),
        "total_views": sum(u.get("view_count", 0) for u in users),
        "total_likes": sum(u.get("like_count", 0) for u in users)
    }
    
    # Collect country statistics
    for user in users:
        country = user.get("country")
        if country:
            stats["countries"][country] = stats["countries"].get(country, 0) + 1
    
    # Sort countries by user count
    stats["countries"] = dict(sorted(
        stats["countries"].items(), 
        key=lambda x: x[1], 
        reverse=True
    ))
    
    # Get top 10 users by different metrics
    stats["top_posters"] = sorted(
        [{"name": u["display_name"], "posts": u["post_count"]} for u in users],
        key=lambda x: x["posts"],
        reverse=True
    )[:10]
    
    stats["most_viewed"] = sorted(
        [{"name": u["display_name"], "views": u["view_count"]} for u in users],
        key=lambda x: x["views"],
        reverse=True
    )[:10]
    
    stats["most_liked"] = sorted(
        [{"name": u["display_name"], "likes": u["like_count"]} for u in users],
        key=lambda x: x["likes"],
        reverse=True
    )[:10]
    
    # Registration timeline by month
    for user in users:
        created = datetime.fromisoformat(user["created"].replace("Z", "+00:00"))
        month_key = created.strftime("%Y-%m")
        stats["registration_timeline"][month_key] = stats["registration_timeline"].get(month_key, 0) + 1
    
    stats["registration_timeline"] = dict(sorted(stats["registration_timeline"].items()))
    
    return stats

def get_total_pages() -> int:
    """Get total number of pages from API response"""
    try:
        data = fetch_users(1)
        if not data:
            return 0
            
        # XenForum API includes pagination info in the response
        pagination = data.get('pagination', {})
        if pagination:
            return pagination.get('total_pages', 1)
            
        # Fallback: Calculate from total users if available
        total_users = data.get('total_users', len(data.get('users', [])))
        users_per_page = len(data.get('users', []))
        if users_per_page > 0:
            return math.ceil(total_users / users_per_page)
            
        return 1
    except Exception as e:
        print(f"❌ Error getting total pages: {str(e)}")
        return 0

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
    print("🚀 Starting parallel user harvest...")
    
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
        # Save users data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"users_{timestamp}.json"
        save_users(all_users, filename)
        
        # Generate and save statistics
        stats = generate_user_statistics(all_users)
        stats_file = DATA_DIR / f"user_info_{timestamp}.json"
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4, ensure_ascii=False)
        print(f"📊 User statistics saved to {stats_file}")
        
        # Save user IDs
        user_ids = [user['id'] for user in all_users]
        with open(DATA_DIR / 'user_ids.json', 'w') as f:
            json.dump({'user_ids': user_ids}, f)
            
        print(f"✨ Successfully harvested {len(all_users)} users total")
        print(f"📈 {stats['verified_users']} verified users")
        print(f"🌎 Users from {len(stats['countries'])} countries")
        print(f"📝 Total posts: {stats['total_posts']}")
    else:
        print("❌ No users were harvested")

def main():
    """Main execution function"""
    try:
        harvest_users()
    except Exception as e:
        print(f"💥 An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
