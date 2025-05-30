# Language Memo App

A simple desktop application for saving and searching language translation pairs.

## Features
- Save translation pairs (English ↔ Foreign language)
- Search saved pairs by keyword or language
- Manage multiple languages
- Keyboard-friendly workflow (press Enter to save)
- SQLite database storage

## Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/language-memo-app.git
cd language-memo-app

# Install dependencies
pip install FreeSimpleGUI
```

## Usage
```bash
python3 language_app.py
```

### Basic Controls
1. **Add Language**:
   - Type in "New Language" field
   - Click "Add Language"

2. **Save Pairs**:
   - Select language from dropdown
   - Enter English and foreign sentences
   - Press Enter or click "Save Pair"

3. **Search**:
   - Enter keyword (optional)
   - Select language filter
   - Click "Search"

## Keyboard Shortcuts
- `Enter` in any text field → Save current pair
- Automatic focus on English field after saving

## Building Executable
```bash
pyinstaller --onefile --noconsole --add-data="language_pairs.db:." language_app.py
```

## Troubleshooting
- **Database issues**: Delete `language_pairs.db` to reset
- **Font problems**: Edit the `LINUX_FONT` variable in code
- **Window freezes**: Run with console to see errors (`python3 language_app.py`)

## License
MIT License