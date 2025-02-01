import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class ForumScraper:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.root_dir / 'data'
        self.processed_dir = self.data_dir / 'processed'
        self.forums: Dict = {}
        self.topics: Dict = {}
        self.users: Dict = {}
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)

    def load_json_file(self, filename: str) -> Dict:
        """Load and parse a JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return {}

    def load_data(self):
        """Load all data files"""
        forums_data = self.load_json_file('forums.json')
        topics_data = self.load_json_file('topics.json')
        users_data = self.load_json_file('users.json')
        
        self.forums = forums_data.get('forums', [])
        self.topics = topics_data.get('topics', [])
        self.users = users_data.get('users', [])

    def process_forums(self) -> List[Dict]:
        """Process forum data into transferable format"""
        processed_forums = []
        
        def process_forum(forum: Dict) -> Dict:
            return {
                'id': forum.get('id'),
                'title': forum.get('title'),
                'slug': forum.get('slug'),
                'description': forum.get('description'),
                'parent_id': forum.get('parent_id', 0),
                'position': forum.get('position', 0),
                'is_folder': forum.get('is_folder', False),
                'status': forum.get('status', True),
                'created_at': forum.get('created'),
                'updated_at': forum.get('updated'),
                'settings': forum.get('settings', {})
            }

        # Process main forums and their children
        for forum in self.forums:
            processed_forums.append(process_forum(forum))
            
            # Process child forums
            for child in forum.get('children', []):
                processed_forums.append(process_forum(child))
                
        return processed_forums

    def process_topics(self) -> List[Dict]:
        """Process topic data into transferable format"""
        processed_topics = []
        
        for topic in self.topics:
            processed_topic = {
                'id': topic.get('id'),
                'forum_id': topic.get('forum_id'),
                'user_id': topic.get('user_id'),
                'title': topic.get('title'),
                'slug': topic.get('slug'),
                'post_count': topic.get('no_posts', 0),
                'view_count': topic.get('view_count', 0),
                'pinned': topic.get('pinned', False),
                'locked': topic.get('locked', False),
                'deleted': topic.get('deleted', False),
                'created_at': topic.get('created'),
                'updated_at': topic.get('updated')
            }
            processed_topics.append(processed_topic)
            
        return processed_topics

    def export_data(self):
        """Export processed data to JSON files"""
        processed_data = {
            'forums': self.process_forums(),
            'topics': self.process_topics()
        }
        
        # Export to new JSON file in processed directory
        output_file = self.processed_dir / 'processed_forum_data.json'
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2)
            print(f"✅ Data exported successfully to {output_file}")
        except Exception as e:
            print(f"❌ Error exporting data: {e}")

def main():
    scraper = ForumScraper()
    scraper.load_data()
    scraper.export_data()
    print("🎉 Forum data processing completed!")

if __name__ == "__main__":
    main()
