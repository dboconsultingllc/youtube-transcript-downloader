# YouTube Transcript Downloader

Download YouTube transcripts in multiple formats, either as:

- A standalone CLI script
- A Dockerized HTTP API service for other containers

## Features

- 📹 Downloads transcripts from any YouTube video using video ID
- 📁 Creates organized folders with format: `video_title_date_timestamp`
- 📄 Generates multiple formats: `.txt`, `.json`, and `.srt`
- 🏷️ Uses video titles for meaningful filenames instead of cryptic video IDs
- 🚀 Perfect for RAG pipelines (JSON format recommended)
- 🛡️ Robust error handling with fallback to video ID if title unavailable
- 🐳 Optional Docker API mode for cross-container usage
- 💾 Easy host file access via bind-mounted `./transcripts` folder

## Modes

### 1. Standalone Script

Use this when you want to run one video at a time from your local shell.

Entry point: `transcript-downloader.py`

### 2. Docker API Service

Use this when you want a long-running service that other containers can call over HTTP.

Entry point: `app.py` (served by `uvicorn`)

## Installation (Standalone)

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
pip install -r requirements.txt
```

## Usage (Standalone)

Run the script with a YouTube video ID:

```bash
python transcript-downloader.py VIDEO_ID
```

### Examples:

```bash
python transcript-downloader.py DwcePNmFKUw
python transcript-downloader.py E7QVNvxjFos
```

Optional output directory:

```bash
# Windows (PowerShell)
$env:OUTPUT_DIR = "C:\\temp\\transcripts"
python transcript-downloader.py DwcePNmFKUw

# macOS/Linux
OUTPUT_DIR=./transcripts python transcript-downloader.py DwcePNmFKUw
```

## Usage (Docker API)

Build and run with Docker Compose:

```bash
docker compose up --build
```

API will be available at:

```text
http://localhost:8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Create transcript files:

```bash
curl -X POST http://localhost:8000/transcripts \
	-H "Content-Type: application/json" \
	-d '{"video_id":"DwcePNmFKUw"}'
```

Request body options:

- `video_id` (required): YouTube video ID (11 chars)
- `language_code` (optional): defaults to `en`
- `formats` (optional): subset of `txt`, `json`, `srt`

Example with options:

```bash
curl -X POST http://localhost:8000/transcripts \
	-H "Content-Type: application/json" \
	-d '{"video_id":"DwcePNmFKUw","language_code":"en","formats":["json","srt"]}'
```

### Using from Other Containers

- Service name on Compose network: `transcript-api`
- Endpoint from sibling containers: `http://transcript-api:8000/transcripts`

An example consumer service is included in `docker-compose.yml` under the `example` profile:

```bash
docker compose --profile example up --build
```

### Getting YouTube Video ID:
From a URL like `https://www.youtube.com/watch?v=DwcePNmFKUw`, the video ID is `DwcePNmFKUw` (the part after `v=`).

## Output Structure

Both modes create a folder named with the format `video_title_date_timestamp` containing:

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

- Python 3.11+ recommended
- Dependencies listed in `requirements.txt`
- Docker Desktop (only for Docker API mode)

## License

MIT License