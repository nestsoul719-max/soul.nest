from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from pymongo import MongoClient
import os

# =======================
# CONFIG
# =======================
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "soulnest_db")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

app = FastAPI(
    title="SoulNest API",
    description="Your safe emotional space 🤍",
    version="1.0"
)

# =======================
# MODELS
# =======================
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    reply: str
    conversation_id: str

class MoodRequest(BaseModel):
    mood: str
    note: Optional[str] = None
    user_id: str = "default_user"

class JournalRequest(BaseModel):
    title: str
    content: str
    user_id: str = "default_user"

# =======================
# ROOT
# =======================
@app.get("/api/")
def root():
    return {"message": "SoulNest API - Your safe emotional space 🤍"}

# =======================
# CHAT API (LLM MOCK – replace later)
# =======================
@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    conversations = db.conversations
    messages = db.messages

    # Create new conversation
    if not req.conversation_id:
        conv = {
            "user_id": req.user_id,
            "created_at": datetime.utcnow()
        }
        conv_id = str(conversations.insert_one(conv).inserted_id)
    else:
        conv_id = req.conversation_id

    # Save user message
    messages.insert_one({
        "conversation_id": conv_id,
        "sender": "user",
        "text": req.message,
        "timestamp": datetime.utcnow()
    })

    # 🤍 Empathetic AI reply (LLM placeholder)
    ai_reply = (
        "Hey 🤍 I hear you. Tum jo feel kar rahe ho wo valid hai. "
        "Thoda sa deep breath lo… main yahin hoon tumhare saath."
    )

    # Save AI message
    messages.insert_one({
        "conversation_id": conv_id,
        "sender": "ai",
        "text": ai_reply,
        "timestamp": datetime.utcnow()
    })

    return ChatResponse(reply=ai_reply, conversation_id=conv_id)

# =======================
# MOOD TRACKING
# =======================
@app.post("/api/mood")
def log_mood(req: MoodRequest):
    moods = db.moods
    mood_doc = {
        "user_id": req.user_id,
        "mood": req.mood,
        "note": req.note,
        "timestamp": datetime.utcnow()
    }
    moods.insert_one(mood_doc)
    return {"status": "Mood saved successfully 💫"}

@app.get("/api/moods")
def get_moods(user_id: str = "default_user"):
    moods = list(db.moods.find({"user_id": user_id}).sort("timestamp", -1))
    for m in moods:
        m["_id"] = str(m["_id"])
    return moods

# =======================
# JOURNAL CRUD
# =======================
@app.post("/api/journal")
def create_journal(req: JournalRequest):
    journals = db.journals
    doc = {
        "user_id": req.user_id,
        "title": req.title,
        "content": req.content,
        "created_at": datetime.utcnow()
    }
    jid = journals.insert_one(doc).inserted_id
    return {"journal_id": str(jid)}

@app.get("/api/journals")
def get_journals(user_id: str = "default_user"):
    journals = list(db.journals.find({"user_id": user_id}))
    for j in journals:
        j["_id"] = str(j["_id"])
    return journals

@app.get("/api/journals/{journal_id}")
def get_journal(journal_id: str):
    journal = db.journals.find_one({"_id": journal_id})
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found")
    journal["_id"] = str(journal["_id"])
    return journal

@app.put("/api/journals/{journal_id}")
def update_journal(journal_id: str, req: JournalRequest):
    result = db.journals.update_one(
        {"_id": journal_id},
        {"$set": {"title": req.title, "content": req.content}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Journal not found")
    return {"status": "Journal updated ✨"}

@app.delete("/api/journals/{journal_id}")
def delete_journal(journal_id: str):
    result = db.journals.delete_one({"_id": journal_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Journal not found")
    return {"status": "Journal deleted 🗑️"}

# =======================
# CONVERSATIONS HISTORY
# =======================
@app.get("/api/conversations")
def get_conversations(user_id: str = "default_user"):
    convs = list(db.conversations.find({"user_id": user_id}))
    for c in convs:
        c["_id"] = str(c["_id"])
    return convs

@app.get("/api/conversations/{conversation_id}/messages")
def get_messages(conversation_id: str):
    msgs = list(db.messages.find({"conversation_id": conversation_id}))
    for m in msgs:
        m["_id"] = str(m["_id"])
    return msgs

