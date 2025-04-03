from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from openai import OpenAI
import uuid
from datetime import datetime
from database.database import get_db
from models.models import ChatMessage

import os
from dotenv import load_dotenv
load_dotenv()

chat_router = APIRouter()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ OpenAI API Setup
openai = OpenAI(api_key=OPENAI_API_KEY)

@chat_router.websocket("/ws/{patient_id}")
async def chat_with_ai(websocket: WebSocket, patient_id: str, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            user_input = await websocket.receive_text()
            if not user_input.strip():
                await websocket.send_text("❌ Please enter a message.")
                continue

            # ✅ Fetch Last 10 Messages from Database
            chat_history = db.query(ChatMessage).filter(
                (ChatMessage.sender_id == patient_id) | (ChatMessage.receiver_id == patient_id)
            ).order_by(ChatMessage.timestamp.desc()).limit(10).all()

            conversation_history = [
                {"role": "user" if msg.sender_id == patient_id else "assistant", "content": msg.message_text}
                for msg in reversed(chat_history)
            ]
            conversation_history.append({"role": "user", "content": user_input})

            # ✅ Save User Message
            db.add(ChatMessage(chat_message_id=str(uuid.uuid4()), sender_id=patient_id, receiver_id="AI_Doctor", message_text=user_input, timestamp=datetime.utcnow()))
            db.commit()

            # ✅ AI Response
            # This code snippet is using the OpenAI API to generate a response from a chatbot model.
            # Here's a breakdown of what's happening:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are a mental health assistant."}] + conversation_history,
                temperature=0.1,
                max_tokens=80,
            )
            ai_response = response.choices[0].message.content.strip()

            # ✅ Save AI Response
            db.add(ChatMessage(chat_message_id=str(uuid.uuid4()), sender_id="AI_Doctor", receiver_id=patient_id, message_text=ai_response, timestamp=datetime.utcnow()))
            db.commit()

            await websocket.send_text(ai_response)

    except WebSocketDisconnect:
        print(f"Patient {patient_id} disconnected.")
