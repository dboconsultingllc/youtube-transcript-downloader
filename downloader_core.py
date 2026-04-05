from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import json
import re
import os
from datetime import datetime


def _validate_video_id(video_id: str) -> bool:
    """YouTube video IDs are 11 alphanumeric characters (a-z, A-Z, 0-9, -, _)."""
    return bool(re.match(r'^[a-zA-Z0-9_-]{11}$', video_id))


class TranscriptApiWrapper:
    def __init__(self, output_dir=None):
        self.api = YouTubeTranscriptApi()
        self.output_dir = output_dir or os.getcwd()

    def get_transcript(self, video_id, language_code=None):
        """
        Fetch transcript for a video.
        Returns transcript as list of dicts: [{start, duration, text}, ...]
        """
        transcript_list = self.api.list(video_id)

        if language_code:
            try:
                for transcript_info in transcript_list:
                    if transcript_info.language_code == language_code:
                        break
                else:
                    transcript_info = next(iter(transcript_list))
            except Exception:
                transcript_info = next(iter(transcript_list))
        else:
            transcript_info = next(iter(transcript_list))

        transcript = transcript_info.fetch()
        return [
            {
                "start": entry.start,
                "duration": entry.duration,
                "text": entry.text,
            }
            for entry in transcript
        ]

    def list_transcripts(self, video_id):
        """
        List available transcripts for a video.
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
        Returns title string or None if unavailable.
        """
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get("title")
        except Exception as e:
            print(f"Warning: Could not retrieve video title: {e}")
            return None

    def _sanitize_title(self, title):
        """
        Sanitize video title for use in a filename.
        Returns lowercase underscored string (max 50 chars) or None.
        """
        if not title:
            return None

        sanitized = title.lower().replace(" ", "_")
        sanitized = re.sub(r"[^a-z0-9_]", "", sanitized)
        sanitized = re.sub(r"_+", "_", sanitized)
        sanitized = sanitized.strip("_")

        if len(sanitized) > 50:
            sanitized = sanitized[:50].rstrip("_")

        return sanitized if sanitized else None

    def _create_folder_name(self, title, video_id):
        """
        Build folder name: sanitized_title_YYYYMMDD_HHMMSS
        Falls back to video_id if title sanitization fails.
        """
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        timestamp_str = now.strftime("%H%M%S")

        sanitized_title = self._sanitize_title(title)
        if sanitized_title:
            return f"{sanitized_title}_{date_str}_{timestamp_str}"
        return f"{video_id}_{date_str}_{timestamp_str}"

    def save_to_file(self, video_id, folder_name, filename=None, format="txt",
                     language_code=None, transcript=None):
        """
        Write transcript to a file inside output_dir/folder_name.

        Args:
            video_id:       YouTube video ID
            folder_name:    Subfolder name (relative to self.output_dir)
            filename:       Output filename; auto-generated from title if None
            format:         "txt", "json", or "srt"
            language_code:  Language preference (e.g. "en")
            transcript:     Pre-fetched transcript list; fetched if None
        Returns:
            Absolute path of the file written.
        """
        if transcript is None:
            transcript = self.get_transcript(video_id, language_code)

        full_folder = os.path.join(self.output_dir, folder_name)
        os.makedirs(full_folder, exist_ok=True)

        if filename is None:
            title = self.get_video_title(video_id)
            sanitized_title = self._sanitize_title(title)
            base = sanitized_title if sanitized_title else video_id
            filename = f"transcript_{base}.{format}"

        full_path = os.path.join(full_folder, filename)
        print(f"Saving to: {full_path}")

        if format == "txt":
            with open(full_path, "w", encoding="utf-8") as f:
                for entry in transcript:
                    f.write(f"[{entry['start']:.2f}s] {entry['text']}\n")

        elif format == "json":
            with open(full_path, "w", encoding="utf-8") as f:
                json.dump(transcript, f, indent=2, ensure_ascii=False)

        elif format == "srt":
            with open(full_path, "w", encoding="utf-8") as f:
                for i, entry in enumerate(transcript, 1):
                    start_time = self._seconds_to_srt_time(entry["start"])
                    end_time = self._seconds_to_srt_time(entry["start"] + entry["duration"])
                    f.write(f"{i}\n{start_time} --> {end_time}\n{entry['text']}\n\n")

        print(f"Transcript saved to: {full_path}")
        return full_path

    def _seconds_to_srt_time(self, seconds):
        """Convert seconds (float) to SRT time format HH:MM:SS,mmm."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"


def download_transcript(video_id, output_dir, language_code="en", formats=None):
    """
    Download and save a YouTube transcript to files.

    Args:
        video_id:       YouTube video ID (11 alphanumeric chars)
        output_dir:     Root directory for output folders/files
        language_code:  Preferred transcript language (default "en")
        formats:        List of formats to save; default ["txt", "json", "srt"]

    Returns:
        dict:
            folder  (str | None)  – absolute path of the created subfolder
            files   (list[str])   – absolute paths of files written
            error   (str | None)  – error message, or None on full success
    """
    if formats is None:
        formats = ["txt", "json", "srt"]

    if not _validate_video_id(video_id):
        return {
            "folder": None,
            "files": [],
            "error": f"Invalid video ID format: '{video_id}'. Expected 11 alphanumeric characters.",
        }

    api = TranscriptApiWrapper(output_dir=output_dir)

    title = api.get_video_title(video_id)
    sanitized_title = api._sanitize_title(title)
    folder_name = api._create_folder_name(title, video_id)
    base_name = sanitized_title or video_id

    try:
        transcript = api.get_transcript(video_id, language_code=language_code)
    except Exception as e:
        return {"folder": None, "files": [], "error": f"Could not fetch transcript: {e}"}

    files = []
    write_errors = []
    for fmt in formats:
        filename = f"transcript_{base_name}.{fmt}"
        try:
            path = api.save_to_file(
                video_id, folder_name,
                filename=filename, format=fmt,
                language_code=language_code, transcript=transcript,
            )
            files.append(path)
        except Exception as e:
            write_errors.append(f"{fmt}: {e}")

    if write_errors and not files:
        return {"folder": None, "files": [], "error": "; ".join(write_errors)}

    folder_path = os.path.join(output_dir, folder_name)
    return {
        "folder": folder_path,
        "files": files,
        "error": "; ".join(write_errors) if write_errors else None,
    }
