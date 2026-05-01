import hashlib
import hmac
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database import get_db
from models.brand import Brand
from models.conversation import Conversation

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks/vapi", tags=["vapi-webhooks"])


def validate_vapi_signature(body: bytes, signature: str | None, secret: str) -> bool:
    if not signature or not secret:
        return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


class CallStartedPayload(BaseModel):
    call_id: str | None = None
    assistant_id: str | None = None
    customer_number: str | None = None
    phone_number: str | None = None


class CallEndedPayload(BaseModel):
    call_id: str | None = None
    assistant_id: str | None = None
    customer_number: str | None = None
    duration_seconds: float | None = None
    transcript: str | None = None
    summary: str | None = None


@router.post("/call-started")
async def call_started(request: Request, db: AsyncSession = Depends(get_db)):
    settings = get_settings()
    body = await request.body()
    signature = request.headers.get("x-vapi-signature")

    if settings.VAPI_WEBHOOK_SECRET and not validate_vapi_signature(
        body, signature, settings.VAPI_WEBHOOK_SECRET
    ):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    data = await request.json()
    message = data.get("message", {})
    call = message.get("call", {})

    call_id = call.get("id")
    assistant_id = call.get("assistantId")
    customer_number = call.get("customer", {}).get("number", "unknown")

    brand = None
    if assistant_id:
        result = await db.execute(
            select(Brand).where(Brand.vapi_assistant_id == assistant_id)
        )
        brand = result.scalar_one_or_none()

    conversation = Conversation(
        brand_id=brand.id if brand else None,
        channel="voice",
        customer_phone=customer_number,
        status="active",
        vapi_call_id=call_id,
    )
    db.add(conversation)
    await db.flush()

    logger.info(f"Call started: {call_id} from {customer_number}")
    return {"status": "ok", "conversation_id": str(conversation.id)}


@router.post("/call-ended")
async def call_ended(request: Request, db: AsyncSession = Depends(get_db)):
    settings = get_settings()
    body = await request.body()
    signature = request.headers.get("x-vapi-signature")

    if settings.VAPI_WEBHOOK_SECRET and not validate_vapi_signature(
        body, signature, settings.VAPI_WEBHOOK_SECRET
    ):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    data = await request.json()
    message = data.get("message", {})
    call = message.get("call", {})

    call_id = call.get("id")
    duration = call.get("duration")

    if call_id:
        result = await db.execute(
            select(Conversation).where(Conversation.vapi_call_id == call_id)
        )
        conversation = result.scalar_one_or_none()

        if conversation:
            conversation.status = "resolved"
            conversation.resolved_by = "ai"
            conversation.duration_seconds = int(duration) if duration else None
            conversation.updated_at = datetime.now(timezone.utc)
            logger.info(f"Call ended: {call_id}, duration: {duration}s")
        else:
            logger.warning(f"Call ended but no conversation found for call_id: {call_id}")
    else:
        logger.warning("Call ended webhook received without call_id")

    return {"status": "ok"}
