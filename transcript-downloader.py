from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import json
import re
import sys
import os
from datetime import datetime
#This script uses the old version of connecting to the Youtube transcipt API but wrapped with new methods.
#To run this script: E:/WORKSPACE/Scripts/Python/youtube-transcript/.venv/Scripts/python.exe transcript-downloader.py VIDEO_ID
# Example: python transcript-downloader.py DwcePNmFKUw
class TranscriptApiWrapper:
    def __init__(self):
        self.api = YouTubeTranscriptApi()
    #Here
    def get_transcript(self, video_id, language_code=None):
        """
        Mimics the modern get_transcript().
        Returns transcript as list of dicts:
        [{ 'start': float, 'duration': float, 'text': str }, ...]
        """
        transcript_list = self.api.list(video_id)

        # Pick transcript based on language if provided
        if language_code:
            try:
                # Try to find specific language
                for transcript_info in transcript_list:
                    if transcript_info.language_code == language_code:
                        break
                else:
                    # fallback to first available if language not found
                    transcript_info = next(iter(transcript_list))
            except Exception:
                transcript_info = next(iter(transcript_list))
        else:
            transcript_info = next(iter(transcript_list))

        # Fetch transcript and normalize format
        transcript = transcript_info.fetch()
        return [
            {
                "start": entry.start,
                "duration": entry.duration,
                "text": entry.text
            }
            for entry in transcript
        ]

    def list_transcripts(self, video_id):
        """
        Mimics the modern list_transcripts().
        Returns simplified info for each transcript.
        """
        transcript_list = self.api.list(video_id)
        return [
            {
                "language": t.language,
                "language_code": t.language_code,
                "is_generated": getattr(t, "is_generated", None),
                "is_translatable": getattr(t, "is_translatable", None),
            }
            for t in transcript_list
        ]

    def get_video_title(self, video_id):
        """
        Get video title using yt-dlp.
        Returns title string or None if failed.
        """
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('title')
        except Exception as e:
            print(f"Warning: Could not retrieve video title: {e}")
            return None
    
    def _sanitize_title(self, title):
        """
        Sanitize video title for use in filename.
        Converts to lowercase, replaces spaces with underscores,
        removes special characters, and limits length to 50 chars.
        """
        if not title:
            return None
        
        # Convert to lowercase and replace spaces with underscores
        sanitized = title.lower().replace(' ', '_')
        
        # Remove all characters except letters, numbers, and underscores
        sanitized = re.sub(r'[^a-z0-9_]', '', sanitized)
        
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        
        # Limit length to 50 characters
        if len(sanitized) > 50:
            sanitized = sanitized[:50].rstrip('_')
        
        return sanitized if sanitized else None
    
    def _create_folder_name(self, title, video_id):
        """
        Create folder name with format: youtube_title_date_timestamp
        Falls back to video_id_date_timestamp if title sanitization fails.
        """
        # Get current date and time
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        timestamp_str = now.strftime("%H%M%S")
        
        # Try to use sanitized title
        sanitized_title = self._sanitize_title(title)
        if sanitized_title:
            folder_name = f"{sanitized_title}_{date_str}_{timestamp_str}"
        else:
            # Fallback to video ID
            folder_name = f"{video_id}_{date_str}_{timestamp_str}"
        
        return folder_name

    def save_to_file(self, video_id, folder_name, filename=None, format="txt", language_code=None):
        """
        Save transcript to file in the specified subfolder.
        
        Args:
            video_id: YouTube video ID
            folder_name: Name of the subfolder to save files in
            filename: Output filename (auto-generated if None)
            format: "txt", "json", or "srt"
            language_code: Language preference (e.g., "en")
        """
        transcript = self.get_transcript(video_id, language_code)
        
        # Create the folder if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"Created folder: {folder_name}")
        
        if filename is None:
            # Get video title for filename
            title = self.get_video_title(video_id)
            sanitized_title = self._sanitize_title(title)
            
            if sanitized_title:
                filename = f"transcript_{sanitized_title}.{format}"
            else:
                # Fallback to video ID format
                filename = f"transcript_{video_id}.{format}"
        
        # Full path includes the folder
        full_path = os.path.join(folder_name, filename)
        print(f"Saving to: {full_path}")
        
        if format == "txt":
            with open(full_path, 'w', encoding='utf-8') as f:
                for entry in transcript:
                    f.write(f"[{entry['start']:.2f}s] {entry['text']}\n")
        
        elif format == "json":
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(transcript, f, indent=2, ensure_ascii=False)
        
        elif format == "srt":
            with open(full_path, 'w', encoding='utf-8') as f:
                for i, entry in enumerate(transcript, 1):
                    start_time = self._seconds_to_srt_time(entry['start'])
                    end_time = self._seconds_to_srt_time(entry['start'] + entry['duration'])
                    f.write(f"{i}\n{start_time} --> {end_time}\n{entry['text']}\n\n")
        
        print(f"Transcript saved to: {full_path}")
        return full_path

    def _seconds_to_srt_time(self, seconds):
        """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

# Main script
if __name__ == "__main__":
    # Check if video ID was provided as command line argument
    if len(sys.argv) < 2:
        print("Error: Please provide a YouTube video ID as a command line argument.")
        print("Usage: python transcript-downloader.py VIDEO_ID")
        print("Example: python transcript-downloader.py DwcePNmFKUw")
        sys.exit(1)
    
    video_id = sys.argv[1]
    print(f"Processing video ID: {video_id}")
    api = TranscriptApiWrapper()

    try:
        print("Available transcripts:")
        transcripts_info = api.list_transcripts(video_id)
        for i, t in enumerate(transcripts_info):
            print(f"{i+1}. {t['language']} ({t['language_code']})")

        print("\n" + "="*50)
        print("Transcript sample (first 5 entries):")
        
        # Get English transcript if available, otherwise first available
        transcript = api.get_transcript(video_id, language_code="en")
        
        for entry in transcript[:5]:
            print(f"[{entry['start']:.2f}s] {entry['text']}")

        print(f"\nTotal entries: {len(transcript)}")

        # Save transcript to different formats
        print("\n" + "="*50)
        print("Saving transcript files...")
        
        # Create folder name once for all files
        title = api.get_video_title(video_id)
        folder_name = api._create_folder_name(title, video_id)
        
        api.save_to_file(video_id, folder_name, format="txt", language_code="en")
        api.save_to_file(video_id, folder_name, format="json", language_code="en")
        api.save_to_file(video_id, folder_name, format="srt", language_code="en")

    except Exception as e:
        print(f"Error: {e}")