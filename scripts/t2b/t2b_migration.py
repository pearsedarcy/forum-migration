import asyncio
import aiohttp
import requests
import pandas as pd
import schedule
import time

# 🟢 Old API Configuration
OLD_API_BASE_URL = "https://app.xenforum.net/api/topics"
OLD_API_HEADERS = {
    "Token": "***REMOVED***",
    "Shop": "***REMOVED***"
}

# 🔵 New API Configuration
NEW_API_BASE_URL = "https://newapi.example.com/api/endpoint"  # Change to the correct URL
NEW_API_HEADERS = {
    "Authorization": "Bearer your_new_api_key",
    "Content-Type": "application/json"
}

# ✅ Fetch data asynchronously from the old API
async def fetch_old_topic_data(session, topic_id):
    url = f"{OLD_API_BASE_URL}/{topic_id}.json"
    async with session.get(url, headers=OLD_API_HEADERS) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"❌ Error fetching topic {topic_id}: {response.status}")
            return None

# 🔄 Transform data to match the new API format
def transform_data(old_data):
    if not old_data:
        return None
    return {
        "title": old_data.get("topic_title"),
        "content": old_data.get("topic_content"),
        "author": old_data.get("author_name"),
        "created_at": old_data.get("creation_date"),
        # Add additional transformations if needed
    }

# 🚀 Upload transformed data to the new API
def post_to_new_api(new_data):
    if not new_data:
        return
    response = requests.post(NEW_API_BASE_URL, headers=NEW_API_HEADERS, json=new_data)
    if response.status_code == 201:
        print("✅ Data uploaded successfully.")
    else:
        print(f"❌ Upload error: {response.status_code} - {response.text}")

# 🔄 Automate multiple topics fetching and uploading
async def migrate_topics(topic_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_old_topic_data(session, topic_id) for topic_id in topic_ids]
        results = await asyncio.gather(*tasks)

    for old_data in results:
        new_data = transform_data(old_data)
        post_to_new_api(new_data)

# 🕒 Schedule the script to run daily
def scheduled_job():
    topic_ids = ["123", "456", "789"]  # Replace with actual topic IDs
    asyncio.run(migrate_topics(topic_ids))

# Set the job to run at 10:00 AM daily
schedule.every().day.at("10:00").do(scheduled_job)

print("⏳ Automated Xenforum data migration script is running...")
while True:
    schedule.run_pending()
    time.sleep(60)
