# YouTube Transcript Downloader

A Python script that downloads YouTube video transcripts and organizes them in title-based folders and filenames.

## Features

- 📹 Downloads transcripts from any YouTube video using video ID
- 📁 Creates organized folders with format: `video_title_date_timestamp`
- 📄 Generates multiple formats: `.txt`, `.json`, and `.srt`
- 🏷️ Uses video titles for meaningful filenames instead of cryptic video IDs
- 🚀 Perfect for RAG pipelines (JSON format recommended)
- 🛡️ Robust error handling with fallback to video ID if title unavailable

## Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/youtube-transcript-downloader.git
cd youtube-transcript-downloader
```

2. Create a virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux  
source .venv/bin/activate
```

4. Install dependencies:
```bash
pip install youtube-transcript-api yt-dlp
```

## Usage

Run the script with a YouTube video ID:

```bash
python transcript-downloader.py VIDEO_ID
```

### Examples:

```bash
python transcript-downloader.py DwcePNmFKUw
python transcript-downloader.py E7QVNvxjFos
```

### Getting YouTube Video ID:
From a URL like `https://www.youtube.com/watch?v=DwcePNmFKUw`, the video ID is `DwcePNmFKUw` (the part after `v=`).

## Output Structure

The script creates a folder named with the format `video_title_date_timestamp` containing:

```
video_title_20260404_175823/
├── transcript_video_title.txt    # Plain text with timestamps
├── transcript_video_title.json   # Structured data (best for RAG)  
└── transcript_video_title.srt    # Subtitle format
```

## File Formats

- **`.txt`**: Plain text with timestamps `[0.00s] transcript text here`
- **`.json`**: Structured format with start time, duration, and text (recommended for RAG pipelines)
- **`.srt`**: Standard subtitle format for video players

## For RAG Pipelines

The **JSON format** is recommended for RAG pipelines because:
- Clean structured data with separated text and metadata
- Easy chunking with timestamp preservation  
- Source attribution capabilities
- No formatting interference with embeddings

## Requirements

- Python 3.7+
- youtube-transcript-api
- yt-dlp

## License

MIT License