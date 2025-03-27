from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Patient, Doctor, ChatMessage
from collections import defaultdict
import uuid

recommend_router = APIRouter()

def get_doctor_recommendations(patient_id: str, db: Session):
    """
    Match a patient with the most suitable doctor based on multiple factors.
    """

    # ✅ Fetch Patient Info
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        return {"error": "Patient not found"}

    # ✅ Fetch All Doctors
    doctors = db.query(Doctor).all()

    # ✅ Scoring System
    doctor_scores = defaultdict(int)

    for doctor in doctors:
        if doctor.language == patient.language:
            doctor_scores[doctor.doctor_id] += 3
        if doctor.religion == patient.religion:
            doctor_scores[doctor.doctor_id] += 2
        if doctor.region == patient.region:
            doctor_scores[doctor.doctor_id] += 2

    # ✅ Fetch Patient's Previous Chat History (Keyword Analysis)
    past_messages = db.query(ChatMessage).filter(ChatMessage.sender_id == patient_id).all()
    common_keywords = ["stress", "depression", "anxiety", "relationship", "trauma", "insomnia"]
    
    for message in past_messages:
        for keyword in common_keywords:
            if keyword in message.message_text.lower():
                for doctor in doctors:
                    if keyword in doctor.specialization.lower():
                        doctor_scores[doctor.doctor_id] += 5  # Higher weight for specialization match

    # ✅ Select Top Recommended Doctors
    top_doctors = sorted(doctor_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    
    recommendations = []
    for doctor_id, score in top_doctors:
        doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
        recommendations.append({
            "doctor_id": doctor.doctor_id,
            "specialization": doctor.specialization,
            "language": doctor.language,
            "region": doctor.region,
            "score": score
        })

    return recommendations

@recommend_router.get("/recommend/{patient_id}")
def recommend_doctor(patient_id: str, db: Session = Depends(get_db)):
    """
    API endpoint to recommend the best doctor for a given patient.
    """
    recommendations = get_doctor_recommendations(patient_id, db)
    return {"recommended_doctors": recommendations}
