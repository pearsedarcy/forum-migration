# 🤖 XenForo Forum Scraper

A Python-based tool for extracting and processing data from XenForo forums using the XenForo API.

## ✨ Features

- 🔍 API endpoint testing and validation
- 📥 Data extraction from multiple endpoints
- ⏱️ Automated JSON file generation with timestamps
- 🔐 Environment variable support for secure configuration
- 🛡️ Comprehensive error handling and logging

## 📋 Prerequisites

- 🐍 Python 3.8+
- 📦 pip (Python package installer)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/pearsedarcy/forum-migration.git
cd forum-migration
```

2. Install required packages:
```bash
pip install requests python-dotenv
```

3. Create `.env` file with your XenForo credentials:
```properties
XENFORO_BASE_URL=your_forum_url
XENFORO_API_KEY=your_api_key
```

## 🎮 Usage

### 🔰 Basic Usage
```bash
python scripts/xenforo_scrape.py
```

### 📜 Available Scripts

- 🌐 `scripts/xenforo_scrape.py`: Tests API connectivity and downloads forum data
- 🔄 `scripts/xenforum(old)/scrape_wrongboarding_forum.py`: Processes downloaded data into a consistent format

### 📤 Output

The scripts generate several JSON files:
- 📄 Individual endpoint responses: `xenforo_[endpoint]_[timestamp].json`
- 📚 Combined responses: `xenforo_all_responses_[timestamp].json`
- 📊 Processed data: `data/processed/processed_forum_data.json`

## ⚙️ Configuration

### 🔑 Environment Variables

- 🌍 `XENFORO_BASE_URL`: Your XenForo forum's base URL
- 🔒 `XENFORO_API_KEY`: Your XenForo API key

## 📁 Project Structure

```
forum-migration/
├── 📂 scripts/
│   ├── 📂 xenforum(old)/
│   │   └── 🔄 scrape_wrongboarding_forum.py
│   └── 🌐 xenforo_scrape.py
├── 📂 data/
│   └── 📊 processed/
├── 🔐 .env
├── 📝 .gitignore
└── 📖 README.md
```

## 🤝 Contributing

1. 🍴 Fork the repository
2. 🌿 Create your feature branch
3. ✍️ Commit your changes
4. 🚀 Push to the branch
5. 📬 Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
