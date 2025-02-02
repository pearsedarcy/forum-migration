import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Setup paths
ROOT_DIR = Path(__file__).parent.parent.parent
TRANSFORMED_DIR = ROOT_DIR / 'data' / 'transformed' / 'users'
XENFORO_DIR = ROOT_DIR / 'data' / 'xenforo' / 'users' / 'processed'
VALIDATION_DIR = ROOT_DIR / 'data' / 'validation' / 'users'

# Ensure validation directory exists
VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

def load_latest_file(directory: Path, pattern: str) -> Tuple[Path, dict]:
    """Load the most recent JSON file matching the pattern from directory"""
    files = list(directory.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files matching {pattern} found in {directory}")
    
    latest_file = max(files, key=lambda x: x.stat().st_mtime)
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return latest_file, data

def validate_user_structure(transformed_user: dict, xenforo_user: dict) -> List[str]:
    """Compare user data structure against XenForo format"""
    issues = []
    
    # Check for missing required fields
    required_fields = set(xenforo_user.keys())
    user_fields = set(transformed_user.keys())
    
    missing_fields = required_fields - user_fields
    if missing_fields:
        issues.append(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Check field types
    for field, value in transformed_user.items():
        if field in xenforo_user:
            if type(value) != type(xenforo_user[field]):
                issues.append(
                    f"Field '{field}' type mismatch: "
                    f"got {type(value).__name__}, "
                    f"expected {type(xenforo_user[field]).__name__}"
                )
    
    # Validate specific field values
    field_validations = {
        "user_state": ["valid", "email_confirm_pending", "moderated"],
        "user_group_id": lambda x: isinstance(x, int) and x > 0,
        "message_count": lambda x: isinstance(x, int) and x >= 0,
        "user_id": lambda x: isinstance(x, int) and x > 0
    }
    
    for field, validation in field_validations.items():
        if field in transformed_user:
            value = transformed_user[field]
            if isinstance(validation, list) and value not in validation:
                issues.append(f"Invalid {field} value: {value}")
            elif callable(validation) and not validation(value):
                issues.append(f"Invalid {field} value: {value}")
    
    return issues

def generate_validation_report() -> dict:
    """Generate validation report comparing transformed data to XenForo format"""
    try:
        # Load latest files
        transformed_file, transformed_data = load_latest_file(TRANSFORMED_DIR, "transformed_users_*.json")
        xenforo_file, xenforo_data = load_latest_file(XENFORO_DIR, "xenforo_users_*.json")
        
        transformed_users = transformed_data['users']
        xenforo_template = xenforo_data['users'][0]  # Use first user as template
        
        # Validation results
        results = {
            "timestamp": datetime.now().isoformat(),
            "transformed_file": str(transformed_file),
            "xenforo_file": str(xenforo_file),
            "total_users": len(transformed_users),
            "valid_users": 0,
            "invalid_users": 0,
            "issues": []
        }
        
        # Validate each transformed user
        for i, user in enumerate(transformed_users, 1):
            user_issues = validate_user_structure(user, xenforo_template)
            
            if user_issues:
                results["invalid_users"] += 1
                results["issues"].append({
                    "user_id": user.get("user_id", f"Unknown-{i}"),
                    "username": user.get("username", "Unknown"),
                    "issues": user_issues
                })
            else:
                results["valid_users"] += 1
        
        # Save validation report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = VALIDATION_DIR / f"validation_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
            
        # Print summary
        print("\n📊 Validation Summary:")
        print(f"✅ Valid users: {results['valid_users']}")
        print(f"❌ Invalid users: {results['invalid_users']}")
        print(f"📝 Full report saved to: {report_file}")
        
        return results
        
    except Exception as e:
        print(f"💥 Validation error: {str(e)}")
        return None

def main():
    """Main execution function"""
    print("🔍 Starting user data validation...")
    results = generate_validation_report()
    
    if results and results["invalid_users"] > 0:
        print("\n⚠️ Some users require attention!")
        print("Please check the validation report for details.")
    elif results:
        print("\n✨ All users passed validation!")

if __name__ == "__main__":
    main()
