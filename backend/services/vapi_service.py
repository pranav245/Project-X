import httpx

from config import get_settings
from prompts.voice_agent import build_voice_system_prompt

VAPI_BASE_URL = "https://api.vapi.ai"


class VAPIService:
    def __init__(self):
        self.settings = get_settings()
        self.headers = {
            "Authorization": f"Bearer {self.settings.VAPI_API_KEY}",
            "Content-Type": "application/json",
        }

    async def create_assistant(
        self,
        brand_name: str,
        persona_name: str = "Sole",
        persona_tone: str = "friendly",
    ) -> dict:
        system_prompt = build_voice_system_prompt(
            brand_name=brand_name,
            persona_name=persona_name,
            persona_tone=persona_tone,
        )

        payload = {
            "name": f"{brand_name} - {persona_name}",
            "model": {
                "provider": self.settings.LLM_PROVIDER,
                "model": self.settings.LLM_MODEL,
                "messages": [{"role": "system", "content": system_prompt}],
            },
            "transcriber": {
                "provider": "custom-transcriber",
                "server": {
                    "url": self.settings.SARVAM_STT_URL,
                    "headers": {"api-subscription-key": self.settings.SARVAM_API_KEY},
                },
            },
            "voice": {
                "provider": "custom-voice",
                "server": {
                    "url": self.settings.SARVAM_TTS_URL,
                    "headers": {"api-subscription-key": self.settings.SARVAM_API_KEY},
                },
            },
            "serverUrl": f"{self.settings.BACKEND_URL}/webhooks/vapi",
            "serverUrlSecret": self.settings.VAPI_WEBHOOK_SECRET,
            "firstMessage": f"Hello! I'm {persona_name}, how can I help you today?",
            "endCallMessage": "Thank you for calling. Have a great day!",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{VAPI_BASE_URL}/assistant",
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()

    async def link_phone_number(self, assistant_id: str, phone_number_id: str) -> dict:
        payload = {
            "assistantId": assistant_id,
            "provider": "telnyx",
        }

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{VAPI_BASE_URL}/phone-number/{phone_number_id}",
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()

    async def update_assistant(self, assistant_id: str, payload: dict) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{VAPI_BASE_URL}/assistant/{assistant_id}",
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()

    async def get_assistant(self, assistant_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{VAPI_BASE_URL}/assistant/{assistant_id}",
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()


vapi_service = VAPIService()
