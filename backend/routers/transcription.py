from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import whisper
import os
import logging
from typing import List, Dict

router = APIRouter(prefix="/api/transcription", tags=["transcription"])
logger = logging.getLogger(__name__)

# Globals will be injected
embedding_engine = None
vector_store = None
llm_backend = None

def set_globals(emb, vs, llm):
    global embedding_engine, vector_store, llm_backend
    embedding_engine = emb
    vector_store = vs
    llm_backend = llm

# Global Whisper model
WHISPER_MODEL = None

def get_whisper_model():
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        logger.info("Loading Whisper model...")
        WHISPER_MODEL = whisper.load_model("base")  # FREE!
    return WHISPER_MODEL

class TranscriptionResponse(BaseModel):
    text: str
    language: str
    segments: List[Dict]
    word_count: int
    duration: float

@router.post("/transcribe-file", response_model=TranscriptionResponse)
async def transcribe_file(file: UploadFile = File(...)):
    """
    Transcribe uploaded audio/video file
    FREE alternative to Clipto AI transcription
    """
    
    try:
        # Save uploaded file
        temp_path = f"/tmp/{file.filename}"
        os.makedirs('/tmp', exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # Transcribe with Whisper
        logger.info(f"Transcribing {file.filename}...")
        model = get_whisper_model()
        result = model.transcribe(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        return TranscriptionResponse(
            text=result['text'],
            language=result['language'],
            segments=result['segments'],
            word_count=len(result['text'].split()),
            duration=result['segments'][-1]['end'] if result['segments'] else 0
        )
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transcribe-url")
async def transcribe_url(url: str):
    """
    Transcribe from URL (YouTube, etc.)
    Combines yt-dlp + Whisper (both FREE!)
    """
    
    import yt_dlp
    
    try:
        # Download audio
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '/tmp/%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
        }
        
        os.makedirs('/tmp', exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            audio_path = f"/tmp/{video_id}.mp3"
        
        # Transcribe
        model = get_whisper_model()
        result = model.transcribe(audio_path)
        
        # Clean up
        os.remove(audio_path)
        
        return {
            "title": info.get('title'),
            "transcription": result['text'],
            "language": result['language'],
            "duration": info.get('duration')
        }
        
    except Exception as e:
        logger.error(f"URL transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-captions")
async def generate_captions(text: str, format: str = "srt"):
    """
    Convert transcription to caption files (SRT, VTT)
    """
    
    # Generate timestamps (simplified)
    words = text.split()
    words_per_line = 10
    seconds_per_word = 0.4
    
    captions = []
    for i in range(0, len(words), words_per_line):
        line_words = words[i:i+words_per_line]
        start_time = i * seconds_per_word
        end_time = (i + len(line_words)) * seconds_per_word
        
        captions.append({
            'index': len(captions) + 1,
            'start': start_time,
            'end': end_time,
            'text': ' '.join(line_words)
        })
    
    if format == "srt":
        # Generate SRT format
        srt_content = ""
        for cap in captions:
            srt_content += f"{cap['index']}\n"
            srt_content += f"{format_timestamp(cap['start'])} --> {format_timestamp(cap['end'])}\n"
            srt_content += f"{cap['text']}\n\n"
        
        return {"format": "srt", "content": srt_content}
    
    elif format == "vtt":
        # Generate VTT format
        vtt_content = "WEBVTT\n\n"
        for cap in captions:
            vtt_content += f"{format_timestamp_vtt(cap['start'])} --> {format_timestamp_vtt(cap['end'])}\n"
            vtt_content += f"{cap['text']}\n\n"
        
        return {"format": "vtt", "content": vtt_content}

def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def format_timestamp_vtt(seconds: float) -> str:
    """Convert seconds to VTT timestamp format (HH:MM:SS.mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

