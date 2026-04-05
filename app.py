import os
import re
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

from downloader_core import download_transcript

app = FastAPI(title="YouTube Transcript API")

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/data/transcripts")

_VIDEO_ID_RE = re.compile(r'^[a-zA-Z0-9_-]{11}$')
_ALLOWED_FORMATS = {"txt", "json", "srt"}


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class TranscriptRequest(BaseModel):
    video_id: str
    language_code: str = "en"
    formats: List[str] = ["txt", "json", "srt"]

    @field_validator("video_id")
    @classmethod
    def validate_video_id(cls, v: str) -> str:
        if not _VIDEO_ID_RE.match(v):
            raise ValueError(
                f"Invalid YouTube video ID: '{v}'. "
                "Must be exactly 11 alphanumeric characters (a-z, A-Z, 0-9, -, _)."
            )
        return v

    @field_validator("formats")
    @classmethod
    def validate_formats(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("At least one format must be specified.")
        invalid = set(v) - _ALLOWED_FORMATS
        if invalid:
            raise ValueError(
                f"Unsupported format(s): {sorted(invalid)}. "
                f"Allowed: {sorted(_ALLOWED_FORMATS)}."
            )
        return v


class TranscriptResponse(BaseModel):
    status: str
    folder: Optional[str]
    files: List[str]
    error: Optional[str]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/transcripts", response_model=TranscriptResponse)
def create_transcript(request: TranscriptRequest):
    result = download_transcript(
        video_id=request.video_id,
        output_dir=OUTPUT_DIR,
        language_code=request.language_code,
        formats=request.formats,
    )

    error = result.get("error")
    files = result.get("files", [])

    if error and not files:
        if "Invalid video ID" in error:
            raise HTTPException(status_code=400, detail=error)
        if "Could not fetch transcript" in error:
            raise HTTPException(status_code=502, detail=error)
        raise HTTPException(status_code=500, detail=error)

    return TranscriptResponse(
        status="success" if not error else "partial",
        folder=result.get("folder"),
        files=files,
        error=error,
    )
