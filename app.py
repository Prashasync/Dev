from fastapi import FastAPI
from services.chat_service import chat_router
from services.emotion_service import emotion_router
from services.recommendation import recommend_router

app = FastAPI(title="Mental Health AI Chatbot")

# ✅ Include all API modules
app.include_router(chat_router, prefix="/chat", tags=["AI Chat"])
app.include_router(emotion_router, prefix="/emotion", tags=["Emotion Analysis"])
app.include_router(recommend_router, prefix="/recommendation", tags=["Doctor Recommendation"])

@app.get("/")
def home():
    return {"message": "Mental Health AI Chatbot API Running ✅"}
