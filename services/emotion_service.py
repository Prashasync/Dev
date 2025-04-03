from fastapi import APIRouter, Depends
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from database.database import get_db,SessionLocal
from model.model import ChatMessage, EmotionAnalysis, Patient
# from config.settings import HF_API_URL, HF_API_KEY
import os
from dotenv import load_dotenv
load_dotenv()

HF_API_URL = os.getenv("HF_API_URL")
HF_API_KEY = os.getenv("HF_API_KEY")
emotion_router = APIRouter()
analyzer = SentimentIntensityAnalyzer()
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

def get_emotion(text):
    response = requests.post(HF_API_URL, headers=HEADERS, json={"inputs": text})
    if response.status_code == 200 and response.json():
        return response.json()[0][0]["label"], round(response.json()[0][0]["score"], 2)
    return "unknown", 0.0

def analyze_emotions():
    db = SessionLocal()
    try:
        patient_ids = db.query(Patient.patient_id).distinct().all()
        for patient_id_tuple in patient_ids:
            patient_id = patient_id_tuple[0]
            messages = db.query(ChatMessage).filter(ChatMessage.sender_id == patient_id).all()
            for msg in messages:
                emotion, confidence = get_emotion(msg.message_text)
                sentiment = round(analyzer.polarity_scores(msg.message_text)["compound"], 2)
                db.add(EmotionAnalysis(emotion_id=str(uuid.uuid4()), chat_message_id=msg.chat_message_id, patient_id=msg.sender_id, emotion_category=emotion, confidence_score=sentiment, analyzed_at=datetime.utcnow()))
            db.commit()
    finally:
        db.close()

# ✅ Run Analysis Daily
scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
scheduler.add_job(analyze_emotions, "cron", hour=0)
scheduler.start()

@emotion_router.get("/run-analysis")
def run_analysis():
    analyze_emotions()
    return {"message": "Emotion analysis completed."}
