# transcript-downloader.py — standalone CLI interface (preserved for direct use)
# Core logic lives in downloader_core.py and is also consumed by the Docker API service.
# Usage: python transcript-downloader.py VIDEO_ID
# Example: python transcript-downloader.py DwcePNmFKUw
import sys
import os
from downloader_core import TranscriptApiWrapper


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide a YouTube video ID as a command line argument.")
        print("Usage: python transcript-downloader.py VIDEO_ID")
        print("Example: python transcript-downloader.py DwcePNmFKUw")
        sys.exit(1)

    video_id = sys.argv[1]
    output_dir = os.environ.get("OUTPUT_DIR", os.getcwd())
    print(f"Processing video ID: {video_id}")

    api = TranscriptApiWrapper(output_dir=output_dir)

    try:
        print("Available transcripts:")
        transcripts_info = api.list_transcripts(video_id)
        for i, t in enumerate(transcripts_info):
            print(f"{i+1}. {t['language']} ({t['language_code']})")

        print("\n" + "=" * 50)
        print("Transcript sample (first 5 entries):")

        transcript = api.get_transcript(video_id, language_code="en")

        for entry in transcript[:5]:
            print(f"[{entry['start']:.2f}s] {entry['text']}")

        print(f"\nTotal entries: {len(transcript)}")

        print("\n" + "=" * 50)
        print("Saving transcript files...")

        title = api.get_video_title(video_id)
        folder_name = api._create_folder_name(title, video_id)
        sanitized_title = api._sanitize_title(title)
        base_name = sanitized_title or video_id

        for fmt in ["txt", "json", "srt"]:
            filename = f"transcript_{base_name}.{fmt}"
            api.save_to_file(
                video_id, folder_name,
                filename=filename, format=fmt,
                language_code="en", transcript=transcript,
            )

    except Exception as e:
        print(f"Error: {e}")