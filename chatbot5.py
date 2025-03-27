from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")

if not groq_api_key:
    raise ValueError("Missing GROQ_API_KEY in .env file!")

# Initialize Flask app
app = Flask(__name__)

# Initialize Chat Model
model = ChatGroq(model="Gemma2-9b-It", groq_api_key=groq_api_key)

# Session storage for long-term memory
store = {}

def get_session_history(user_id: str):
    """Retrieve chat history for a given user."""
    if user_id not in store:
        store[user_id] = ChatMessageHistory()
    return store[user_id]

with_message_history = RunnableWithMessageHistory(model, get_session_history)

# Home Route
@app.route('/', methods=['GET'])
def home():
    """Check if the server is running."""
    return jsonify({"message": "Flask app is running!"})

# Mental Health Chatbot with Long-Term Memory
@app.route('/chat', methods=['POST'])
def chat():
    """Handle chatbot conversations with users."""
    data = request.get_json()
    
    if not data or 'message' not in data or 'user_id' not in data:
        return jsonify({"error": "Message and user_id are required!"}), 400

    user_id = data['user_id']
    message = data['message']
    language = data.get('language', 'English')

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a friendly and professional mental health consultant. Your role is to listen to the user, ask relevant questions, and provide brief, meaningful guidance in {language}.
        
        Keep track of past conversations to offer personalized support.
        
        ### Example Conversations:
        **User**: I'm feeling really anxious lately.
        **Consultant**: I'm sorry to hear that. Can you tell me what's been on your mind?
        
        **User**: I just feel overwhelmed with work.
        **Consultant**: That sounds tough. Have you tried breaking tasks into smaller steps?
        
        Keep your responses concise, engaging, and supportive.
        """),
        MessagesPlaceholder(variable_name="messages")
    ])

    chat_history = get_session_history(user_id)
    chat_history.add_message(HumanMessage(content=message))

    chain = prompt | model
    response = chain.invoke({
        "messages": chat_history.messages,
        "language": language
    })

    chat_history.add_message(response)
    
    return jsonify({"response": response.content})

# Run Flask Server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
