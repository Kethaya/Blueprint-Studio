# Blueprint Asset Builder

A professional desktop application for documentary editors to build asset libraries from Blueprint JSON files.

## Features

- **Scene Management**: Browse and select scenes from your blueprint
- **Asset Search**: Search for videos, images, logos, icons, fonts, and SFX
- **Asset Download**: Download assets directly to organized folders
- **Live Preview**: Real-time preview updates as you make changes
- **Selection Tracking**: Automatic selection.json management
- **Scene Board**: Visual grid overview of all scenes
- **Threaded Operations**: Non-blocking search and download operations

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python app.py
```

## Project Structure

```
/workspace/
├── app.py              # Main application entry point
├── preview.py          # Legacy preview file (backup)
├── blueprint.json      # Read-only blueprint schema
├── selection.json      # Auto-generated selection tracking
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── ui/                 # UI components
├── services/           # API and download services
├── models/             # Data models
├── utils/              # Utility functions
├── core/               # Core application logic
├── assets/             # Downloaded assets
│   ├── videos/
│   ├── images/
│   ├── logos/
│   ├── screenshots/
│   ├── icons/
│   ├── fonts/
│   └── sfx/
├── cache/              # Cached thumbnails and search results
└── exports/            # Export files
```

## Blueprint JSON Schema

The application reads from a blueprint.json file with the following structure:

```json
{
  "project": {
    "title": "Project Name",
    "description": "Project description",
    "language": "English",
    "default_font": "Font Name"
  },
  "scenes": [
    {
      "scene_id": 1,
      "scene_type": "video",
      "title": "Scene Title",
      "narration": "Narration text",
      "subtitle": "",
      "keywords": ["keyword1", "keyword2"],
      "search": {
        "video": ["search term"],
        "image": ["search term"],
        "logo": ["search term"],
        "website": ["https://example.com"],
        "icon": ["search term"],
        "sfx": ["search term"]
      },
      "text": {
        "enabled": false,
        "content": "",
        "font": ""
      },
      "editing_note": "Editing instructions"
    }
  ]
}
```

## Selection JSON Schema

The application automatically manages selection.json:

```json
{
  "project": {
    "title": "Project Name"
  },
  "scenes": [
    {
      "scene_id": 1,
      "selection": {
        "video": {
          "provider": "Pexels",
          "id": 123456,
          "title": "Video Title",
          "url": "https://...",
          "local_path": "assets/videos/...",
          "downloaded": true
        },
        "image": {},
        "logo": {},
        "website": {"url": "https://..."},
        "website_screenshot": {"local_path": "assets/screenshots/..."},
        "icon": {},
        "text": {"content": "", "font": ""},
        "sfx": {}
      }
    }
  ]
}
```

## Search Providers

- **Video**: Pexels API
- **Image**: Pexels API
- **Logo**: Logo.dev / Clearbit API
- **Website**: User-provided URL
- **Website Screenshot**: Screenshot capture service
- **Icon**: Icon library
- **Font**: Local fonts folder
- **SFX**: Local SFX library

## Keyboard Shortcuts

- `Ctrl+S`: Save project
- `Ctrl+O`: Open blueprint
- `Ctrl+D`: Download selected assets
- `F5`: Refresh

## License

MIT License
