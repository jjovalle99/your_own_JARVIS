import os
import tempfile
import wave
from typing import List, Optional

import pyaudio
from loguru import logger
from openai import AsyncOpenAI


async def capture_voice_input(
    client: AsyncOpenAI,
    p: pyaudio.PyAudio,
    timeout: int = 5,
) -> Optional[str]:
    """
    Capture voice input from microphone and transcribe it using OpenAI's Whisper model.

    Args:
        client (AsyncOpenAI): OpenAI client instance for transcription
        p (pyaudio.PyAudio): PyAudio instance for audio recording
        timeout (int, optional): Recording duration in seconds. Defaults to 5.

    Returns:
        Optional[str]: Transcribed text if successful, None if an error occurs

    Raises:
        Exception: Any error during audio capture or transcription
    """
    # Audio recording parameters
    CHUNK: int = 1024
    FORMAT: int = pyaudio.paInt16
    CHANNELS: int = 1
    RATE: int = 44100

    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        temp_filename: str = temp_audio.name

    try:
        # Open stream
        stream: pyaudio.Stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        logger.info("Listening... (speaking for 5 seconds)")

        # Record audio
        frames: List[bytes] = []
        for _ in range(0, int(RATE / CHUNK * timeout)):
            data: bytes = stream.read(CHUNK)
            frames.append(data)

        # Stop recording
        stream.stop_stream()
        stream.close()

        # Save recording
        with wave.open(temp_filename, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))

        # Transcribe
        with open(temp_filename, "rb") as audio_file:
            transcription: str = await client.audio.transcriptions.create(
                model="whisper-1", file=audio_file, response_format="text"
            )

        return transcription

    except Exception as e:
        logger.error("Error capturing voice: {e}", e=e)
        return None

    finally:
        os.unlink(temp_filename)