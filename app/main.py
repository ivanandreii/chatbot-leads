from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DATA_FILE = Path("data/leads.json")
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    name: Optional[str] = Field(None, description="User name for booking")
    phone: Optional[str] = Field(None, description="User phone number for booking")
    service: Optional[str] = Field(
        None, description="Requested service for booking (e.g. haircut, consult)"
    )


class Lead(BaseModel):
    name: str
    phone: str
    service: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChatResponse(BaseModel):
    reply: str
    intent: str
    requested_fields: List[str] = Field(default_factory=list)


app = FastAPI(title="Small Business Chatbot")


RESPONSES = {
    "program": "Suntem deschiși de luni până vineri, între 09:00 și 18:00.",
    "locatie": "Ne găsești pe Strada Exemplu nr. 10, București.",
    "servicii": "Oferim: tuns, coafat, manichiură, pedichiură și consultanță de stil.",
    "preturi": "Prețurile încep de la 100 RON pentru tuns și 150 RON pentru coafat. Solicitați detalii pentru servicii specifice.",
}


BOOKING_KEYWORDS = {"programare", "rezervare", "book", "appointment"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    message_lower = payload.message.lower()

    if any(keyword in message_lower for keyword in BOOKING_KEYWORDS):
        return handle_booking(payload)

    for intent, answer in RESPONSES.items():
        if intent in message_lower:
            return ChatResponse(reply=answer, intent=intent)

    # default fallback
    return ChatResponse(
        reply="Nu am înțeles exact. Te pot ajuta cu programul, locația, serviciile sau prețurile noastre.",
        intent="fallback",
    )


def handle_booking(payload: ChatRequest) -> ChatResponse:
    missing_fields = [
        field_name
        for field_name, value in (
            ("nume", payload.name),
            ("telefon", payload.phone),
            ("serviciu dorit", payload.service),
        )
        if not value
    ]

    if missing_fields:
        message = (
            "Hai să setăm programarea. Am nevoie de următoarele informații: "
            + ", ".join(missing_fields)
            + "."
        )
        return ChatResponse(reply=message, intent="booking", requested_fields=missing_fields)

    # Save lead when all fields are present
    lead = Lead(name=payload.name, phone=payload.phone, service=payload.service)
    save_lead(lead)
    return ChatResponse(
        reply=(
            "Mulțumim! Am înregistrat programarea pentru serviciul "
            f"{lead.service} pe numele {lead.name}. Te vom contacta la {lead.phone}."
        ),
        intent="booking",
    )


def save_lead(lead: Lead) -> None:
    leads = load_leads()
    leads.append(lead)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump([lead.model_dump() for lead in leads], f, ensure_ascii=False, indent=2)


def load_leads() -> List[Lead]:
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return [Lead(**item) for item in data]
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Fișierul de lead-uri nu poate fi citit.")


@app.get("/")
def health() -> dict:
    return {"status": "ok"}
