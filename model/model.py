import uuid
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, String, Integer, Boolean, ForeignKey, Text, Date, Time, Enum, DateTime, Float, DECIMAL, Index
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import enum

# Database Connection
DATABASE_URL = "postgresql://postgres:Prashaind2025@database-1.cyvysmg4w1i4.us-east-1.rds.amazonaws.com:5432/prasha_health"

# Create Database Engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base Model
Base = declarative_base()

# Enum for Gender
class GenderEnum(str, enum.Enum):
    male = "Male"
    female = "Female"
    other = "Other"

# ✅ Users Table (General: Patients & Doctors)
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    roles = Column(String, nullable=False)  # "patient" or "doctor"
    is_active = Column(Boolean, default=True)

    # Relationships
    patients = relationship("Patient", back_populates="user", cascade="all, delete-orphan")
    doctors = relationship("Doctor", back_populates="user", cascade="all, delete-orphan")

# ✅ Patients Table
class Patient(Base):
    __tablename__ = "patients"
    
    patient_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    dob = Column(Date, nullable=False)
    language = Column(String)
    religion = Column(String)
    region = Column(String)
    health_score = Column(Integer)

    # Relationships
    user = relationship("User", back_populates="patients")
    emotion_insights = relationship("UserEmotionInsights", back_populates="patient", cascade="all, delete-orphan")

# ✅ Doctors Table
class Doctor(Base):
    __tablename__ = "doctors"
    
    doctor_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    specialization = Column(String, nullable=False)
    consultation_fee = Column(Integer, nullable=False)
    language = Column(String)
    religion = Column(String)
    region = Column(String)

    # Relationships
    user = relationship("User", back_populates="doctors")

# ✅ Doctor Availability (Renamed to `doctor_schedules`)
class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"
    
    schedule_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    doctor_id = Column(String, ForeignKey("doctors.doctor_id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

# ✅ Appointments Table
class Appointment(Base):
    __tablename__ = "appointments"
    
    appointment_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(String, ForeignKey("doctors.doctor_id", ondelete="CASCADE"), nullable=False)
    appointment_date = Column(Date, nullable=False, index=True)
    appointment_time = Column(Time, nullable=False)
    status = Column(String, default="Scheduled")

# ✅ Ratings & Reviews Table
class Rating(Base):
    __tablename__ = "ratings"
    
    rating_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(String, ForeignKey("doctors.doctor_id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)  # Range: 1-5
    review = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_rating", "doctor_id", "rating"),  # Faster doctor rating retrieval
    )

# ✅ Chat Messages Table
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    chat_message_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = Column(String, nullable=False)
    receiver_id = Column(String, nullable=False)
    message_text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# ✅ Diary Entries Table
class DiaryEntry(Base):
    __tablename__ = "diary_entries"
    
    event_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)
    notes = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ✅ Emotion Analysis Table
class EmotionAnalysis(Base):
    __tablename__ = "emotion_analysis"
    
    emotion_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_message_id = Column(String, ForeignKey("chat_messages.chat_message_id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(String, ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)
    emotion_category = Column(String, nullable=False)  # e.g., "stress", "happiness", "anxiety"
    confidence_score = Column(DECIMAL(5, 2), nullable=False)  # Higher precision for confidence score
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    chat_message = relationship("ChatMessage", back_populates="emotion_analysis")

# ✅ User Emotion Insights Table
class UserEmotionInsights(Base):
    __tablename__ = "user_emotion_insights"

    insight_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, default=datetime.utcnow, index=True)
    dominant_emotion = Column(String, nullable=False)  # Most frequent emotion in a period
    emotion_trend = Column(String)  # Increasing stress, stable happiness, etc.
    major_shifts = Column(String)  # Sudden emotion spikes

    # Relationships
    patient = relationship("Patient", back_populates="emotion_insights")

# Define Relationships
ChatMessage.emotion_analysis = relationship("EmotionAnalysis", back_populates="chat_message", cascade="all, delete-orphan")

# Create Tables
# Base.metadata.create_all(bind=engine)
