import json

# Read and parse the JSON file with UTF-8 encoding
with open('topics.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Extract topic IDs using list comprehension
topic_ids = [topic['id'] for topic in data['topics']]

# Write topic IDs to a JSON file
with open('topic_ids.json', 'w', encoding='utf-8') as outfile:
    json.dump({'topic_ids': topic_ids}, outfile, indent=4)

print(f"Successfully wrote {len(topic_ids)} topic IDs to topic_ids.json")
