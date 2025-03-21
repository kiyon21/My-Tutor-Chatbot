from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime
from query_data import query_rag
from ingest_data import ingest_documents

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

class ChatMessage(BaseModel):
    role: str
    content: str

class Chat(BaseModel):
    id: str
    title: str
    messages: List[ChatMessage]
    created_at: str

@app.post("/api/chat")
async def chat(message: ChatMessage):
    try:
        response = query_rag(message.content)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save the uploaded file
        file_path = f"data/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the document
        ingest_documents([file_path])
        
        return {"message": "File uploaded and processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chats")
async def get_chats():
    try:
        if os.path.exists("data/chats.json"):
            with open("data/chats.json", "r") as f:
                return json.load(f)
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chats")
async def save_chat(chat: Chat):
    try:
        chats = []
        if os.path.exists("data/chats.json"):
            with open("data/chats.json", "r") as f:
                chats = json.load(f)
        
        chats.append(chat.dict())
        
        with open("data/chats.json", "w") as f:
            json.dump(chats, f)
        
        return {"message": "Chat saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 