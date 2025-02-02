import sys
from pathlib import Path
from datetime import datetime
import time

# Add parent directory to path to import from sibling directories
SCRIPT_DIR = Path(__file__).parent.parent
sys.path.append(str(SCRIPT_DIR))

# Update imports to use correct paths
from xenforum_old.user_harvester import harvest_users as harvest_old_users
from xenforo_new.user_harvester import harvest_users as harvest_new_users
from transformers.user_format_transformer import transform_users_data
from validators.user_data_validator import generate_validation_report

# Create __init__.py files in directories
def ensure_init_files():
    """Ensure __init__.py files exist in all module directories"""
    module_dirs = [
        SCRIPT_DIR / 'xenforum_old',
        SCRIPT_DIR / 'xenforo_new',
        SCRIPT_DIR / 'transformers',
        SCRIPT_DIR / 'validators'
    ]
    
    for dir_path in module_dirs:
        init_file = dir_path / '__init__.py'
        if not init_file.exists():
            init_file.touch()
            print(f"Created {init_file}")

class UserMigrationMatrix:
    def __init__(self):
        """Initialize paths and create required directories"""
        self.root_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.root_dir / 'data'
        
        # Ensure all required directories exist
        for dir_name in ['xenforum/users/processed', 'xenforo/users/processed', 
                        'transformed/users', 'validation/users']:
            (self.data_dir / dir_name).mkdir(parents=True, exist_ok=True)
    
    def run_harvest_phase(self) -> bool:
        """Phase 1: Harvest users from both old and new forums"""
        print("\n🔄 PHASE 1: DATA HARVESTING")
        print("=" * 50)
        
        try:
            print("\n📥 Harvesting users from old forum (XenForum)...")
            harvest_old_users()
            
            print("\n📥 Harvesting users from new forum (XenForo)...")
            harvest_new_users()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Harvest phase failed: {str(e)}")
            return False

    def run_transform_phase(self) -> bool:
        """Phase 2: Transform old forum data to new format"""
        print("\n🔄 PHASE 2: DATA TRANSFORMATION")
        print("=" * 50)
        
        try:
            # Find most recent old forum user data
            old_data_dir = self.data_dir / 'xenforum' / 'users' / 'processed'
            old_user_files = list(old_data_dir.glob("users_*.json"))
            
            if not old_user_files:
                print("❌ No old forum user data found to transform")
                return False
                
            latest_file = max(old_user_files, key=lambda x: x.stat().st_mtime)
            print(f"\n📄 Using latest old forum data: {latest_file.name}")
            
            transform_users_data(latest_file)
            return True
            
        except Exception as e:
            print(f"\n❌ Transform phase failed: {str(e)}")
            return False

    def run_validation_phase(self) -> bool:
        """Phase 3: Validate transformed data against new format"""
        print("\n🔄 PHASE 3: DATA VALIDATION")
        print("=" * 50)
        
        try:
            results = generate_validation_report()
            
            if not results:
                return False
                
            # Detailed validation summary
            total = results['total_users']
            valid = results['valid_users']
            invalid = results['invalid_users']
            
            print("\n📊 Validation Results:")
            print(f"Total Users: {total}")
            print(f"Valid Users: {valid} ({(valid/total)*100:.1f}%)")
            print(f"Invalid Users: {invalid} ({(invalid/total)*100:.1f}%)")
            
            return invalid == 0
            
        except Exception as e:
            print(f"\n❌ Validation phase failed: {str(e)}")
            return False

    def execute(self):
        """Execute all migration phases in sequence"""
        start_time = time.time()
        
        print("\n🚀 Starting User Migration Matrix")
        print("=" * 50)
        
        # Execute phases
        harvest_success = self.run_harvest_phase()
        if not harvest_success:
            print("\n❌ Migration failed during harvest phase")
            return False
            
        transform_success = self.run_transform_phase()
        if not transform_success:
            print("\n❌ Migration failed during transform phase")
            return False
            
        validation_success = self.run_validation_phase()
        if not validation_success:
            print("\n⚠️ Migration completed but validation found issues")
        
        # Final summary
        duration = time.time() - start_time
        print("\n✨ Migration Matrix Complete")
        print(f"⏱️ Total duration: {duration:.1f} seconds")
        print("=" * 50)
        
        return validation_success

if __name__ == "__main__":
    ensure_init_files()  # Create necessary __init__.py files
    matrix = UserMigrationMatrix()
    success = matrix.execute()
    sys.exit(0 if success else 1)
