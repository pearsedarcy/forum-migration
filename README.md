# 🤖 XenForo Forum Migration Tool

A Python-based tool for migrating data between XenForum and XenForo platforms.

## ✨ Features

- 🔄 Automated migration between forum platforms
- 📊 User data validation and transformation
- 🔍 Migration progress tracking and reporting
- 🛡️ Comprehensive error handling and logging
- ⏱️ Performance metrics for migration phases

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

3. Create `.env` file with your credentials:
```properties
# XenForo Configuration
XENFORO_BASE_URL=your_forum_url
XENFORO_API_KEY=your_api_key

# XenForum Configuration
XENFORUM_OLD_BASE_URL=https://app.xenforum.net/api/topics
XENFORUM_OLD_TOKEN=your_xenforum_token
XENFORUM_OLD_SHOP=your_shop_identifier
```

## 🎮 Usage

### 🔰 Basic Usage

Run the migration workflow:
```bash
python scripts/t2b/t2b_user_matrix.py
```

The migration process runs in three phases:
1. 📥 Data Harvesting: Extracts user data from both forums
2. 🔄 Data Transformation: Converts data to the target format
3. ✅ Data Validation: Verifies the transformed data

### 📤 Output

The script generates data in the following structure:
```
data/
├── xenforum/
│   └── users/
│       └── processed/
├── xenforo/
│   └── users/
│       └── processed/
├── transformed/
│   └── users/
└── validation/
    └── users/
```

## ⚙️ Configuration

### 🔑 Environment Variables

- 🌍 `XENFORO_BASE_URL`: Your XenForo forum's base URL
- 🔒 `XENFORO_API_KEY`: Your XenForo API key
- 🌐 `XENFORUM_OLD_BASE_URL`: Base URL for old XenForum API
- 🔑 `XENFORUM_OLD_TOKEN`: Authentication token for XenForum API
- 🏪 `XENFORUM_OLD_SHOP`: Shop identifier for XenForum

## 📁 Project Structure

```
forum-migration/
├── 📂 scripts/
│   ├── 📂 t2b/
│   │   └── 🔄 t2b_user_matrix.py
│   ├── 📂 xenforo_new/
│   │   ├── 🌐 xenforo_scrape.py
│   │   └── 👥 user_harvester.py
│   ├── 📂 xenforum_old/
│   │   ├── 🌐 scrape_wrongboarding_forum.py
│   │   └── 👥 user_harvester.py
│   ├── 📂 transformers/
│   │   └── 🔄 user_format_transformer.py
│   └── 📂 validators/
│       └── ✅ user_data_validator.py
├── 📂 data/
│   ├── 📂 xenforum/
│   │   └── 📂 users/
│   │       └── 📂 processed/
│   ├── 📂 xenforo/
│   │   └── 📂 users/
│   │       └── 📂 processed/
│   ├── 📂 transformed/
│   │   └── 📂 users/
│   └── 📂 validation/
│       └── 📂 users/
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

This project is licensed under the MIT License - see the LICENSE file for
details.
