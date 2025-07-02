# main.py
import os
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from agent.setup_agent import setup_agent, query_llm
from utils.location import get_current_location
from metadata.store import save_message

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize once
agent_executor, _ = setup_agent(verbose=False)

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    session_id = str(uuid.uuid4())
    save_message(session_id, "system", "WebSocket session started")
    try:
        while True:
            text = await ws.receive_text()
            save_message(session_id, "user", text)

            # auto-detect location if requested
            if "use my location" in text.lower():
                loc = get_current_location()
                if loc["city"]:
                    text = f"{text}\n(city: {loc['city']}, country: {loc['country']})"

            reply = query_llm(agent_executor, text)
            save_message(session_id, "assistant", reply)
            await ws.send_text(reply)
    except WebSocketDisconnect:
        save_message(session_id, "system", "WebSocket disconnected")
