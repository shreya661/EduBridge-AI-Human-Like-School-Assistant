"""Tests for Voice (STT / TTS) and AI Avatar (Lip-sync Visemes & Streaming)."""

import pytest
import io
from fastapi.testclient import TestClient

from app.main import app
from app.voice.stt import stt_provider
from app.voice.tts import tts_provider
from app.avatar.provider import avatar_provider
from app.i18n.language_router import SupportedLanguage
from app.domain.seed_data import seed_school_data

client = TestClient(app)
seed_school_data()


def test_stt_transcription_provider():
    """Verify STT provider transcribes audio bytes with metadata."""
    sample_wav = b"RIFF____WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data____" + (b"\x00" * 3200)
    result = stt_provider.transcribe_audio(sample_wav)
    assert result.text != ""
    assert result.confidence > 0.9
    assert result.language == SupportedLanguage.ENGLISH


def test_tts_synthesis_provider():
    """Verify TTS provider generates base64 audio and valid duration."""
    res = tts_provider.synthesize_speech("Hello, welcome to XYZ AI school assistant.", SupportedLanguage.ENGLISH)
    assert res.audio_base64 != ""
    assert res.duration_seconds > 0.5
    assert res.sample_rate == 24000


def test_avatar_viseme_generation():
    """Verify avatar provider produces sequential viseme cues with closing rest."""
    cues = avatar_provider.generate_visemes("Good morning class 10", 3.0)
    assert len(cues) >= 4
    assert cues[0].start_ms == 0
    assert cues[-1].viseme == "X"  # Closing rest shape


def test_voice_endpoints_authenticated():
    """Verify HTTP endpoints for voice transcription & speech synthesis."""
    login_res = client.post("/api/v1/auth/login", json={"user_id": "S001"})
    assert login_res.status_code == 200
    cookies = login_res.cookies

    # 1. Voice Synthesis
    synth_res = client.post(
        "/api/v1/voice/synthesize",
        json={"text": "Your attendance is 92%", "language": "en"},
        cookies=cookies
    )
    assert synth_res.status_code == 200
    synth_data = synth_res.json()
    assert "audio_base64" in synth_data
    assert synth_data["language"] == "en"

    # 2. Voice Transcription
    fake_audio_file = io.BytesIO(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
    transcribe_res = client.post(
        "/api/v1/voice/transcribe",
        files={"file": ("sample.wav", fake_audio_file, "audio/wav")},
        cookies=cookies
    )
    assert transcribe_res.status_code == 200
    transcribe_data = transcribe_res.json()
    assert "text" in transcribe_data


def test_avatar_endpoints_authenticated():
    """Verify HTTP endpoints for avatar session creation and live rendering."""
    login_res = client.post("/api/v1/auth/login", json={"user_id": "T001"})
    assert login_res.status_code == 200
    cookies = login_res.cookies

    # 1. Start Session
    sess_res = client.post("/api/v1/avatar/session", json={"avatar_id": "teacher_avatar"}, cookies=cookies)
    assert sess_res.status_code == 200
    sess_data = sess_res.json()
    assert sess_data["session_id"].startswith("avs-")
    assert sess_data["status"] == "active"

    # 2. Speak with lip-sync
    speak_res = client.post(
        "/api/v1/avatar/speak",
        json={"session_id": sess_data["session_id"], "text": "Class 10 roster loaded", "language": "en"},
        cookies=cookies
    )
    assert speak_res.status_code == 200
    speak_data = speak_res.json()
    assert len(speak_data["viseme_cues"]) > 0
    assert speak_data["video_stream_url"] is not None
