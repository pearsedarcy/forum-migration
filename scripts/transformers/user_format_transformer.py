import json
from datetime import datetime
from pathlib import Path
import time

# Setup paths
ROOT_DIR = Path(__file__).parent.parent.parent
OLD_DATA_DIR = ROOT_DIR / 'data' / 'xenforum' / 'users' / 'processed'
NEW_DATA_DIR = ROOT_DIR / 'data' / 'xenforo' / 'users' / 'processed'
TRANSFORMED_DIR = ROOT_DIR / 'data' / 'transformed' / 'users'

# Ensure directories exist
TRANSFORMED_DIR.mkdir(parents=True, exist_ok=True)

def convert_timestamp(iso_date: str) -> int:
    """Convert ISO timestamp to Unix timestamp"""
    try:
        dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
        return int(dt.timestamp())
    except:
        return int(time.time())

def transform_user(old_user: dict) -> dict:
    """Transform a single user from old format to new format"""
    return {
        "activity_visible": True,
        "avatar_urls": {
            "o": old_user.get("avatar") or "",
            "h": old_user.get("avatar") or "",
            "l": old_user.get("avatar") or "",
            "m": old_user.get("avatar") or "",
            "s": old_user.get("avatar") or ""
        },
        "can_ban": False,
        "can_converse": False,
        "can_edit": False,
        "can_follow": False,
        "can_ignore": False,
        "can_post_profile": False,
        "can_view_profile": True,
        "can_view_profile_posts": True,
        "can_warn": False,
        "custom_fields": {
            "facebook": "",
            "skype": "",
            "twitter": ""
        },
        "custom_title": old_user.get("user_title") or "New member",
        "is_admin": old_user.get("is_staff", False),
        "is_banned": False,
        "is_discouraged": False,
        "is_moderator": old_user.get("is_staff", False),
        "is_staff": old_user.get("is_staff", False),
        "is_super_admin": False,
        "last_activity": convert_timestamp(old_user.get("last_access")),
        "location": f"{old_user.get('city', '')}, {old_user.get('province', '')}, {old_user.get('country', '')}".strip(", "),
        "message_count": old_user.get("post_count", 0),
        "profile_banner_urls": {
            "l": None,
            "m": None
        },
        "question_solution_count": 0,
        "reaction_score": old_user.get("like_count", 0),
        "register_date": convert_timestamp(old_user.get("created")),
        "secondary_group_ids": [],
        "signature": old_user.get("signature") or "",
        "trophy_points": 0,
        "user_group_id": 2,
        "user_id": old_user.get("id"),
        "user_state": "valid" if old_user.get("verified_email") else "email_confirm_pending",
        "user_title": "New member",
        "username": old_user.get("display_name"),
        "view_url": f"index.php?members/{old_user.get('display_name').lower().replace(' ', '-')}.{old_user.get('id')}/",
        "visible": True,
        "vote_score": 0,
        "warning_points": 0,
        "website": ""
    }

def transform_users_data(input_file: Path) -> None:
    """Transform users data from old format to new format"""
    print(f"🔄 Transforming users from {input_file}")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
            
        if not old_data or 'users' not in old_data:
            print("❌ No users found in input file")
            return
            
        transformed_users = []
        for user in old_data['users']:
            transformed_user = transform_user(user)
            transformed_users.append(transformed_user)
            
        # Save transformed data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = TRANSFORMED_DIR / f"transformed_users_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "users": transformed_users,
                "total": len(transformed_users),
                "transformed_at": datetime.now().isoformat()
            }, f, indent=4, ensure_ascii=False)
            
        print(f"✨ Successfully transformed {len(transformed_users)} users")
        print(f"💾 Saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error transforming users: {str(e)}")

def main():
    """Main execution function"""
    try:
        # Find most recent users file from old data
        old_user_files = list(OLD_DATA_DIR.glob("users_*.json"))
        if not old_user_files:
            print("❌ No user files found to transform")
            return
            
        latest_file = max(old_user_files, key=lambda x: x.stat().st_mtime)
        transform_users_data(latest_file)
        
    except Exception as e:
        print(f"💥 An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
