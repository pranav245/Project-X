import httpx

from config import get_settings


class SarvamService:
    def __init__(self):
        self.settings = get_settings()
        self.headers = {"api-subscription-key": self.settings.SARVAM_API_KEY}

    async def speech_to_text(self, audio_bytes: bytes, language_code: str = "hi-IN") -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.settings.SARVAM_STT_URL,
                headers=self.headers,
                files={"file": ("audio.wav", audio_bytes, "audio/wav")},
                data={"language_code": language_code, "model": "saarika:v2"},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()["transcript"]

    async def text_to_speech(
        self,
        text: str,
        language_code: str = "hi-IN",
        speaker: str | None = None,
    ) -> str:
        payload = {
            "inputs": [text],
            "target_language_code": language_code,
            "speaker": speaker or self.settings.SARVAM_DEFAULT_VOICE,
            "pitch": 0,
            "pace": 1.0,
            "loudness": 1.5,
            "speech_sample_rate": 8000,
            "enable_preprocessing": True,
            "model": "bulbul:v1",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.settings.SARVAM_TTS_URL,
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()["audios"][0]

    async def detect_language(self, text: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.settings.SARVAM_LID_URL,
                headers=self.headers,
                json={"input": text},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()["language_code"]


sarvam_service = SarvamService()
